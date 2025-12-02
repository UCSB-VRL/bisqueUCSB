import logging, io

_log = logging.getLogger('bq.util.xmlrender')

def render_xml(template_name, template_vars, **kwargs):
    # turn vars into an xml string.
    st = io.StringIO()

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
        if template_name in template_vars:
            writeElem(template_vars[template_name])
        st.write("</%s>" % template_name)
        _log.debug("render_xml %s", st.getvalue() )
    except Exception as ex:
        _log.exception("")
    return st.getvalue()
