import time
from flask import Flask, render_template, redirect, request, jsonify
import pandas as pd
from dotenv import load_dotenv
import json
import os
import subprocess
from decimal import Decimal

load_dotenv('.env')

app = Flask(__name__)

@app.route('/index')
def alias():
    return redirect('/')

@app.get('/')
def home():
    return render_template('index.html')

def convert_numbers(obj, precision):
    if type(obj) is int or type(obj) is float:
        return str(obj) if precision == 'any' else '{num:.{prec}f}'.format(num=Decimal(str(obj)), prec=precision)
    if type(obj) is list:
        for i, item in enumerate(obj):
            obj[i] = convert_numbers(item, precision)
    if type(obj) is dict:
        for k, v in obj.items():
            print(k)
            print(v)
            obj[k] = convert_numbers(v, precision)
    return obj

@app.post('/')
def upload():
    id = time.time() * 1000
    filepaths = []
    args = []
    for name in request.files:
        file = request.files[name]
        if file.filename == '':
            continue
        if file.content_type != 'text/csv':
            return jsonify(success=False, error=f'Bad filetype (should be CSV): {file.filename}')
        csv = pd.read_csv(file.stream)
        if os.getenv(f'XVAR_{file.name}') not in csv.columns or os.getenv(f'YVAR_{file.name}') not in csv.columns:
            return jsonify(success=False, error=f'Missing column(s) in {file.filename}; should have {os.getenv(f'XVAR_{file.name}')} and {os.getenv(f'YVAR_{file.name}')}')
        filename = f'{file.name}_{id}.csv'
        file.stream.seek(0)
        file.save(os.path.join('temp', filename))
        filepaths.append(os.path.join('temp', filename))
    for option in request.form:
        # checkbox
        if request.form.get(option) == "true":
            args.append(f'--{option}')
        elif request.form.get(option) == "false":
            args.append(f'-!{option}')
        # text
        else:
            args.append(f'-{option}')
            args.append(request.form.get(option))
    if len(filepaths) == 0:
        id = 'noid'
    
    command = f'{os.getenv('LANGUAGE')} wrapper.{os.getenv('EXTENSION')} calculation.{os.getenv('EXTENSION')} {os.getenv('METHOD')} {os.getenv('OUTPUT_STRING')} {id}'
    args = command.split(' ') + args
    res = subprocess.check_output(args)
    
    for file in filepaths:
        os.remove(file)

    json_out = eval(res)
    json_out = convert_numbers(json_out, int(os.getenv('PRECISION')))
        
    return jsonify(success=True, data=json_out)

if __name__ == '__main__':
    app.run()