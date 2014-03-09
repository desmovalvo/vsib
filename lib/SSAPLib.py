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
SSAP_BNODES_PARAM_TEMPLATE = '<parameter name = "bnodes"><urllist>%s</urllist></parameter>'

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

### The following method is used to send a confirmation
### to the INSERT request sent by the client
def reply_to_insert(self, node_id, space_id, transaction_id, write_enabled):

    # TODO: check if the bnodes field is always empty
    if write_enabled:
        reply = [SSAP_MESSAGE_TEMPLATE%(node_id, 
                                        space_id, 
                                        "INSERT",
                                        transaction_id,
                                        (SSAP_SUCCESS_PARAM_TEMPLATE%("m3:Success") + SSAP_BNODES_PARAM_TEMPLATE%("")))]
    else:
        # TODO: check what kind of response we should send
        pass

    return reply

