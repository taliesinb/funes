import opcode
import dis
import weakref
import types

from funes.logging import logging

# this will store hashes and global lists for functions / values,
# without preventing them from being GC'd
code_object_global_names_cache = weakref.WeakKeyDictionary()


STORE_GLOBAL = opcode.opmap['STORE_GLOBAL']
DELETE_GLOBAL = opcode.opmap['DELETE_GLOBAL']
LOAD_GLOBAL = opcode.opmap['LOAD_GLOBAL']
GLOBAL_OPS = (STORE_GLOBAL, DELETE_GLOBAL, LOAD_GLOBAL)


# adapted from https://web.archive.org/web/20140626004012/http://www.picloud.com
def get_code_object_global_names(code_object):
    global code_object_global_names_cache
    out_names = code_object_global_names_cache.get(code_object)
    if out_names:
        return out_names
    try:
        names = code_object.co_names
    except AttributeError:
        out_names = set()
    else:
        out_names = set()
        for instr in dis.get_instructions(code_object):
            op = instr.opcode
            if op in GLOBAL_OPS:
                out_names.add(names[instr.arg])
        # see if nested function have any global refs
        if code_object.co_consts:
            for const in code_object.co_consts:
                if type(const) is types.CodeType:
                    out_names |= set(get_code_object_global_names(const))
    out_names = sorted(out_names)
    code_object_global_names_cache[code_object] = out_names
    return out_names


# this generates the digests of all the globals that a function
# depends on
def hash_code_object_dependencies(fn, hasher, module_scope):
    from funes.hashing import hash_digest
    code_object = fn.__code__
    global_dict = fn.__globals__
    if module_scope and fn.__module__ != module_scope:
        if logging:
            print (f"skipping dependencies out-of-scope function {fn.__name__}")
        return
    for var in get_code_object_global_names(code_object):
        if var in sorted(global_dict.keys()):
            val = global_dict[var]
            digest = hash_digest(val, module_scope)
            if logging:
                print(f'{fn.__name__} depends on {var} which has digest {digest}')
            hasher.update(digest)


# we don't want our hashing of functions to depend on unstable properties of the
# co, like the filename, first line, source map, etc.
def get_stable_code_object_fields(co):
    return (co.co_argcount,
            co.co_nlocals,
            co.co_flags & ~1,   # null out the 'optimized' flag
            co.co_stacksize,
            co.co_names,
            co.co_varnames,
            co.co_code,
            co.co_consts)
