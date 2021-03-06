"""Miscellaneous helpers live here"""
from collections.abc import MutableMapping
from copy import deepcopy
from pathlib import Path
from dynaconf import settings
import yaml


def merge_dicts(dict1, dict2):
    """Merge two nested dicitonaries together"""
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict1
    merged = {}
    dupe_keys = dict1.keys() & dict2.keys()
    for key in dupe_keys:
        merged[key] = merge_dicts(dict1[key], dict2[key])
    for key in dict1.keys() - dupe_keys:
        merged[key] = deepcopy(dict1[key])
    for key in dict2.keys() - dupe_keys:
        merged[key] = deepcopy(dict2[key])
    return merged


def flatten_dict(nested_dict, parent_key=""):
    """flatten a nested dictionary, keeping nested notation in key
    {
        'key': 'value1',
        'another': {
            'nested': 'value2',
            'nested2': [1, 2, {'deep': 'value3'}]
        }
    }
    becomes
    {
        "key": "value",
        "another_nested": "value2",
        "another_nested2": [1, 2],
        "another_nested2_deep": "value3"
    }
    note that dictionaries nested in lists will be removed from the list
    """

    flattened = []
    for key, value in nested_dict.items():
        new_key = f"{parent_key}_{key}" if parent_key else key
        if isinstance(value, dict):
            flattened.extend(flatten_dict(value, new_key).items())
        elif isinstance(value, list):
            to_remove = []
            value = value.copy()  # avoid mutating nested structures
            for index, val in enumerate(value):
                if isinstance(val, dict):
                    flattened.extend(flatten_dict(val, new_key).items())
                    to_remove.append(index)
            for index in to_remove:
                del value[index]
            flattened.append((new_key, value))
        else:
            flattened.append((new_key, value))
    return dict(flattened)


def resolve_nick(nick):
    """check if the nick exists and if so, return the arguments"""
    nick_names = settings.get("NICKS", {})
    if nick in nick_names:
        return settings.NICKS[nick].to_dict()


def load_inventory():
    inventory_file = Path(settings.INVENTORY_FILE)
    if not inventory_file.exists():
        inv_data = []
    else:
        with inventory_file.open() as inv:
            inv_data = yaml.load(inv, Loader=yaml.FullLoader) or []
    return inv_data


def update_inventory(new_hosts, replace_all=False):
    inventory_file = Path(settings.INVENTORY_FILE)
    if not inventory_file.exists():
        inv_data = []
    else:
        with inventory_file.open() as inv:
            inv_data = yaml.load(inv, Loader=yaml.FullLoader) or []
        inventory_file.unlink()
    if replace_all:
        inv_data = new_hosts
    else:
        inv_data.extend(new_hosts)
    inventory_file.touch()
    with inventory_file.open("w") as inv:
        yaml.dump(inv_data, inv)
