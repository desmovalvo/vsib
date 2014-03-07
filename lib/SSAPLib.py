#!/usr/bin/python

SSAP_MESSAGE_TEMPLATE = '''
<SSAP_message>
<node_id>%s</node_id>
<space_id>%s</space_id>
<transaction_type>%s</transaction_type>
<message_type>CONFIRM</message_type>
<transaction_id>%s</transaction_id>
%s
</SSAP_message>'''

SSAP_SUCCESS_PARAM_TEMPLATE = '<parameter name = "status">%s</parameter>'


### The following method is used to send a confirmation
### to the JOIN request sent by the client
def reply_to_join(self, node_id, space_id, transaction_id):
    reply = [SSAP_MESSAGE_TEMPLATE%(node_id, 
                                    space_id, 
                                    "JOIN",
                                    transaction_id,
                                    SSAP_SUCCESS_PARAM_TEMPLATE%("m3:Success"))]
    return reply


### The following method is used to send a confirmation
### to the JOIN request sent by the client
def reply_to_leave(self, node_id, space_id, transaction_id):
    reply = [SSAP_MESSAGE_TEMPLATE%(node_id, 
                                    space_id, 
                                    "LEAVE",
                                    transaction_id,
                                    SSAP_SUCCESS_PARAM_TEMPLATE%("m3:Success"))]
    return reply

