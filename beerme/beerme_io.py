import os
import json
import pickle
import beerme.constants as const


def load_rawdata(path=const.DBPATH):
    return read_pickle(path)


def read_json(path):
    if os.path.isfile(path):
        with open(path, 'r') as fidr:
            return json.load(fidr)
    else:
        return None


def read_pickle(path):
    p = None
    if os.path.isfile(path):
        with open(path, 'rb') as fidr:
            p = pickle.load(fidr)
    return p


def write_json(path, data, indent=2):
    with open(path, 'w') as fidw:
        json.dump(data, fidw, indent=indent)
    return True


def write_pickle(path, data):
    with open(path, 'wb') as fidw:
        pickle.dump(data, fidw, protocol=pickle.HIGHEST_PROTOCOL)
    return True
