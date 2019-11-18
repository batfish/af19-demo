import yaml
import copy

BASE_DIR = './'
yaml_template = BASE_DIR + '/inputs/leaf01.yml'

with open(yaml_template, 'r') as fp:
    template_data = yaml.safe_load(fp)

blank_template = copy.deepcopy(template_data)

for i in range (2,90):
    hostname = "leaf"+ f'{i:02d}'
    file_name = BASE_DIR + '/inputs/' + hostname + ".yml"
    blank_template['hostname'] = hostname
    blank_template['bgp_as'] = template_data['bgp_as'] + (i-1)
    blank_template['loopback']['address'] = "10.1.1.{}".format(str(i))
    blank_template['mgmt']['address'] = "10.254.1.{}/16".format(str(i))
    blank_template['ports'][4]['vlan'] = 100 + i
    blank_template['ports'][5]['vlan'] = 200 + i
    blank_template['vlans'][0]['id'] = 100 + i
    blank_template['vlans'][0]['address'] = "10.100.{}.1/24".format(str(i))
    blank_template['vlans'][1]['id'] = 200 + i
    blank_template['vlans'][1]['address'] = "10.200.{}.1/24".format(str(i))

    with open(file_name, 'w') as yaml_file:
        yaml.dump(blank_template, yaml_file, default_flow_style=False)