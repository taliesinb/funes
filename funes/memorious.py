import os.path
import time
import functools
import sys

from funes.pickling import pickle, unpickle
from funes.hashing import hash_hexdigest
from funes.logging import logging


# this simulates the way that python will resolve positional and named arguments, yielding
# a single ordered dict that contains the names of arguments and their values
def normalize_args(fn_name, args, kwargs, arg_names, defaults):
    result = {}
    for key in kwargs.keys():
        if key not in arg_names:
            if key == 'global_seed':
                result['global_seed'] = kwargs[key]
            else:
                raise RuntimeError(f"{fn_name}: unknown key {key} provided")
    if len(args) > len(arg_names):
        raise RuntimeError(f"{fn_name}: excess arguments provided {len(args)} > {len(arg_names)}")
    for i, name in enumerate(arg_names):
        if i < len(args):
            result[name] = args[i]
        elif name in kwargs:
            result[name] = kwargs[name]
        elif name in defaults:
            result[name] = defaults[name]
        else:
            raise RuntimeError(f"{fn_name}: value for argument {i} ('{name}') not specified")
    return result


def apply_global_seed(seed):
    import random
    random.seed(seed)
    if 'numpy' in sys.modules:
        import numpy
        numpy.random.seed(seed)
    if 'torch' in sys.modules:
        import torch
        torch.manual_seed


# this is the decorator that turns a function into a disk-memoizing version
def memorious(fn):

    fn.__cache_path__ = 'cache/' + fn.__name__ + '/' + hash_hexdigest(fn) + '/'
    fn.__arg_names__ = fn.__code__.co_varnames[:fn.__code__.co_argcount]
    defaults = fn.__defaults__ or []
    fn.__kwdefaults__ = dict(zip(fn.__arg_names__[-len(defaults):], defaults))

    if not os.path.exists(fn.__cache_path__):
        os.makedirs(fn.__cache_path__)

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        input_dict = normalize_args(fn.__name__, args, kwargs, fn.__arg_names__, fn.__kwdefaults__)
        if logging:
            print(f"Input: {input_dict}")
        output_path = fn.__cache_path__ + hash_hexdigest(input_dict, cache_hash=False)
        if os.path.exists(output_path):
            res = unpickle(output_path)
            return res['output']
        start = time.time()
        #
        if 'global_seed' in kwargs:
            apply_global_seed(kwargs['global_seed'])
            del kwargs['global_seed']
        output = fn(*args, **kwargs)
        end = time.time()
        output_dict = {'input': input_dict, 'output': output, 'timing': end - start}
        if logging:
            print(f"Output: {output_dict}")
        pickle(output_path, output_dict)
        return output

    return wrapper