import sys
import pandas as pd
import os
import importlib.util

def convert_to_obj(args):
    obj = {}
    i = 0
    while len(args) > i:
        word = args[i]
        if word.startswith('--'):
            # true
            obj[word[2:]] = True
        elif word.startswith('-!'):
            # false
            obj[word[2:]] = False
        else:
            i += 1
            # string
            obj[word[1:]] = args[i]
        i += 1
    return obj

def load_as_module(source):
    mod_name = ""
    spec = importlib.util.spec_from_file_location(mod_name, source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module

args = sys.argv
filename = args[1]
method_name = args[2]
id = args[3]

as_obj = convert_to_obj(args[4:])
as_obj['files'] = {}

file_names = [file for file in os.listdir('temp') if file.endswith(f'_{id}.csv')]
for file in file_names:
    with open(os.path.join('temp', file)) as f:
        csv = pd.read_csv(f)
        name = file.rsplit('_')[0]
        as_obj['files'][name] = csv

method = load_as_module(filename).__getattribute__(method_name)
print(method(as_obj))