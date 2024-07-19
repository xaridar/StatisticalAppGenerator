import sys
import pandas as pd
import os
import importlib.util
import re

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
            if re.match('^-?\\d*.?\\d+?$', args[i]):
                # number
                obj[word[1:]] = float(args[i])
            else:
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
output_string = args[3]
id = args[4]

if len(args) > 5:
    as_obj = convert_to_obj(args[5:])
else:
    as_obj = {}
if id != 'noid':
    as_obj['files'] = {}

    file_names = [file for file in os.listdir('temp') if file.endswith(f'_{id}.csv')]
    for file in file_names:
        with open(os.path.join('temp', file)) as f:
            csv = pd.read_csv(f)
            name = file.rsplit('_')[0]
            as_obj['files'][name] = csv

method = load_as_module(filename).__getattribute__(method_name)
out_obj = method(**as_obj)

# format output
output_format = {name.split(':')[0]: name.split(':')[1] for name in output_string.split(',')}
output = {}
for key, value in out_obj.items():
    output[key] = {}
    output[key]['type'] = output_format[key].split('(')[0]
    if output[key]['type'] == 'graph':
        x_var = output_format[key][6:-1].split('/')[0]
        y_var = output_format[key][6:-1].split('/')[1]
        output[key]['labels'] = list(value[x_var])
        output[key]['values'] = list(value[y_var])
    elif output_format[key] == 'table':
        output[key]['table'] = value

print(output)