import sys
import os
import argparse as ap
import json
from jsonschema import validate, ValidationError
from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter
from shutil import copytree, rmtree, copyfile
from alive_progress import alive_bar
import numpy as np
from html import escape
import copy
import gui

inp_path = os.path.join(sys._MEIPASS, './template') if getattr(sys, 'frozen', False) else './template'
outp_path = './app'

def check_paths():
    # check filepaths
    try:
        with open(args['math_filepath']) as math_file:
            ext = math_file.name.split('.')[-1]
            if ext not in ['py', 'r']:
                raise Exception('bad filetype')
    except (Exception):
        raise Exception('Math file must be a valid .r or .py path')

    if args['config'] is not None:
        try:
            with open(args['config']) as cf:
                ext = cf.name.split('.')[-1]
                if ext != 'json':
                    raise Exception('bad filetype')
        except (Exception):
            raise Exception('Config file must be a valid .json path')

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
        raise Exception('Invalid config file: ' + e.message)
    
    return fillDefaults(config, schema)

def createInput(html, options):
    match(options['type']):
        case 'text' | 'number' | 'checkbox':
            input = html.new_tag('input')
            input['type'] = options['type']
            small_string = f'{options["type"]} input'
            input['id'] = f'{options['name']}_inp'
            input['name'] = options['name']
            if not options['optional']:
                input['class'] = 'required'
            if options['type'] == 'text':
                if options['minlength'] > 0:
                    input['minlength'] = options['minlength']
                    if options['maxength'] is None:
                        small_string += f', minimum {options["minlength"]} characters'
                if options['maxlength'] is not None:
                    input['maxlength'] = options['maxlength']
                    small_string += f', {options["minlength"]} - {options["maxlength"]} characters'
                if options['pattern'] is not None:
                    input['pattern'] = options['pattern']
                    small_string += f'<br>pattern: {options["pattern"]}'
            if options['type'] == 'number':
                input['step'] = 'any'
                if options['integer']:
                    input['step'] = '1'
                    small_string = 'integer input'
                if options['min'] is not None:
                    input['min'] = options['min']
                    small_string += f', min: {options["min"]}'
                if options['max'] is not None:
                    input['max'] = options['max']
                    small_string += f', max: {options["max"]}'
        case 'select':
            input = html.new_tag('select')
            input['id'] = f'{options['name']}_inp'
            input['name'] = options['name']
            if not options['optional']:
                input['class'] = 'required'
            small_string = 'Select one dropdown option'
            if options['multiselect']:
                input['multiple'] = ''
                small_string = 'Ctrl + click or drag to select multiple'
            def_el = html.new_tag('option')
            def_el['disabled'] = ''
            def_el['value'] = ''
            def_el['selected'] = ''
            for option in options['options']:
                option_el = html.new_tag('option')
                option_el['value'] = option['value']
                option_el.string = escape(option['text'])
                input.append(option_el)
        case 'array':
            input = html.new_tag('div')
            small_string = None
            ctr = html.new_tag('div')
            inp = html.new_tag('input')
            inp['type'] = options['items']['type']
            inp['id'] = f'{options['name']}_'
            inner_small_string = f'{options["type"]} input'
            inp['name'] = options['name']
            if not options['optional']:
                inp['class'] = 'required'
            if options['items']['type'] == 'text':
                if options['items']['minlength'] > 0:
                    inp['minlength'] = options['items']['minlength']
                    if options['items']['maxength'] is None:
                        inner_small_string += f', minimum {options["items"]["minlength"]} characters'
                if options['items']['maxlength'] is not None:
                    inp['maxlength'] = options['items']['maxlength']
                    inner_small_string += f', {options["items"]["minlength"]} - {options["items"]["maxlength"]} characters'
                if options['items']['pattern'] is not None:
                    inp['pattern'] = options['items']['pattern']
                    inner_small_string += f'<br>pattern: {options["items"]["pattern"]}'
            if options['items']['type'] == 'number':
                inp['step'] = 'any'
                if options['items']['integer']:
                    inp['step'] = '1'
                    inner_small_string = 'integer input'
                if options['items']['min'] is not None:
                    inp['min'] = options['items']['min']
                    inner_small_string += f', min: {options["items"]["min"]}'
                if options['items']['max'] is not None:
                    inp['max'] = options['items']['max']
                    inner_small_string += f', max: {options["items"]["max"]}'
            sublabel = html.new_tag('label')
            sublabel['for'] = f'{options["name"]}_'
            span = html.new_tag('span')
            span.string = 'Element '
            sublabel.append(span)
            sublabel.append(html.new_tag('br'))

            small = html.new_tag('small')
            small.string = inner_small_string

            sublabel.append(small)
            
            if isinstance(options['length'], int):
                num_inps = options['length']
            else:
                num_inps = 1
                ctr['data-depends-on'] = options['length']

            ctr['class'] = f'array-input-{options["name"]}'

            ctr.append(sublabel)
            ctr.append(inp)
            
            for idx in range(num_inps):
                it_ctr = copy.copy(ctr)
                it_ctr.find('input')['id'] += str(idx)
                it_ctr.find('label')['for'] += str(idx)
                it_ctr.find('label').find('span').string += str(idx)
                input.append(it_ctr)

            input['id'] = f'{options['name']}_inp'
            input['class'] = 'option_array'

    div = html.new_tag('div')
    div['class'] = 'option'
    if 'description' in options:
        label = html.new_tag('label')
        label['for'] = f'{options["name"]}_inp'
        span = html.new_tag('span')
        span.string = escape(options['description'])
        label.append(span)
        label.append(html.new_tag('br'))

        if small_string is not None:
            small = html.new_tag('small')
            small.string = small_string
            label.append(small)
        div.append(label)
    if options['type'] == 'checkbox':
        hidden = html.new_tag('input')
        hidden['type'] = 'hidden'
        hidden['name'] = options['name']
        hidden['value'] = 'false'
        input['value'] = 'true'
        input['onfocus'] = "$(e.target).siblings('.checkbox_repl').focus()"
        label.append(input)
        div.append(hidden)
        repl = html.new_tag('span')
        repl['class'] = 'checkbox_repl'
        label.append(repl)
    else:
        div.append(input)
    return div

