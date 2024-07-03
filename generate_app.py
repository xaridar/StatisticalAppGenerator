import sys
import argparse as ap
import json
from jsonschema import validate, ValidationError
from config_schema import config_schema

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
        return False
    
    config = fillDefaults(config, config_schema)
    print(config)

if __name__ == '__main__':
    parser = ap.ArgumentParser(prog='Statistical App Generator', description='Generates a stats web app from a template')
    parser.add_argument('math_filepath')
    parser.add_argument('-c', '--config')

    args = parser.parse_args()

    check_paths()
    with open(args.config) as cf:
        if not parseConfigToObj(cf):
            sys.exit(0)
    
    