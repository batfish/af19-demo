from jinja2 import Environment, FileSystemLoader
import json
import os
from os import listdir
from os.path import isfile, join
import re

BASE_DIR = os.getcwd()
yaml_dir = BASE_DIR + '/inputs/'
template_dir = BASE_DIR + '/templates/'
inventory_file = BASE_DIR + '/playbooks/inventory'
inventory_template = template_dir + 'inventory.j2'

if not os.path.isdir(yaml_dir):
    raise ValueError("YAML input directory does not exist")

file_map = {
    'leaf': [],
    'spine': []
}

for k in file_map.keys():
    regex = re.compile("(^{}[\d]+).yml$".format(k))

    for f in os.listdir(yaml_dir):
        match = re.match(regex, f)
        if match:
            file_map[k].append(match.group(1))

    file_map[k].sort()

#render template
file_loader = FileSystemLoader(template_dir)
env = Environment(loader=file_loader, trim_blocks=True, extensions=['jinja2.ext.do'])

template = env.get_template('inventory.j2')
template_output = template.render(leaf_list = file_map['leaf'], spine_list = file_map['spine'])

with open(inventory_file, 'w') as f:
    f.write(template_output)