def createFileInput(html, options, graph):
    label = html.new_tag('label')
    label['for'] = f'{options["name"]}_inp'
    span = html.new_tag('span')
    span.string = options['name']
    label.append(span)
    small = html.new_tag('small')
    small.string = f'Requires \'{options["x_param"]}\', \'{options["y_param"]}\''
    label.append(html.new_tag('br'))
    label.append(small)
    input_ctr = html.new_tag('div')

    inner_label = html.new_tag('label')
    inner_label['for'] = f'{options["name"]}_inp'
    file_upload = html.new_tag('span')
    file_upload['class'] = 'file-upload'
    file_upload.string = 'Upload .csv file'
    p = html.new_tag('p')
    p['class'] = 'filename'
    inner_label.append(file_upload)
    inner_label.append(p)

    input = html.new_tag('input')
    input['type'] = 'file'
    input['id'] = f'{options["name"]}_inp'
    input['class'] = 'file'
    input['name'] = options["name"]
    if not options['optional']:
        input['class'] += ' required'
    input['data-x-label'] = options['x_param']
    input['data-y-label'] = options['y_param']
    input_ctr.append(input)
    input_ctr.append(inner_label)
    ctr = html.new_tag('div')
    ctr['class'] = 'file-ctr'
    ctr.append(label)

    if graph:
        canvas = html.new_tag('canvas')
        canvas['class'] = 'filechart'
        input_ctr.append(canvas)
    ctr.append(input_ctr)
    error = html.new_tag('p')
    p['class'] = 'error'
    ctr.append(error)
    return ctr

