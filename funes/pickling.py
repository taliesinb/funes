import dill

def unpickle(path):
    with open(path, 'rb') as file:
        return dill.load(file)

def pickle(path, value):
    with open(path, 'wb') as file:
        dill.dump(value, file)

def pickle_string(obj):
    return dill.dumps(obj)

