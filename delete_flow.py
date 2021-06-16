import json
import httplib2

import config

ip = config.baseIP
port = config.port
http = httplib2.Http()
http.add_credentials(config.username, config.password)


# ==================================================================================================================
# Delete flow cache
def delete_flow(url, flow_delete, id_table_delete, id_flow_delete):
    # fill the url
    url_put = url % (ip, port, flow_delete, str(id_table_delete), str(id_flow_delete))
    body = {}
    content = http.request(url_put,
                           method="DELETE", body=json.dumps(body))[1]

    print(content.decode())


url_input = "http://%s:%s/restconf/config/opendaylight-inventory:nodes/node/%s/flow-node-inventory" \
            ":table/%s/flow/%s"

# =======================================
# delete flows
delete_flow(url_input, "openflow:2", 2, 1)
delete_flow(url_input, "openflow:2", 2, 2)
delete_flow(url_input, "openflow:1", 1, 3)
delete_flow(url_input, "openflow:1", 1, 4)
delete_flow(url_input, "openflow:4", 4, 5)
delete_flow(url_input, "openflow:4", 4, 6)
delete_flow(url_input, "openflow:3", 3, 7)
delete_flow(url_input, "openflow:3", 3, 8)