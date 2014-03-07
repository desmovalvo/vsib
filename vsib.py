#!/usr/bin/env python

# requirements
from smart_m3.m3_kp import *
import socket
import sys
from termcolor import colored
from lib import SIBLib
from xml.etree import ElementTree as ET
from lib import SSAPLib
from lib import VirtualSIB

# constants
CONFIG_FILE = 'vsib_configuration.xml'
TCP_IP = '127.0.0.1'
TCP_PORT = 10010
BUFFER_SIZE = 1024

vsib = VirtualSIB.VirtualSIB(TCP_IP, TCP_PORT)

# infinite loop
while 1:

    try:
        # accept incoming informations
        conn, addr = vsib.s.accept()
        print colored("virtualSIB> ", "blue", attrs=["bold"]) + 'Incoming connection address from ' + str(addr)

        # parse received message
        data = conn.recv(BUFFER_SIZE)
        if not data: break    
        vsib.react_to_message(data, conn, addr)
       
    except KeyboardInterrupt:
        sys.exit(0)
