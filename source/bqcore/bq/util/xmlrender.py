import logging, StringIO

_log = logging.getLogger('bq.util.xmlrender')

def render_xml(template_name, template_vars, **kwargs):
    # turn vars into an xml string.
    st = StringIO.StringIO()

    def writeElem( obj):
        if isinstance( obj, dict ):
            for k in obj:
                # create element and recurse
                if isinstance( obj[k], list ):
                    # Add multiple elements. Each value should be a
                    #dictionary.
                    for val in obj[k]:
                        st.write("<%s>" % k)
                        writeElem(val)
                        st.write("</%s>" % k)

                elif isinstance( obj[k], dict ):
                    # element
                    st.write("<%s>" % k)
                    writeElem(obj[k])
                    st.write("</%s>" % k)

                else:
                    st.write("<%s>" % k)
                    st.write(str(obj[k]))
                    st.write("</%s>" % k)

        elif isinstance( obj, list ):
            for val in obj:
                writeElem(val)
        else:
            st.write(str(obj))

    # main part of function
    try:
        st.write("<%s>" % template_name)
        if template_vars.has_key(template_name):
            writeElem(template_vars[template_name])
        st.write("</%s>" % template_name)
        _log.debug("render_xml %s", st.getvalue() )
    except Exception,ex:
        _log.exception("")
    return st.getvalue()
