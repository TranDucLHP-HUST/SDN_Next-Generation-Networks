import requests
import json
import httplib2
import re
from termcolor import colored

import config

ip = config.baseIP
port = config.port
http = httplib2.Http()
http.add_credentials(config.username, config.password)

format_flow_add = """
    {
        "flow": [
        {
            "id": "%s",
            "flow-name": "%s",
            "instructions": {
                "instruction": [
                {
                    "order": 0,
                    "apply-actions": {
                    "action": [
                        {
                        "order": 0,
                        "output-action": {
                            "output-node-connector": "%s"
                        }
                        }
                    ]
                    }
                }
                ]
            },
            "flags": "",
            "match": {
                "in-port": "%s",
                "ethernet-match": {
                "ethernet-source": {
                    "address": "%s"
                },
                "ethernet-destination": {
                    "address": "%s"
                }
                }
            },
            "hard-timeout": 0,
            "priority": 2,
            "table_id": "%s",
            "idle-timeout": 0
            }
            ]
    }

    """

# init id_table, id_flow
flow = 0


def get_data_json(file):
    # Opening JSON file
    f = open(file, 'r')

    # returns JSON object as
    # a dictionary
    data_json = json.load(f)
    f.close()

    # return data to string
    return str(data_json)


def add_flow(mac_source, mac_destination, port_source, port_destination, flow_id, table_id):
    # get format add flow from file
    global format_flow_add
    format_add_flow = format_flow_add  # get_data_json('file.json')

    flow_name = "flow_" + flow_id
    return format_add_flow % (flow_id, flow_name, port_destination, port_source, mac_source, mac_destination, table_id)


def filter_max(host):
    list_str = host.split(':')
    if len(list_str[0]) == 2:
        return host
    else:
        return ':'.join(list_str[1:])


def put_request(url, data):
    global flow
    flow += 1
    # get each data in data
    node, mac_src, mac_dst, port_in, port_out, flow = data
    mac_src = filter_max(mac_src)
    mac_dst = filter_max(mac_dst)

    # each switch has 1 table
    table = re.findall(r'\d+', node)[0]

    # fill the url
    url_put = url % (ip, port, node, table, str(flow))

    # get the data add flow
    data_put = add_flow(mac_src, mac_dst, str(port_in), str(port_out), str(flow), table)
    headers = {"Content-Type": "application/json"}

    body = json.loads(data_put)

    content = http.request(url_put,
                           method="PUT",
                           headers=headers,
                           body=json.dumps(body))[1]

    if str(content)[0] == 'b':
        print(colored("Add flow successfully!", 'green'))
        print("Flow information: ")
        print('{0:15} {1:10} {2:15} {3:22} {4:22} {5:22}'.format('NODE', 'TABLE', 'FLOW_ID',
                                                                 'PORT(IN-OUT)', 'MAC_SOURCE', 'MAC_DESTINATION'))
        print('{0:15} {1:10} {2:15} {3:22} {4:22} {5:22}'
              .format(node, table, str(flow), str(port_in+'-'+port_out), mac_src, mac_dst))
        print(colored("===================", 'green'))

    else:
        print(content.decode())


# main call function
def request(data):
    # data = (switch_node, host_source, host_destination, port_in, port_out, flow_id)
    url_input = "http://%s:%s/restconf/config/opendaylight-inventory:nodes/node/%s/flow-node-inventory" \
                ":table/%s/flow/%s"
    put_request(url_input, data)


