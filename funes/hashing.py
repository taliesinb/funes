import hashlib
import weakref

from funes.pickling import pickle_string
from funes.logging import logging
from funes.co_tools import get_stable_code_object_fields, hash_code_object_dependencies


stable_hash_cache = weakref.WeakKeyDictionary()


# this hashes a value, using dill. if that value is a function, we special case
# the hashing to 1) be stable 2) include the hashes of those functions it depends on
def hash_digest(x, module_scope=None, hasher=None, cache_hash=True):
    global stable_hash_cache
    if cache_hash and x in stable_hash_cache:
        return stable_hash_cache.get(x)
    is_func = hasattr(x, '__code__')
    if hasher is None:
        hasher = hashlib.new('md5')
    if is_func:
        dump = pickle_string(get_stable_code_object_fields(x.__code__))
    else:
        dump = pickle_string(x)
    hasher.update(dump)
    if logging:
        print(f"base hash for {x}: {hasher.hexdigest()}")
    if is_func:
        hash_code_object_dependencies(x, hasher, module_scope or x.__module__)
    digest = hasher.digest()
    if cache_hash:
    	try:
        	stable_hash_cache[x] = digest
    	except TypeError:
        	pass
    return digest


def hash_hexdigest(x, module_scope=None, cache_hash=True):
    hasher = hashlib.new('md5')
    hash_digest(x, module_scope=module_scope, hasher=hasher, cache_hash=cache_hash)
    return hasher.hexdigest()
