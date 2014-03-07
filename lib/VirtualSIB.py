#!/usr/bin/python

# requirements
from smart_m3.m3_kp import *
import socket
import sys
from termcolor import colored
from lib import SIBLib
from xml.etree import ElementTree as ET
from lib import SSAPLib

# constants
CONFIG_FILE = 'vsib_configuration.xml'
TCP_IP = '127.0.0.1'
TCP_PORT = 10010
BUFFER_SIZE = 1024

# main class
class VirtualSIB:
    
    def __init__(self, ip, port):
      
        # connection to the other SIBs
        self.connect_to_sibs()
            
        # initialization of the TCP socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((TCP_IP, TCP_PORT))
        self.s.listen(1)


    def connect_to_sibs(self):

        # read the configuration file to see the real SIBs
        tree = ET.parse(CONFIG_FILE)
        root = tree.getroot()
        
        # create and fill a dict to store the info about real SIBs
        rsib = {}
        for r in root.findall('SIB'):
            sib_name = r.find('name').text
            rsib[sib_name] = {}
            rsib[sib_name]["IP"] = r.find('IP').text
            rsib[sib_name]["port"] = int(r.find('port').text)
            rsib[sib_name]["type"] = r.find('type').text
            print colored("virtualSIB> ", "blue", attrs=["bold"]) + "Found a " + rsib[sib_name]["type"] + " sib with IP " + rsib[sib_name]["IP"] + " and port " + str(rsib[sib_name]["port"])
        
        # connection to the SIBs
        nodes = {}
        for r in rsib.keys():
            print colored("virtualSIB> ", "blue", attrs=["bold"]) + "Connecting to " + r
            nodes[r] = SIBLib.SibLib(rsib[r]["IP"], rsib[r]["port"])
            try:
                nodes[r].join_sib()
                rsib[r]["state"] = "online"
            except socket.error:
                print colored("virtualSIB> ", "red", attrs=["bold"]) + "SIB " + r + " is not online"
                rsib[r]["state"] = "offline"


    def react_to_message(self, xml, conn, addr):

        # data extraction
        root = ET.fromstring(xml)
        info = {}
        for child in root:
            info[child.tag] = child.text
    
        # printing informations
        print colored("VirtualSIB> ", "blue", attrs=["bold"]) + "Received " + info["transaction_type"] + " request from " + str(addr)

        # send a reply to the client
        if info["transaction_type"] == "JOIN":
            reply = SSAPLib.reply_to_join(None,
                                          info["node_id"], 
                                          info["space_id"],
                                          info["transaction_id"])
            print colored("virtualSIB> ", "blue", attrs=["bold"]) + str(addr) + " joined the virtual SIB"
    
        elif info["transaction_type"] == "LEAVE":
            reply = SSAPLib.reply_to_leave(None,
                                           info["node_id"], 
                                           info["space_id"],
                                           info["transaction_id"])
            print colored("virtualSIB> ", "red", attrs=["bold"]) + str(addr) + " left the virtual SIB"
            
        reply_msg = "".join(reply)
        conn.send(reply_msg)