if __name__ == '__main__':
    if len(sys.argv) == 1:
        gui_mode = True
        # GUI
        args = gui.create_gui()
    else:
        gui_mode = False
        parser = ap.ArgumentParser(prog='Statistical App Generator', description='Generates a stats web app from a template')
        parser.add_argument('math_filepath', help="Path to a .py or .r file, containing a function (named 'calc' unless otherwise specified in config), which does math given an argument object and outputs an object", required=True)
        parser.add_argument('-c', '--config', help="Path to a .JSON file (format in README.md) for app configuration", required=True)
        parser.add_argument('-o', '--out', help="Relative or absolute path where an 'app' directory should be generated containing the application", required=True)

        args = parser.parse_args()
    outp_path = os.path.join(args['out'], 'app')

    try:
        if not gui_mode:
            bar = alive_bar(unknown='brackets', spinner='classic', calibrate=40)
        else:
            bar = None
        if bar:
            bar.text('Reading config schema...')
        with open(os.path.join(sys._MEIPASS, './schema.json') if getattr(sys, 'frozen', False) else './schema.json') as jsonschema:
            config_schema = json.load(jsonschema)
        if bar:
            bar()

        if bar:
            bar.text('Parsing config...')
        check_paths()
        with open(args['config']) as cf:
            cf = parseConfigToObj(cf, config_schema)
        if bar:
            bar()

        # checks for repeat inputs/outputs
        inp_unique, cts = np.unique([option['name'] for option in [*cf['options'], *cf['settings']['input_file']['files']]], return_counts=True)
        if len(inp_unique[cts > 1]) > 0:
            raise Exception('Repeated option/file names not allowed!')
        
        outp_unique, cts = np.unique([option['name'] for option in cf['output']['format']], return_counts=True)
        if len(outp_unique[cts > 1]) > 0:
            raise Exception('Repeated output names not allowed!')
        if bar:
            bar()

        # checks array variable names against inputs
        varnames = [option['length'] for option in cf['options'] if option['type'] == 'array' and isinstance(option['length'], str)]
        for varname in varnames:
            if varname not in inp_unique or varname in [option['name'] for option in cf['settings']['input_file']['files']]:
                raise Exception('Please check validity of all variable array length reference names!')

        # creates generated .env file
        env_vars = {
            'METHOD': cf['output']['function_name'],
            'LANGUAGE': 'python' if args['math_filepath'].split('.')[-1] == 'py' else 'Rscript',
            'EXTENSION': args['math_filepath'].split('.')[-1]
        }

        output_strs = []
        graph_obj = {}
        out_descr = {}
        for option in cf['output']['format']:
            match option['type']:
                case 'graph':
                    output_strs.append(f'{option["name"]}:graph({option["x_axis"]}/{"|".join([col['column_name'] for col in option["y_axis"]] if isinstance(option['y_axis'], list) else "!")})')
                    graph_obj[option["name"]] = {'x': option["x_axis"], 'y': option["y_axis"] if not isinstance(option["y_axis"], list) else [col['plot_type'] for col in option["y_axis"]], 'legend': option['legend'], 'x_label': option['x_label'] or option['x_axis'], 'y_label': option['y_label']}
                case 'table':
                    output_strs.append(f'{option["name"]}:table({option["precision"] if not isinstance(option["precision"], list) else "|".join(map(str, option["precision"]))})')
                case 'text':
                    output_strs.append(f'{option["name"]}:text')
                case 'data_table':
                    output_strs.append(f'{option["name"]}:data_table({option["precision"] if not isinstance(option["precision"], list) else "|".join(map(str, option["precision"]))})')
            out_descr[option['name']] = option['description']
        env_vars['OPTIONS'] = json.dumps(cf['options'])
        env_vars['OUTPUT_STRING'] = ','.join(output_strs)
        if bar:
            bar()

        for option in cf['settings']['input_file']['files']:
            env_vars[f'XVAR_{option["name"]}'] = option['x_param']
            env_vars[f'YVAR_{option["name"]}'] = option['y_param']
            env_vars[f'REQUIRED_{option["name"]}'] = not option['optional']
        if bar:
            bar()


        if bar:
            bar.text('Generating HTML...')
        # reads existing HTML template
        with open(os.path.join(inp_path, 'templates/index.html')) as file:
            html = BeautifulSoup(file.read(), 'html.parser')
        with open(os.path.join(inp_path, 'templates/base.html')) as file:
            base_html = BeautifulSoup(file.read(), 'html.parser')
        if bar:
            bar()
        
        # adds necessary options to templates/index.html
        form = html.find('form', class_="calcForm")

        for i, option in enumerate(cf['options']):
            div = createInput(html, option)
            form.insert(i, div)

        # adds title
        title = html.new_tag('h1')
        title.string = escape(cf['settings']['title'])
        html.find('div', class_='tab active').insert(0, title)

        graph = cf['settings']['input_file']['graph_input']
        for i, option in enumerate(cf['settings']['input_file']['files']):
            div = createFileInput(html, option, graph)
            form.insert(i, div)

        # set color theme
        body = base_html.find('body')
        body['color'] = cf['settings']['themeColor']

        # set title
        base_html.find('title').string = cf['settings']['title']
        
        if bar:
            bar.text('Copying template app...')
        # copies 'template' directory (in executable) to new 'app' directory
        if os.path.exists(outp_path):
            rmtree(outp_path)
            if bar:
                bar()
        copytree(inp_path, outp_path)
        if bar:
            bar()

        if bar:
            bar.text(f'Copying {args["math_filepath"]} to app...')
        # copies math file into app
        copyfile(args['math_filepath'], os.path.join(outp_path, f'calculation.{args['math_filepath'].split('.')[-1]}'))
        if bar:
            bar()

            
        # writes output
        formatter = HTMLFormatter(indent=4)
        with open(os.path.join(outp_path, 'templates/index.html'), 'w') as file:
            file.write(html.prettify(formatter=formatter))
        with open(os.path.join(outp_path, 'templates/base.html'), 'w') as file:
            file.write(base_html.prettify(formatter=formatter))
        if bar:
            bar()


        if bar:
            bar.text(f'Writing to {os.path.join(outp_path, ".env")}')
        with open(os.path.join(outp_path, '.env'), 'w') as file:
            file.write('\n'.join([f'{kv[0]}={kv[1]}' for kv in env_vars.items()]))
        if bar:
            bar()

        if bar:
            bar.text('Generating JavaScript...')
        # writes graph_obj to script.js
        with open(os.path.join(inp_path, 'static/script.js'), 'r') as file:
            js_contents = file.read()
        with open(os.path.join(outp_path, 'static/script.js'), 'w') as file:
            file.write('\n'.join([f'const graphObj = {json.dumps(graph_obj)};', f'const descriptions = {json.dumps(out_descr)};', js_contents]))
        if bar:
            bar()
    except Exception as e:
        if gui_mode:
            gui.create_exc(str(e))
        else:
            raise e

if gui_mode:
    gui.show_success_msg(os.path.abspath(outp_path))
else:
    print(f'App generated at {os.path.abspath(outp_path)}')