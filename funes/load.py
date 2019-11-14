import glob

from funes.pickling import unpickle


def load_cached_results(fn):
    cache_path = fn.__cache_path__
    for file_path in glob.glob(cache_path + '*'):
        res = unpickle(file_path)
        yield res


def load_cached_results_as_pandas(fn, exclude=None, index=None):
    import glob, pandas
    cache_path = fn.__cache_path__
    records = []
    for file_path in glob.glob(cache_path + '*'):
        res = unpickle(file_path)
        inputs = res['input']
        outputs = res['output']
        if not isinstance(outputs, dict):
            outputs = {'output': outputs}
        record = inputs
        record.update(outputs)
        record['timing'] = res['timing']
        records.append(record)
    return pandas.DataFrame.from_records(records, exclude=exclude, index=index)
