#!/usr/bin/python

# requirements
from smart_m3.m3_kp import *
import socket
import sys
from termcolor import colored
from lib import SIBLib
from xml.etree import ElementTree as ET
import SSAPLib
import itertools

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
        self.rsib = {}
        for r in root.findall('SIB'):
            sib_name = r.find('name').text
            self.rsib[sib_name] = {}
            self.rsib[sib_name]["IP"] = r.find('IP').text
            self.rsib[sib_name]["port"] = int(r.find('port').text)
            self.rsib[sib_name]["type"] = r.find('type').text
            print colored("virtualSIB> ", "blue", attrs=["bold"]) + "Found a " + self.rsib[sib_name]["type"] + " sib with IP " + self.rsib[sib_name]["IP"] + " and port " + str(self.rsib[sib_name]["port"])
        
        # connection to the SIBs
        self.nodes = {}
        for r in self.rsib.keys():
            print colored("virtualSIB> ", "blue", attrs=["bold"]) + "Connecting to " + r
            self.nodes[r] = SIBLib.SibLib(self.rsib[r]["IP"], self.rsib[r]["port"])
            try:
                self.nodes[r].join_sib()
                self.rsib[r]["state"] = "online"
            except socket.error:
                print colored("virtualSIB> ", "red", attrs=["bold"]) + "SIB " + r + " is not online"
                self.rsib[r]["state"] = "offline"

    def react_to_message(self, xml, conn, addr):

        # data extraction
        root = ET.fromstring(xml)
        info = {}
        for child in root:
            if child.attrib.has_key("name"):
                k = child.tag + "_" + str(child.attrib["name"])
            else:
                k = child.tag
            info[k] = child.text
    
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

            if self.write_enabled:
                
                reply = SSAPLib.reply_to_insert(None,
                                                info["node_id"], 
                                                info["space_id"],
                                                info["transaction_id"],
                                                self.write_enabled)

                print colored("virtualSIB> ", "red", attrs=["bold"]) + "insertion is enabled but non yet implemented."

                # make the list of triples to insert
                triples={}
                for r in root.findall('parameter'):
                    if r.get("name")=="insert_graph":
                        for tl in r.findall('triple_list'):
                            triple_list = []
                            for t in tl.findall('triple'):
                                tsubject = t.find('subject').text
                                tpredicate = t.find('predicate').text
                                tobject = t.find('object').text
                                print "Triple to insert: < " + tsubject + "---" + tpredicate + "---" + tobject + " >"
                                                                
                                #costruisco la tripla e la metto nella lista delle triple da inserire nelle sib reali
                                triple_list.append(Triple(URI(tsubject),
                                                          URI(tpredicate),
                                                          URI(tobject)))

                # insert the triples into all the sibs
                for r in self.rsib.keys():
                    if self.rsib[r]["state"] == "online":
                        try:
                            self.nodes[r].insert(triple_list)
                        except socket.error:
                            print colored("virtualSIB> ", "red", attrs=["bold"]) + "SIB " + r + " is not online"
                            self.rsib[r]["state"] = "offline"
                            
                print colored("virtualSIB> ", "blue", attrs=["bold"]) + str(addr) + " inserted a triple in the virtual SIB"

            else:
                print colored("virtualSIB> ", "red", attrs=["bold"]) + str(addr) + " insertion is forbidden by the virtual SIB"  


        #######################################################
        #
        # QUERY
        #
        #######################################################
            
        elif info["transaction_type"] == "QUERY":

            if str(info["parameter_type"]) == "sparql":
                print colored("virtualSIB> ", "blue", attrs=["bold"]) + str(addr) + " sent the following SPARQL query:"
                print str(info["parameter_query"])

                # forwarding the query to the real SIBs
                results = []
                for r in self.nodes:
                    results.append(self.nodes[r].execute_query(info["parameter_query"])[0])

                # remove duplicates
                results = list(results for results,_ in itertools.groupby(results))
                print colored("virtualSIB> ", "blue", attrs=["bold"]) + "The query returned " + str(len(results)) + " results"

                # building a reply
                reply = SSAPLib.reply_to_query(None,
                                                info["node_id"], 
                                                info["space_id"],
                                                info["transaction_id"], results)

            elif str(info["parameter_type"]) == "RDF-M3":
                # TODO implement rdf query
                print colored("virtualSIB> ", "red", attrs=["bold"]) + str(addr) + " sent a rdf query, but they are not yet implemented."
                reply_msg = ""


        #######################################################
        #
        # DELETE
        #
        #######################################################
            
        elif info["transaction_type"] == "REMOVE":

            reply = SSAPLib.reply_to_remove(None,
                                            info["node_id"], 
                                            info["space_id"],
                                            info["transaction_id"])
            
            # make the list of triples to remove
            triples={}
            for r in root.findall('parameter'):
                if r.get("name")=="remove_graph":
                    for tl in r.findall('triple_list'):
                        triple_list = []
                        for t in tl.findall('triple'):
                            tsubject = t.find('subject').text
                            tpredicate = t.find('predicate').text
                            tobject = t.find('object').text
                            print "Triple to remove: < " + tsubject + "---" + tpredicate + "---" + tobject + " >"
                            
                            # lista delle triple da rimuovere dalle sib reali
                            triple_list.append(Triple(URI(tsubject),
                                                      URI(tpredicate),
                                                      URI(tobject)))

            # remove the triples from all the sibs
            for r in self.rsib.keys():
                if self.rsib[r]["state"] == "online":
                    try:
                        self.nodes[r].remove(triple_list)
                    except socket.error:
                        print colored("virtualSIB> ", "red", attrs=["bold"]) + "SIB " + r + " is not online"
                        self.rsib[r]["state"] = "offline"
                            

            print colored("virtualSIB> ", "blue", attrs=["bold"]) + str(addr) + " deleted a triple in the virtual SIB"

        reply_msg = "".join(reply)
        conn.send(reply_msg)
