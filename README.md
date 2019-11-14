# Funes

Funes lets you decorate functions in such a way that their computations are memorized permanently to disk.

It is named after the Borges short story [Funes the Memories](https://en.wikipedia.org/wiki/Funes_the_Memorious).

## Background

This package allows the results of expensive functions be cached to disk, by decorating these functions with the `@memorious` decorator. When that function is called again on an identical input, the cached result will be loaded from disk and returned. 

This is achieved by pickling the result and input and writing it to disk, using a unique path that identifies the particular version of the function that is being cached (based on a hash that depends on its definition, thanks to the 'dill' package), as well as a key that depends on the hashed arguments of the function.

Memorious functions should not contain (possibly mutually) recursive definitions, or the stack will overflow. Their hash values WILL change if functions that depend on are changed, but these dependencies are only followed if they remain within the current module. 

The pickled results will be cached under cache/funcname/hexhash/arg_hash.dill. These files can be deleted manually to clear the cache, or transported between computers.

Each pickled computation contains a dictionary with the following keys:
`input`: ordered dict of function arguments + their provided (or defaulting) values  
`output`: whatever the function produced
`time`: time in seconds the function took to run

A special `global_seed` keyword argument can be provided to any memorious function to set the global random seed prior to running the function. This allows controlled stochasticity to be used, while maintaining the benefits of caching. 

## Examples

The following script demonstrates the basic idea behind funes:

```
from funes import memorious, load_cached_results
from time import sleep

@memorious
def double(x):
    print('doubling', x)
    sleep(0.5)
    return x * 2

print("uncached (will be slow)")
for i in range(5):
    double(i)

print("cached (will be fast)")
for i in range(5):
    double(i)

print("uncached (will be slow, unique global seed)")
for seed in range(5):
    double(0, global_seed=seed)

print("cached (will be fast, reuse global seed)")
for seed in range(5):
    double(0, global_seed=seed)

print("all cached values")
print(list(load_cached_results(double)))
```