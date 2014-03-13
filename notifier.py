import sys
import uuid
from termcolor import colored
from xml.etree import ElementTree as ET
from lib import SIBLib
from socket import * 

# constants
CONFIG_FILE = 'register.xml'

# SSAP Register request template
SSAP_REGISTER_REQUEST_TEMPLATE = '''
<SSAP_message>
<transaction_type>REGISTER</transaction_type>
<message_type>REQUEST</message_type>
<transaction_id>%s</transaction_id>
<node_id>%s</node_id>	
<space_id>X</space_id>
</SSAP_message>'''

class Notifier():
    
    def __init__(self, sib_ip, sib_port):
        self.node_id = str(uuid.uuid4())
        self.transaction_id = 0

        pass

    def register(self):

        # vedo a quali SIB virtuali posso registrarmi con la mia SIB 
        tree = ET.parse(CONFIG_FILE)
        root = tree.getroot()
        
        # create and fill a dict to store the info about virtual SIBs
        self.vsib = {}
        i = 1
        for v in root.findall('SIB'):
            sib_name = v.find('name').text
            self.vsib[sib_name] = {}
            self.vsib[sib_name]["IP"] = v.find('IP').text
            self.vsib[sib_name]["port"] = int(v.find('port').text)
            self.vsib[sib_name]["id"] = i
            print colored("Notifier > ", "blue", attrs=["bold"]) + "[" + str(i) + "] " + sib_name + " with IP " + self.vsib[sib_name]["IP"] + " and port " + str(self.vsib[sib_name]["port"])
            i += 1

        sib = raw_input("Select a SIB > ")

        found = False
        for v in self.vsib.keys():
            if int(sib) == int( self.vsib[v]["id"]):
                found = True
                self.sib_name = v
                break

        if found == False:
            print colored("Notifier > ", "blue", attrs=["bold"]) + "Don't exsists a virtual sib with id " + str(sib)

        else:
            # avvio la connessione con la virtual sib scelta
            # create a tcp socket 
            s = socket(AF_INET, SOCK_STREAM)
            
            # connect to the virtual sib server 
            s.connect((self.vsib[sib_name]["IP"], self.vsib[sib_name]["port"]))
    
            # gli invio il messaggio SSAP REGISTER
            msg_reg = SSAP_REGISTER_REQUEST_TEMPLATE%(self.transaction_id, self.node_id)
            print str(msg_reg)
            s.send(msg_reg)
