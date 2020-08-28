

from lxml import etree

def xmlmerge(sources):
    '''Merge a set of documents
    '''
    response = etree.Element('response')

    for xml in sources:
        for item in xml:
            response.append(item)
    return response


def xmlmerge1(sources, resource_type, **kw):
    '''Merge a set of documents
    '''
    for src in sources:
        response = src.query (resource_type, **kw)
        for item in response: 
            yield item


def xmljoin(sources, **join_attributes):
    '''Join a set of XML documents.  '''
    return sources

    
