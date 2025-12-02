import logging, io

_log = logging.getLogger('bq.util.bqrender')

from lxml import etree


def elem_to_pesterfish(elem):
    """
    turns an elementtree-compatible object into a pesterfish dictionary
    (not json).

    """
    d=dict(tag=elem.tag)
    if elem.text:
        d['text']=elem.text
    if elem.attrib:
        d['attributes']=elem.attrib
    children=elem.getchildren()
    if children:
        d['children']=list(map(elem_to_pesterfish, children))
    if elem.tail:
        d['tail']=elem.tail
    return d


def render_bq(template_name, template_vars, **kwargs):
    # turn vars into an xml string.
    st = io.StringIO()
    root = etree.Element (template_name)

    def writeElem( obj, node):
        if isinstance( obj, dict ):
            for k in obj:
                # create element and recurse
                if isinstance( obj[k], list ):
                    # Add multiple elements. Each value should be a
                    #dictionary.
                    node = node.SubElement ('tag', name=k)
                    for val in obj[k]:
                        v = node.SubElement ('value')
                        v.text = val

                elif isinstance( obj[k], dict ):
                    # element
                    node = node.SubElement ('resource')
                else:
                    node = node.SubElement ('tag', name=k, value=str(obj[k]))

        elif isinstance( obj, list ):
            node = node.SubElement('resource')
            for val in obj:
                writeElem(val, node)
        else:
            st.write(str(obj))

    # main part of function
    try:
        node = etree.Element (template_name)
        if template_name in template_vars:
            writeElem(template_vars[template_name], node)
        return etree.tostring(node, encoding='unicode')
        _log.debug("render_bq %s", st.getvalue() )
    except Exception as ex:
        _log.exception("")
    return st.getvalue()
