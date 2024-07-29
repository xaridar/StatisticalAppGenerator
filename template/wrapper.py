import sys
import pandas as pd
import os
import importlib.util
import warnings
import math

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
        elif word.startswith('-""'):
            # string
            i += 1
            obj[word[3:]] = args[i]
        elif word.startswith('-[""]'):
            # string array
            i += 1
            if (args[i] == ''):
                obj[word[5:]] = []
            else:
                obj[word[5:]] = args[i].split(', ')
        elif word.startswith('-[]'):
            # number array
            i += 1
            obj[word[3:]] = [float(elem) for elem in args[i].split(', ')]
        else:
            # number
            i += 1
            if (args[i] == ''):
                obj[word[1:]] = []
            else:
                obj[word[1:]] = float(args[i])
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
    file_names = [file for file in os.listdir('temp') if file.endswith(f'_{id}.csv')]
    for file in file_names:
        with open(os.path.join('temp', file)) as f:
            csv = pd.read_csv(f)
            name = file.rsplit('_')[0]
            as_obj[name] = csv

method = load_as_module(filename).__getattribute__(method_name)
warnings.filterwarnings("ignore")
out_obj = method(**as_obj)
warnings.filterwarnings("default")

# format output
output_format = {name.split(':')[0]: name.split(':')[1] for name in output_string.split(',')}
output = {}
for key, value in out_obj.items():
    output[key] = {}
    if key not in output_format:
        continue
    arg_type = output_format[key].split('(')[0]
    output[key]['type'] = arg_type
    if arg_type == 'graph':
        x_var = output_format[key][6:-1].split('/')[0]
        y_var = output_format[key][6:-1].split('/')[1]
        output[key]['labels'] = ['Infinity' if data == math.inf else '-Infinity' if data == -math.inf else data for data in list(value[x_var])]
        output[key]['values'] = ['Infinity' if data == math.inf else '-Infinity' if data == -math.inf else data for data in list(value[y_var])]
    elif arg_type == 'table':
        d = {'columns': ['Param', 'Value']}
        try:
            precision = [int(prec) for prec in output_format[key][6:-1].split('|')]
            if len(precision) != 1 and len(precision) != 2:
                print({'error': "Table precision should either be \\'any\\', a single int between 0 and 6, or an array with 1 int for each resulting column."})
                sys.exit(0)
            if len(precision) == 1:
                precision *= 2
            d['data'] = [[data if isinstance(data, str) else 'Infinity' if data == math.inf else '-Infinity' if data == -math.inf else '{num:.{prec}f}'.format(num=data, prec=precision[i]) for i, data in enumerate([ele, value[ele]])] for ele in value]
        except ValueError:
            d['data'] = [[str(data) for data in [ele, value[ele]]] for ele in value]
        output[key]['table'] = d
    elif arg_type == 'text':
        output[key]['text'] = str(value)
    elif arg_type == 'data_table':
        table = value.to_dict(orient='split', index=False)
        try:
            precision = [int(prec) for prec in output_format[key][11:-1].split('|')]
            if len(precision) != 1 and len(precision) != len(table['columns']):
                print({'error': "Table precision should either be \\'any\\', a single int between 0 and 6, or an array with 1 int for each resulting column."})
                sys.exit(0)
            if len(precision) == 1:
                precision *= len(table['columns'])
            table['data'] = [[data if isinstance(data, str) else 'Infinity' if data == math.inf else '-Infinity' if data == -math.inf else '{num:.{prec}f}'.format(num=data, prec=precision[i]) for i, data in enumerate(row)] for row in table['data']]
        except ValueError:
            table['data'] = [[str(data) for data in row] for row in table['data']]
        table['columns'] = [str(el) for el in table['columns']]
        output[key]['type'] = 'table'
        output[key]['table'] = table

print(output)