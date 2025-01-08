import logging
import json

logger = logging.getLogger(__name__)


class AlreadyExists(Exception):
    """Base class for exceptions in this module."""
    pass


def array_set(arr, key, value, overwrite=True):
    # Set the value of a multidimensional array element using dot notation
    # print 'SET {}={}'.format(key, value)
    if key == 'type':
        self.set_type(value)
        return
    origkey = key
    key = key.split('.')
    while len(key) != 0:
        k = key.pop(0)
        if k not in arr:
            arr[k] = {}
        if len(key) == 0:
            if arr[k] != {} and not overwrite:
                raise AlreadyExists('Could not set {}="{}" because another value already exists: "{}"'.format(origkey, str(value), str(arr)))
            arr[k] = value
        arr = arr[k]

def array_add(arr, key, value):
    # Add a value to a multidimensional array element using dot notation
    key = key.split('.')
    while len(key) != 0:
        k = key.pop(0)
        if k not in arr:
            arr[k] = [] if len(key) == 0 else {}
        if len(key) == 0:
            arr[k].append(value)
        arr = arr[k]

def array_get(arr, key, default=None):
    # Get the value of a multidimensional array element using dot notation
    key = key.split('.')
    while len(key) > 1:
        k = key.pop(0)
        if k not in arr:
            return default
        arr = arr[k]
    return arr.get(key[0], default)
