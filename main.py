"""
    File to get full information of topology in order to put flows
"""
import httplib2
import numpy as np
import json
from termcolor import colored
import logging
from subprocess import Popen, PIPE

import put_data
import config

########################################################################################################
# GLOBAL VARIABLES
########################################################################################################

baseUrl = config.baseUrl
baseIP = config.baseIP
h = httplib2.Http()
h.add_credentials(config.username, config.password)

# count flow
flow = 0


########################################################################################################
# SUPPORT FUNCTIONS
########################################################################################################
def get_all_wrapper(typestring, attribute):
    url = baseUrl + typestring
    logging.debug('url %s', url)
    _, content = h.request(url, "GET")
    allContent = json.loads(content)
    all_rows = allContent[attribute]
    if all_rows == {}:  # check if we have a topology
        print("Topology not found!")
        exit()
    elif all_rows == {u'topology': [{u'topology-id': u'flow:1'}]}:
        print("Topology not found!")
        exit()
    return all_rows


def systemCommand(cmd):
    terminalProcess = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    terminalOutput, stderr = terminalProcess.communicate()


# =======================================================================================
def get_all_nodes():
    node_list_data = get_all_wrapper('/operational/opendaylight-inventory:nodes', 'nodes')

    list_node = []
    for node in node_list_data['node']:
        list_node.append(node['id'])
        print(node['id'])

    return list_node


def get_all_hosts():
    host_list_data = get_all_wrapper('/operational/network-topology:network-topology', 'network-topology')

    list_host = []
    hosts = host_list_data['topology'][0]
    for host in hosts['node']:
        maybe_host = host['node-id']
        if maybe_host.startswith("host"):
            list_host.append(maybe_host)
            print(maybe_host)

    return list_host


def get_all_edges():
    all_edges_data = get_all_wrapper('/operational/network-topology:network-topology', 'network-topology')

    edges = all_edges_data['topology'][0]

    list_edge = []
    for edge in edges['link']:
        print('[' + edge['source']['source-tp'] + ']' + ' to ' + '[' + edge['destination']['dest-tp'] + ']')
        list_edge.append((edge['source']['source-tp'], edge['destination']['dest-tp']))

    return list_edge


# split and get mac address
def get_mac(host):
    return host[5:]


# check each connection in  route
def check_route(connection, list_edge):
    node_1 = connection[0]
    node_2 = connection[1]
    port_in = port_out = 0

    if node_1 == node_2:    # in one switch --> false
        return False, port_in, port_out

    check = False
    for each_edge in list_edge:
        if node_1 in each_edge[0] and node_2 in each_edge[1]:
            check = True
            port_out = each_edge[0][len(each_edge[0]) - 1:]
            port_in = each_edge[1][len(each_edge[1]) - 1:]
            break
        if node_1 in each_edge[1] and node_2 in each_edge[0]:
            check = True
            port_in = each_edge[0][len(each_edge[0]) - 1:]
            port_out = each_edge[1][len(each_edge[1]) - 1:]
            break

    return check, port_in, port_out


def user_interface():
    # show topology information
    print("This is your topology:")
    print("- List switches: ")
    list_switches = get_all_nodes()
    print('===================================')
    print("- List hosts: ")
    list_host = get_all_hosts()
    print('===================================')
    print("- List connections: ")
    list_edges = get_all_edges()

    # user add flow
    while True:
        print('===================================')
        print("Enter this information to add flow:")
        host_source = input("host source: ")
        host_destination = input("host destination: ")

        # check host
        if host_source not in list_host or host_destination not in list_host:
            print(colored("Host is not valid!", 'red'))
            continue

        list_switches_route = input("List switches in route (?-?..-?):")

        # check switchs in route
        list_switches_route = list_switches_route.split('-')

        # route has more one switch
        if len(list_switches_route) == 1:
            print(colored("Route is not valid!", 'red'))
            continue

        # check each switch in route
        check = True
        for switch in list_switches_route:
            if switch not in list_switches:
                check = False
                break
        if not check:
            print(colored("Some switches is not valid!", 'red'))
            continue

        # check route
        check = True
        list_port_connection = []
        for i in range(len(list_switches_route)-1):
            src = list_switches_route[i]
            dst = list_switches_route[i+1]

            find, port_in, port_out = check_route((src, dst), list_edges)
            list_port_connection.append(port_out)
            list_port_connection.append(port_in)

            if not find:
                print(colored("Route is not valid!", 'red'))
                check = False
                break

        if not check:
            continue

        # check connection between host and switch
        find, port_in, port_out = check_route((host_source, list_switches_route[0]), list_edges)
        if not find:
            print(colored("Route is not valid!", 'red'))
            continue
        list_port_connection.insert(0, port_in)

        find, port_in, port_out = check_route((list_switches_route[len(list_switches_route)-1], host_destination),
                                              list_edges)
        if not find:
            print(colored("Route is not valid!", 'red'))
            continue
        list_port_connection.append(port_out)

        print(colored("Adding flow ...", 'green'))
        # check input is ok, then process to add flow
        # get mac address of hosts
        host_s = get_mac(host_source)
        host_d = get_mac(host_destination)

        # add flow with put requests
        for i in range(len(list_switches_route)):
            switch_1 = list_switches_route[i]

            # data = (switch_node, host_source, host_destination, port_in, port_out, flow_id)
            global flow
            flow += 1
            data = (switch_1, host_s, host_d, list_port_connection[2*i], list_port_connection[2*i+1], flow)
            put_data.request(data)

            flow += 1
            data = (switch_1, host_d, host_s, list_port_connection[2 * i+1], list_port_connection[2 * i], flow)
            put_data.request(data)


def test():
    list_edges = get_all_edges()
    print(list_edges)
    data = ("openflow:2", "openflow:1")
    data_one = "host:fe:49:db:26:11:b5"
    print(check_route(data, list_edges))


user_interface()