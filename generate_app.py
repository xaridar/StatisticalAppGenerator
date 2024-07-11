import sys
import os
import argparse as ap
import json
from jsonschema import validate, ValidationError
from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter
from shutil import copytree, rmtree, copyfile

inp_path = os.path.join(sys._MEIPASS, './template') if getattr(sys, 'frozen', False) else './template'
outp_path = './app'

def check_paths():
    # check filepaths
    try:
        with open(args.math_filepath) as math_file:
            ext = math_file.name.split('.')[-1]
            if ext not in ['py', 'r']:
                raise Exception('bad filetype')
    except (Exception):
        print('Math file must be a valid .r or .py path')
        return False

    if args.config is not None:
        try:
            with open(args.config) as cf:
                ext = cf.name.split('.')[-1]
                if ext != 'json':
                    raise Exception('bad filetype')
        except (Exception):
            print('Config file must be a valid .json path')
            return False
    return True

# uses 'default' values in schema to produce default config variables
def fillDefaults(obj, schema):
    if '$ref' in schema:
        path = schema['$ref'][2:].split('/')
        internal = config_schema
        for ele in path:
            internal = internal[ele]
        schema = {**{x: schema[x] for x in schema.keys() if x != '$ref'}, **internal}
    if 'anyOf' in schema:
        objType = obj['type']
        for opt in schema['anyOf']:
            interType = opt['properties']['type']['const']
            inter_schema = {**{x: schema[x] for x in schema.keys() if x != 'anyOf'}, **opt}
            
            if interType != objType:
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

def parseConfigToObj(cf, schema):
    config = json.load(cf)
    try:
        validate(config, schema)
    except ValidationError as e:
        print('Invalid config file: ' + e.message)
        return None
    
    return fillDefaults(config, schema)

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
            def_el = html.new_tag('option')
            def_el['disabled'] = ''
            def_el['value'] = ''
            def_el['selected'] = ''
            for option in options['options']:
                option_el = html.new_tag('option')
                option_el['value'] = option['value']
                option_el.string = option['text']
                input.append(option_el)
        case 'option_group':
            input = html.new_tag('div')
            input['id'] = options['id']
            input['class'] = 'option-group'
            if options['header'] != '':
                span = html.new_tag('span')
                span.string = options['header']
                input.append(span)
            for option in options['options']:
                inp = createInput(html, option)
                input.append(inp)

    div = html.new_tag('div')
    div['class'] = 'option'
    div.append(input)
    if 'description' in options and options['description'] != '':
        label = html.new_tag('label')
        label['for'] = f'{options['name']}_inp'
        label.string = options['description']
        div.append(label)
    if options['type'] == 'checkbox':
        hidden = html.new_tag('input')
        hidden['type'] = 'hidden'
        hidden['name'] = options['name']
        hidden['value'] = 'false'
        input['value'] = 'true'
        div.append(hidden)
    return div

def createFileInput(html, options, graph):
    input = html.new_tag('input')
    input['type'] = 'file'
    input['id'] = f'{options['name']}_inp'
    input['class'] = 'file'
    input['name'] = options['name']
    if not options['optional']:
        input['class'] += ' required'
    input['data-x-label'] = options['x_param']
    input['data-y-label'] = options['y_param']
    ctr = html.new_tag('div')
    ctr['class'] = 'file-ctr'
    ctr.append(input)
    if graph:
        canvas = html.new_tag('canvas')
        canvas['class'] = 'filechart'
        ctr.append(canvas)
    return ctr

if __name__ == '__main__':
    parser = ap.ArgumentParser(prog='Statistical App Generator', description='Generates a stats web app from a template')
    parser.add_argument('math_filepath', help="Path to a .py or .r file, containing a function (named 'calc' unless otherwise specified in config), which does math given an argument object and outputs an object")
    parser.add_argument('-c', '--config', help="Path to a .JSON file (format in schema.json) for app configuration")

    args = parser.parse_args()

    with open('./schema.json') as jsonschema:
        config_schema = json.load(jsonschema)

    if not check_paths():
        sys.exit(1)
    if args.config is not None:
        with open(args.config) as cf:
            cf = parseConfigToObj(cf, config_schema)
            if cf is None:
                sys.exit(0)
    else:
        cf = fillDefaults({}, config_schema)

    print(json.dumps(cf, indent=4))
    
    # copies 'template' directory (in executable) to new 'app' directory
    if os.path.exists(outp_path):
        rmtree(outp_path)
    copytree(inp_path, outp_path)

    # copies math file into app
    copyfile(args.math_filepath, os.path.join(outp_path, f'calculation.{args.math_filepath.split('.')[-1]}'))

    # creates generated .env file
    env_vars = {
        'METHOD': cf['settings']['output']['function_name'],
        'LANGUAGE': 'python' if args.math_filepath.split('.')[-1] == 'py' else 'Rscript',
        'EXTENSION': args.math_filepath.split('.')[-1]
    }

    if cf['settings']['input_file']['enabled']:
        for option in cf['settings']['input_file']['files']:
            env_vars[f'XVAR_{option['name']}'] = option['x_param']
            env_vars[f'YVAR_{option['name']}'] = option['y_param']

    with open(os.path.join(outp_path, '.env'), 'w') as file:
        file.write('\n'.join([f'{kv[0]}="{kv[1]}"' for kv in env_vars.items()]))

    # reads existing HTML template
    with open(os.path.join(inp_path, 'templates/index.html')) as file:
        html = BeautifulSoup(file.read(), 'html.parser')
    with open(os.path.join(inp_path, 'templates/base.html')) as file:
        base_html = BeautifulSoup(file.read(), 'html.parser')
    
    # adds necessary options to templates/index.html
    form = html.find('form', class_="calcForm")

    for i, option in enumerate(cf['options']):
        div = createInput(html, option)
        form.insert(i, div)

    if cf['settings']['input_file']['enabled']:
        graph = cf['settings']['input_file']['graph_input']
        for i, option in enumerate(cf['settings']['input_file']['files']):
            div = createFileInput(html, option, graph)
            form.insert(i, div)

    # set color theme
    body = base_html.find('body')
    body['color'] = cf['settings']['themeColor']
        
    # writes output
    formatter = HTMLFormatter(indent=4)
    with open(os.path.join(outp_path, 'templates/index.html'), 'w') as file:
        file.write(html.prettify(formatter=formatter))
    with open(os.path.join(outp_path, 'templates/base.html'), 'w') as file:
        file.write(base_html.prettify(formatter=formatter))