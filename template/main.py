from flask import Flask, render_template, redirect, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/index')
def alias():
    return redirect('/')

@app.get('/')
def home():
    return render_template('index.html')

@app.post('/')
def upload():
    if 'file' not in request.files:
        print('No file')
        return jsonify(success=False)
    file = request.files['file']
    if file.filename == '' or file.content_type != 'text/csv':
        print('No file')
        return jsonify(success=False)
    csv_data = pd.read_csv(file.stream)
    return jsonify(success=True, data=csv_data.to_string())

if __name__ == '__main__':
    app.run()