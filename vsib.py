#!/usr/bin/env python

from smart_m3.m3_kp import *
import socket
import sys
from termcolor import colored
from sib import SIBLib

TCP_IP = '127.0.0.1'
TCP_PORT = 10010
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

# XML parser
from xml.etree import ElementTree as ET

### SSAP PROTOCOL DATA ###
SSAP_MESSAGE_TEMPLATE = '''
<SSAP_message>
<node_id>%s</node_id>
<space_id>%s</space_id>
<transaction_type>%s</transaction_type>
<message_type>CONFIRM</message_type>
<transaction_id>%s</transaction_id>
%s
</SSAP_message>'''

SSAP_JOIN_PARAM_TEMPLATE = '<parameter name = "status">%s</parameter>'
### END SSAP PROTOCOL DATA ###

# read the configuration file to see the real SIBs
tree = ET.parse('vsib_configuration.xml')
root = tree.getroot()

# create and fill a dict to store the info about real SIBs
rsib = {}
for r in root.findall('SIB'):
    sib_name = r.find('name').text
    rsib[sib_name] = {}
    rsib[sib_name]["IP"] = r.find('IP').text
    rsib[sib_name]["port"] = int(r.find('port').text)
    rsib[sib_name]["type"] = r.find('type').text
    print colored("virtualSIB> ", "red", attrs=["bold"]) + "Found a " + rsib[sib_name]["type"] + " sib with IP " + rsib[sib_name]["IP"] + " and port " + str(rsib[sib_name]["port"])

# connection to the SIBs
nodes = {}
for r in rsib.keys():
    print colored("virtualSIB> ", "red", attrs=["bold"]) + "Connecting to " + r
    nodes[r] = SIBLib.SibLib(rsib[r]["IP"], rsib[r]["port"])
    nodes[r].join_sib()
    
sys.exit()
    
# initialization of the TCP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(5)

# infinite loop
while 1:
    
    # incoming connection informations
    conn, addr = s.accept()
    print 'Connection address:', addr

    # received data
    data = conn.recv(BUFFER_SIZE)
    if not data: break
    print "received data:", data

    # data extraction
    xml = data
    root = ET.fromstring(xml)
    info = {}
    for child in root:
        info[child.tag] = child.text

    # send a reply to the client
    if info["transaction_type"] == "JOIN":
        reply = [SSAP_MESSAGE_TEMPLATE%(info["node_id"], info["space_id"],
                                        "JOIN", info["transaction_id"],
                                        SSAP_JOIN_PARAM_TEMPLATE%("m3:Success"))]
    elif info["transaction_type"] == "LEAVE":
        reply = [SSAP_MESSAGE_TEMPLATE%(info["node_id"], info["space_id"],
                                        "LEAVE", info["transaction_id"],
                                        SSAP_JOIN_PARAM_TEMPLATE%("m3:Success"))]
        
    reply_msg = "".join(reply)
    conn.send(reply_msg)

conn.close()
