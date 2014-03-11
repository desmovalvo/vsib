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

### Templates used to build query results
SSAP_RESULTS_PARAM_TEMPLATE = """
<parameter name="status">m3:Success</parameter>
<parameter name="results">
<sparql xmlns="http://www.w3.org/2005/sparql-results#">    
%s
</sparql>
</parameter>
"""

SSAP_HEAD_TEMPLATE = """<head>
%s</head>"""

SSAP_VARIABLE_TEMPLATE = """<variable name="%s"/>
"""

SSAP_RESULTS_TEMPLATE = """<results>
%s</results>
"""

SSAP_RESULT_TEMPLATE = """<result>
%s</result>
"""

SSAP_BINDING_TEMPLATE = """<binding name="%s"><uri>%s</uri>
</binding>
"""


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

### The following method is used to send a confirmation
### to the QUERY request sent by the client
def reply_to_query(self, node_id, space_id, transaction_id, results):

    print results

    # building HEAD part of the query results
    variable_list = []
    for triple in results:
        for element in triple:    
            if not SSAP_VARIABLE_TEMPLATE%(str(element[0])) in variable_list:
                variable_list.append(SSAP_VARIABLE_TEMPLATE%(str(element[0])))
    head = SSAP_HEAD_TEMPLATE%(''.join(variable_list))
    
    # building RESULTS part of the query results
    result_string = ""
    for triple in results:
        binding_string = ""
        for element in triple:    
            binding_string = binding_string + SSAP_BINDING_TEMPLATE%(element[0], element[2])
        result_string = result_string + SSAP_RESULT_TEMPLATE%(binding_string)
    results_string = SSAP_RESULTS_TEMPLATE%(result_string)
    body = SSAP_RESULTS_PARAM_TEMPLATE%(head + results_string)

    # finalizing the reply
    reply = [SSAP_MESSAGE_TEMPLATE%(node_id, 
                                    space_id, 
                                    "QUERY",
                                    transaction_id,
                                    body)]
    return reply


### The following method is used to send a confirmation
### to the REMOVE request sent by the client
def reply_to_remove(self, node_id, space_id, transaction_id):
    reply = [SSAP_MESSAGE_TEMPLATE%(node_id,
                                    space_id,
                                    "REMOVE",
                                    transaction_id,
                                    (SSAP_SUCCESS_PARAM_TEMPLATE%("m3:Success")))]

    return reply
