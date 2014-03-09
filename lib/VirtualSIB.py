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
BUFFER_SIZE = 1024

# main class
class VirtualSIB:
    
    def __init__(self, ip, port, write_enabled):
      
        # reading parameters
        self.tcp_ip = ip
        self.tcp_port = port
        self.write_enabled = write_enabled

        # joined KPs
        self.kps = {}

        # connection to the other SIBs
        self.connect_to_sibs()
            
        # initialization of the TCP socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.tcp_ip, self.tcp_port))
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

        #######################################################
        #
        # JOIN
        #
        #######################################################

        # send a reply to the client
        if info["transaction_type"] == "JOIN":
            # building a reply
            reply = SSAPLib.reply_to_join(None,
                                          info["node_id"], 
                                          info["space_id"],
                                          info["transaction_id"])        

            # adding the client to a dict
            if self.kps.has_key(info["node_id"]):

                # printing debug informations
                print colored("virtualSIB> ", "red", attrs=["bold"]) + str(addr) + " already joined the virtual SIB"

            else:
                
                # adding the client to a dict
                self.kps[info["node_id"]] = {}
                self.kps[info["node_id"]]["IP"] = addr[0]
                self.kps[info["node_id"]]["port"] = addr[1]

        #######################################################
        #
        # LEAVE
        #
        #######################################################

        elif info["transaction_type"] == "LEAVE":

            # check if the client is connected 
            if self.kps.has_key(info["node_id"]):
                
                # forge a reply
                reply = SSAPLib.reply_to_leave(None,
                                               info["node_id"], 
                                               info["space_id"],
                                               info["transaction_id"])
                
                # print debug informations
                print colored("virtualSIB> ", "red", attrs=["bold"]) + str(addr) + " left the virtual SIB"

                # remove the kps
                del self.kps[info["node_id"]]

            else:

                # print debug informations
                print colored("virtualSIB> ", "red", attrs=["bold"]) + str(addr) + " requested to leave the virtual SIB, but is not connected"

                # TODO: how should we respond?
                # At the moment we send the same response
                reply = SSAPLib.reply_to_leave(None,
                                               info["node_id"], 
                                               info["space_id"],
                                               info["transaction_id"])

        #######################################################
        #
        # INSERT
        #
        #######################################################
            
        elif info["transaction_type"] == "INSERT":

            # TODO: read information about the data inserted
            # TODO: check whether insertion is forbidden
            if WRITE_ENABLED:
                
                reply = SSAPLib.reply_to_insert(None,
                                                info["node_id"], 
                                                info["space_id"],
                                                info["transaction_id"])

                # TODO: insertion on the real SIBs
#                print colored("virtualSIB> ", "blue", attrs=["bold"]) + str(addr) + " inserted a triple in the virtual SIB"
                print colored("virtualSIB> ", "red", attrs=["bold"]) + "insertion is enabled but non yet implemented."

            else:
                print colored("virtualSIB> ", "red", attrs=["bold"]) + str(addr) + " insertion is forbidden by the virtual SIB"  

            
        reply_msg = "".join(reply)
        conn.send(reply_msg)
