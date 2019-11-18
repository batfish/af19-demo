import yaml
import copy
import json

BASE_DIR = './'
OUT_DIR = BASE_DIR + 'snapshots/snapshot0'
topology_file = OUT_DIR + "/layer1_topology.json"

max_leaf = 96

spines = ['spine01', 'spine02', 'spine03', 'spine04']
lf_spines = {
    'spine01': 'swp49',
    'spine02': 'swp50',
    'spine03': 'swp51',
    'spine04': 'swp52',
}

bl_spines = {
    'spine01': 'swp1',
    'spine02': 'swp2',
    'spine03': 'swp3',
    'spine04': 'swp4'
}

empty_edge =  {
    "node1": {
        "hostname": "",
        "interfaceName": ""
    },
    "node2": {
        "hostname": "",
        "interfaceName": ""
    }
}

spine_port = {
    'spine01': 1,
    'spine02': 1,
    'spine03': 1,
    'spine04': 1
}

topology = {
    'edges': []
}

for spine in spines:
    node1 = spine

    for i in range(1,(max_leaf + 1)):
        node2 = "leaf"+ f'{i:02d}'

        rem = i % 4
        if rem != 0:
            spine_subport = rem - 1
        else:
            spine_subport = 3
        node1_port = "swp{}s{}".format(spine_port[spine], spine_subport)
        node2_port = lf_spines[spine]

        new_edge = copy.deepcopy(empty_edge)
        new_edge['node1']['hostname'] = node1
        new_edge['node1']['interfaceName'] = node1_port
        new_edge['node2']['hostname'] = node2
        new_edge['node2']['interfaceName'] = node2_port

        if spine_subport == 3:
            spine_port[spine] += 1

        topology['edges'].append(copy.deepcopy(new_edge))

    for i in range(1,3):
        node1_port = "swp{}".format(spine_port[spine])
        node2 = "bl" + f'{i:02d}'
        node2_port = bl_spines[spine]

        new_edge = copy.deepcopy(empty_edge)
        new_edge['node1']['hostname'] = node1
        new_edge['node1']['interfaceName'] = node1_port
        new_edge['node2']['hostname'] = node2
        new_edge['node2']['interfaceName'] = node2_port

        topology['edges'].append(copy.deepcopy(new_edge))
        spine_port[spine] +=1

print(new_edge)

with open(topology_file, 'w') as f:
    json.dump(topology, f)