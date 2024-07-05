import sys
import os
import argparse as ap
import json
from jsonschema import validate, ValidationError
from config_schema import config_schema
from bs4 import BeautifulSoup
from shutil import copytree

inp_path = os.path.join(sys._MEIPASS, './template') if getattr(sys, 'frozen', False) else './template'
outp_path = './app'

def check_paths():
    # check filepaths
    try:
        with open(args.math_filepath) as math_file:
            ext = math_file.name.split('.')[-1]
            if ext not in ['py', 'r']:
                raise 'bad filetype'
    except FileNotFoundError | 'bad filetype':
        print('Math file must be a valid .r or .py path')

    if args.config is not None:
        try:
            with open(args.config) as cf:
                ext = cf.name.split('.')[-1]
                if ext != 'json':
                    raise 'bad filetype'
        except FileNotFoundError | 'bad filetype':
            print('Config file must be a valid .json path')

# uses 'default' values in schema to produce default config variables
def fillDefaults(obj, schema):
    if 'anyOf' in schema:
        for opt in schema['anyOf']:
            inter_schema = {**{x: schema[x] for x in schema.keys() if x != 'anyOf'}, **opt}
            try:
                validate(obj, schema)
            except ValidationError:
                continue
            
            schema = inter_schema
            break
    if 'type' in schema:
        match schema['type']:
            case 'object':
                for key in schema['properties'].keys():
                    if key in obj:
                        obj[key] = fillDefaults(obj[key], schema['properties'][key])
                    elif 'default' in schema['properties'][key]:
                        obj[key] = schema['properties'][key]['default']
                    else:
                        obj[key] = fillDefaults({}, schema['properties'][key])
            case 'array':
                for i in range(len(obj)):
                    obj[i] = fillDefaults(obj[i], schema['items'])
            case _:
                pass
    return obj

def parseConfigToObj(cf):
    config = json.load(cf)
    try:
        val = validate(config, config_schema)
    except ValidationError as e:
        print('Invalid config file: ' + e.message)
        return None
    
    return fillDefaults(config, config_schema)

def createInput(html, options):
    match(options['type']):
        case 'text' | 'number' | 'checkbox':
            input = html.new_tag('input')
            input['type'] = options['type']
            input['id'] = f'{options['name']}_inp'
            input['name'] = options['name']
            if not options['optional']:
                input['class'] = 'required'
            if options['type'] == 'text':
                if options['minlength'] > 0:
                    input['minlength'] = options['minlength']
                if options['maxlength'] is not None:
                    input['maxlength'] = options['maxlength']
                if options['pattern'] is not None:
                    input['pattern'] = options['pattern']
            if options['type'] == 'number':
                if options['min'] is not None:
                    input['min'] = options['min']
                if options['max'] is not None:
                    input['max'] = options['max']
                if options['integer']:
                    input['type'] = 'text'
                    input['pattern'] = '\\d*'
        case 'select':
            input = html.new_tag('select')
            input['id'] = f'{options['name']}_inp'
            input['name'] = options['name']
            if not options['optional']:
                input['class'] = 'required'
            for option in options['options']:
                option_el = html.new_tag('option')
                option_el['value'] = option
                option_el.text = option
                input.append(option_el)

    label = html.new_tag('label')
    label['for'] = f'{options['name']}_inp'
    label.string = options['description']
    div = html.new_tag('div')
    div.append(label)
    div.append(input)
    return div

if __name__ == '__main__':
    parser = ap.ArgumentParser(prog='Statistical App Generator', description='Generates a stats web app from a template')
    parser.add_argument('math_filepath')
    parser.add_argument('-c', '--config')

    args = parser.parse_args()

    check_paths()
    if args.config is not None:
        with open(args.config) as cf:
            cf = parseConfigToObj(cf)
            if cf is None:
                sys.exit(0)
    else:
        cf = fillDefaults({}, config_schema)

    print(cf)
    
    # copies 'template' directory (in executable) to new 'app' directory
    copytree(inp_path, outp_path)
    