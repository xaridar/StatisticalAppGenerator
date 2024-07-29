import time
from flask import Flask, render_template, redirect, request, jsonify
import pandas as pd
from dotenv import load_dotenv
import json
import os
import subprocess
import re
import math

load_dotenv('.env')

app = Flask(__name__)

@app.route('/index')
def alias():
    return redirect('/')

@app.get('/')
def home():
    return render_template('index.html')

@app.post('/')
def upload():
    id = time.time() * 1000
    filepaths = []
    args = []

    # check files
    for name in request.files:
        if (not os.getenv(f'XVAR_{name}')):
            return jsonify(success=False, error=f"Unexpected file: '{name}'")
        file = request.files[name]
        if file.filename == '':
            continue
        if file.content_type != 'text/csv':
            return jsonify(success=False, error=f'Bad filetype (should be CSV): {file.filename}')
        csv = pd.read_csv(file.stream)
        if os.getenv(f'XVAR_{name}') not in csv.columns or os.getenv(f'YVAR_{name}') not in csv.columns:
            return jsonify(success=False, error=f'Missing column(s) in {file.filename}; should have {os.getenv(f'XVAR_{name}')} and {os.getenv(f'YVAR_{name}')}')
        filename = f'{name}_{id}.csv'
        file.stream.seek(0)
        file.save(os.path.join('temp', filename))
        filepaths.append(os.path.join('temp', filename))

    # check options
    opt_def = json.loads(os.getenv('OPTIONS'))
    missing_req = [option['name'] not in request.form for option in opt_def if not option['optional']]
    arrs = [x and [option for option in opt_def if not option['optional']][i]['type'] == 'array' for i, x in enumerate(missing_req)]
    for i, x in enumerate(arrs):
        if not x:
            continue
        missing_req[i] = False
    arr_names = [[option for option in opt_def if not option['optional']][i]['name'] for i, x in enumerate(arrs)]

    if (any(missing_req)):
        return jsonify(success=False, error=f"Missing required input: '{[[option for option in opt_def if not option['optional']][i]['name'] for i, x in enumerate(missing_req) if x][0]}'")

    for option in [*request.form, *arr_names]:
        if option not in [option['name'] for option in opt_def]:
            return jsonify(success=False, error=f"Unexpected input: '{option}'")
        
        opt = [opt for opt in opt_def if opt['name'] == option][0]
        match opt['type']:
            # checkbox
            case 'checkbox':
                if request.form.get(option) == "true":
                    args.append(f'--{option}')
                elif request.form.get(option) == "false":
                    args.append(f'-!{option}')
                else:
                    return jsonify(success=False, error=f"Expected 'true' or 'false' for parameter '{option}'.")
            # text
            case 'text':
                val = request.form.get(option)
                if len(val) < opt['minlength'] or (opt['maxlength'] is not None and len(val) > opt['maxlength']):
                    return jsonify(success=False, error=f"Parameter '{option}' is of incorrect length.")
                if opt['pattern'] is not None and not re.match(opt['pattern'], val):
                    return jsonify(success=False, error=f"Parameter '{option}' does not match required pattern.")
                args.append(f'-""{option}')
                args.append(val)
            # number
            case 'number':
                val = request.form.get(option)
                try:
                    float(val)
                except ValueError:
                    return jsonify(success=False, error=f"Expected number value for parameter '{option}'.")
                if (opt['min'] is not None and float(val) < opt['min']) or (opt['max'] and float(val) > opt['max']):
                    return jsonify(success=False, error=f"Parameter '{option}' does not adhere to its defined minimum and maximum.")
                if opt['integer']:
                    try:
                        int(val)
                    except ValueError:
                        return jsonify(success=False, error=f"Parameter '{option}' should be an integer.")
                args.append(f'-{option}')
                args.append(val)
            # select
            case 'select':
                val = request.form.getlist(option)
                if not opt['multiselect'] and len(val) > 1:
                    return jsonify(success=False, error=f"Parameter '{option}' cannot have multiple values.")
                extra_opt = [v not in [poss['value'] for poss in opt['options']] for v in val]
                if any(extra_opt):
                    return jsonify(success=False, error=f"Option '{[[v for v in val][i] for i, x in enumerate(extra_opt) if x][0]}' not a valid value for parameter '{option}'.")
                if opt['multiselect']:
                    args.append(f'-[""]{option}')
                    args.append(', '.join(val))
                else:
                    args.append(f'-{option}')
                    args.append(val[0])
            # array
            case 'array':
                val = request.form.getlist(option) or []
                if isinstance(opt['length'], int) and len(val) != opt['length']:
                    return jsonify(success=False, error=f"Expected {opt['length']} values for parameter '{option}', received {len(val)}.")
                if opt['items']['type'] == 'text':
                    prefix = '-[""]'
                    for s in val:
                        if len(s) < opt['items']['minlength'] or (opt['items']['maxlength'] is not None and len(s) > opt['items']['maxlength']):
                            return jsonify(success=False, error=f"A value for parameter '{option}' is of incorrect length.")
                        if opt['items']['pattern'] is not None and not re.match(opt['items']['pattern'], s):
                            return jsonify(success=False, error=f"A value for parameter '{option}' does not match required pattern.")
                elif opt['items']['type'] == 'number':
                    prefix = '-[]'
                    for n in val:
                        try:
                            float(n)
                        except ValueError:
                            return jsonify(success=False, error=f"Expected all number values for parameter '{option}'.")
                        if (opt['items']['min'] is not None and n < opt['items']['min']) or (opt['items']['max'] and n > opt['items']['max']):
                            return jsonify(success=False, error=f"A value for parameter '{option}' does not adhere to its defined minimum and maximum.")
                        if opt['items']['integer']:
                            try:
                                int(val)
                            except ValueError:
                                return jsonify(success=False, error=f"A value for parameter '{option}' should be an integer.")

                args.append(f'{prefix}{option}')
                args.append(', '.join(val))
    if len(filepaths) == 0:
        id = 'noid'
    
    command = f'{os.getenv('LANGUAGE')} wrapper.{os.getenv('EXTENSION')} calculation.{os.getenv('EXTENSION')} {os.getenv('METHOD')} {os.getenv('OUTPUT_STRING')} {id}'
    args = command.split(' ') + args
    res = subprocess.check_output(args)
    
    for file in filepaths:
        os.remove(file)

    json_out = eval(res)
    if 'error' in json_out:
        print(json_out['error'])
        return jsonify(success=False, error='Server error; please try again later.')
        
    return jsonify(success=True, data=json_out)

if __name__ == '__main__':
    app.run()