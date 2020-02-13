import time
from lxml.builder import ElementMaker
from lxml import etree

namespaces = {
    'SOAP' :  'http://schemas.xmlsoap.org/soap/envelope/',
    'samlp' : 'urn:oasis:names:tc:SAML:1.0:protocol',
    'samla' : 'urn:oasis:names:tc:SAML:1.0:assertion',
}

soap = ElementMaker(namespace='http://schemas.xmlsoap.org/soap/envelope/',
                    nsmap={'SOAP': 'http://schemas.xmlsoap.org/soap/envelope/'})
samlp = ElementMaker(namespace="urn:oasis:names:tc:SAML:1.0:protocol",
                     nsmap={'samlp' : "urn:oasis:names:tc:SAML:1.0:protocol"})


#  This file is based on information found at
#  https://wiki.jasig.org/display/CASUM/SAML+1.1
#

def create_soap_saml(ticket):
    'create a valid soap request for saml 1.1 based on the ticket delivered by cas'

    gmt = time.gmtime()
    env =  soap.Envelope(soap.Header(),
                         soap.Body(samlp.Request(samlp.AssertionArtifact(ticket),
                                               MinorVersion = '1',
                                               MajorVersion='1',
                                               RequestID='1',
                                               IssueInstant = time.strftime('%Y-%m-%dT%H:%M:%sZ', gmt)
                                               )
                                 )
                       )
    return etree.tostring(env, pretty_print=True)

def parse_soap_saml(xml):
    'parse response for validation and attributes'
    attributes = {}
    try:
        response = etree.XML(xml)
    except Exception:
        return attributes

    # Pull out username and attributes if available
    # Will be empty on failures
    user_name = response.xpath('//samla:NameIdentifier', namespaces=namespaces)
    if len(user_name):
        attributes['user_id'] = user_name[0].text

    for attr in response.xpath('//samla:Attribute', namespaces=namespaces):
        attributes[attr.get('AttributeName')] = attr[0].text

    return attributes




