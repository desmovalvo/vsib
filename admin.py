#!/usr/bin/env python

# XML parser
from lxml import etree as ET
#from xml.etree import ElementTree as ET
#from xml.etree.ElementTree import Element

operation = raw_input("Action > ")

if (operation == "delete") | (operation == "2"):
    ############# deleting a sib #####################
    sib_name = raw_input("Insert sib name > ")
    # read the configuration file to see the real SIBs
    tree = ET.parse('vsib_configuration.xml')
    root = tree.getroot()
    found = False
    for sib in root.findall('SIB'):
        rank = sib.find('name').text
        if rank == sib_name:
            root.remove(sib)
            found = True
    if found == False:
        print sib_name + " don't exists!!"
    else:
        tree.write('vsib_configuration.xml')
        print sib_name + " deleted!"
    
elif (operation == "insert") | (operation == "1"):
    sib_name = raw_input("Insert sib name > ")
    sib_ip = raw_input("Insert sib IP > ")
    sib_port = raw_input("Insert sib port > ")
    sib_type = raw_input("Insert sib type > ")

    # read the configuration file to see the real SIBs
    parser = ET.XMLParser(remove_blank_text = True)
    tree = ET.parse('vsib_configuration.xml', parser)
    root = tree.getroot()

    sib = ET.Element('SIB')
    name = ET.SubElement(sib, 'name')
    name.text = sib_name
    ip = ET.SubElement(sib, 'IP')
    ip.text = sib_ip
    port = ET.SubElement(sib, 'port')
    port.text = sib_port
    s_type = ET.SubElement(sib, 'type')
    s_type.text = sib_type
    root.insert(0, sib)
    
    print(ET.tostring(root,pretty_print=True))
    tree.write('vsib_configuration.xml', pretty_print=True)




