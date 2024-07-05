import sys
import os
from bs4 import BeautifulSoup

read_path = os.path.join(sys._MEIPASS, './template.html') if getattr(sys, 'frozen', False) else './template.html'
write_path = './static/index.html'

def getInput(options):
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
            label = html.new_tag('label')
            label['for'] = f'{options['name']}_inp'
            label.string = options['description']
            div = html.new_tag('div')
            div.append(label)
            div.append(input)
            return div

with open(read_path) as file:
    html = BeautifulSoup(file.read(), 'html.parser')

    form = html.find('form', class_="calcForm")
    div = getInput({
        'name': 'test1',
        'description': 'A, B, or C',
        'type': 'text',
        'pattern': 'A|B|C',
        'optional': False,
        'minlength': 0,
        'maxlength': None
    })
    form.insert(0, div)

with open(write_path, "w+") as file:
    file.write(html.prettify())