from jinja2 import Environment, FileSystemLoader
import os
import re

import yaml
import pathlib

BASE_DIR = os.getcwd()
yaml_dir = BASE_DIR + '/inputs/'
template_dir = BASE_DIR + '/templates/'

cfg_dir = "{}/configs".format(os.environ.get("BF_SNAPSHOT_DIR", "."))

# Do not change the ordering of the templates in the dict below
# Batfish requires config stanzas for Cumulus to show up in a specific order in the config file
template_map = {
    'leaf': ['leaf_interfaces.j2', 'leaf_ports_conf.j2', 'leaf_frr.j2'],
    'bl': ['border_leaf_interfaces.j2','border_leaf_ports_conf.j2', 'border_leaf_frr.j2'],
    'spine': ['spine_interfaces.j2', 'spine_ports_conf.j2', 'spine_frr.j2'],
    'bor': ['border_config.j2'],
    'fwl': ['fwl_base_config_h.j2', 'fwl_zone_config_h.j2']
}


def get_router_list(yaml_dir):
    if not os.path.isdir(yaml_dir):
        raise ValueError("YAML input directory does not exist")

    file_map = {
        'leaf': [],
        'spine': [],
        'bl': [],
        'bor': [],
        'fwl': []
    }

    for k in file_map.keys():
        regex = re.compile("(^{}[\d]+).yml$".format(k))

        for f in os.listdir(yaml_dir):
            match = re.match(regex, f)
            if match:
                file_map[k].append(match.group(1))

        file_map[k].sort()

    return file_map

def assemble(template_dir, yaml_dir, router, cfg_dir, templates):
    file_loader = FileSystemLoader(template_dir)
    env = Environment(loader=file_loader, trim_blocks=True, extensions=['jinja2.ext.do'])

    with open("{}/{}.yml".format(yaml_dir, router), 'r') as f:
        router_conf = yaml.safe_load(f)
    f.close()
    config_file = "{}/{}.cfg".format(cfg_dir, router)

    f = open(config_file, "w")
    for template in templates:
        cfg_template = env.get_template(template)
        cfg = cfg_template.render(router_conf)
        f.write(cfg)
    f.close()

router_map = get_router_list(yaml_dir)

pathlib.Path(cfg_dir).mkdir(parents=True, exist_ok=True)
for rt_type in router_map.keys():
    print(rt_type)
    for router in router_map[rt_type]:
        print(router)
        assemble(template_dir, yaml_dir, router, cfg_dir, template_map[rt_type])
