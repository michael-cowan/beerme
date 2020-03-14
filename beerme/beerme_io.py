import os
import json
import pickle


def read_json(path):
    if os.path.isfile(path):
        with open(path, 'r') as fidr:
            return json.load(fidr)
    else:
        return None


def read_pickle(path):
    if os.path.isfile(path):
        with open(path, 'rb') as fidr:
            return pickle.load(fidr)
    else:
        return None


def write_json(path, data, indent=2):
    with open(path, 'w') as fidw:
        json.dump(data, fidw, indent=indent)


def write_pickle(path, data):
    with open(path, 'wb') as fidw:
        pickle.dump(data, fidw, protocol=pickle.HIGHEST_PROTOCOL)
    return True
