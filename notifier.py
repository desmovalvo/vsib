import sys
import uuid
from termcolor import colored
from xml.etree import ElementTree as ET
from lib import SIBLib
from socket import * 

# constants
CONFIG_FILE = 'register.xml'
BUFFER_SIZE = 2048


# SSAP Register request template
SSAP_REGISTER_REQUEST_TEMPLATE = '''
<SSAP_message>
<transaction_type>REGISTER</transaction_type>
<message_type>REQUEST</message_type>
<transaction_id>%s</transaction_id>
<node_id>%s</node_id>	
<space_id>X</space_id>
</SSAP_message>'''

# SSAP Register request template
SSAP_REGISTER_CONFIRM_TEMPLATE = '''
<SSAP_message>
<node_id>%s</node_id>	
<space_id>X</space_id>
<transaction_type>REGISTER</transaction_type>
<message_type>CONFIRM</message_type>
<transaction_id>%s</transaction_id>
<parameter name="status">m3:Success</parameter>
</SSAP_message>'''

class Notifier():
    
    def __init__(self, sib_ip, sib_port):
        self.node_id = str(uuid.uuid4())
        self.transaction_id = 0
        self.sib_ip = sib_ip
        self.sib_port = sib_port

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
            print colored("Notifier > ", "blue", attrs=["bold"]) + "[" + sib_name + "]" + " with IP " + self.vsib[sib_name]["IP"] + " and port " + str(self.vsib[sib_name]["port"])
            i += 1
            
        # selection of a SIB
        sib = raw_input("Select a SIB > ")
        
        if self.vsib.has_key(sib) == False:
            print colored("Notifier > ", "blue", attrs=["bold"]) + "Don't exsists a virtual sib with id " + str(sib)

        else:

            # avvio la connessione con la virtual sib scelta
            # create a tcp socket 
            self.s_vsib = socket(AF_INET, SOCK_STREAM)
            self.s_vsib.bind(("127.0.0.1", 8010))
                    
            # connect to the virtual sib server             
            self.s_vsib.connect((self.vsib[sib]["IP"], self.vsib[sib]["port"]))
    
            # gli invio il messaggio SSAP REGISTER
            msg_reg = SSAP_REGISTER_REQUEST_TEMPLATE%(self.transaction_id, self.node_id)
            self.s_vsib.send(msg_reg)
            
            # TODO: controllare che arrivi il messaggio di conferma register
            response = self.s_vsib.recv(BUFFER_SIZE)
            check = self.check_msg(response)
            
            if check:
                # TODO: creare un metodo che si metta in ascolto sulla socket in attesa di messaggi                
                self.listening()


    def check_msg(self, response):
        # data extraction
        root = ET.fromstring(response)
        info = {}
        for child in root:
            k = child.tag
            info[k] = child.text
        
        if (info["message_type"] == "CONFIRM") & (info["node_id"] == str(self.node_id)) & (info["transaction_type"] == "REGISTER") & (info["parameter"] == "m3:Success"):
            print colored("Notifier > ", "blue", attrs=["bold"]) + "Received confirm message!"
            print response
        
        #self.s_vsib.close()

    def listening():
        print "In attesa di messaggi di insert/remove/query/subscription da parte di un KP..."
        # infinite loop
        while 1:

            try:
                # accept connections
                #self.s_vsib.listen(1)

                # accept incoming informations
                #conn, addr = self.s_vsib.accept()
                #print colored("Notifier> ", "blue", attrs=["bold"]) + 'Incoming connection address from ' + str(addr)
                
                # parse received message
                data = self.s_vsib.recv(BUFFER_SIZE)
                if not data: break    
                
                print data
                
            except KeyboardInterrupt:
                sys.exit(0)

