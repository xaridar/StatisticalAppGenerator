import time
from flask import Flask, render_template, redirect, request, jsonify
import pandas as pd
from dotenv import load_dotenv
import os
import subprocess

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
    # if 'file' not in request.files:
    #     print('No file')
    #     return jsonify(success=False)
    # file = request.files['file']
    # if file.filename == '' or file.content_type != 'text/csv':
    #     print('No file')
    #     return jsonify(success=False)
    # csv_data = pd.read_csv(file.stream)
    # return jsonify(success=True, data=csv_data.to_string(), argnames=str(request.form.keys()))
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
    
    command = f'{os.getenv('LANGUAGE')} wrapper.{os.getenv('EXTENSION')} calculation.{os.getenv('EXTENSION')} {os.getenv('METHOD')} {id}'
    args = command.split(' ') + args
    res = subprocess.check_output(args)
    for file in filepaths:
        os.remove(file)
        
    return jsonify(success=True, data=res.decode('UTF-8'))

if __name__ == '__main__':
    app.run()