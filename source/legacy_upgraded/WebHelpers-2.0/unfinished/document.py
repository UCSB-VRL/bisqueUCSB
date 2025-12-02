class HTMLDocument(object):
    def __init__(self, body, head=None, doctype=None,
        html_attrs=None, head_attrs=None, body_attrs=None,
        encoding=None, lang=None, title=None, xml_version="1.0"):
        self.body = body
        self.head = head or ""
        self.doctype = doctype
        self.html_attrs = self._get_dict(html_attrs)
        self.head_attrs = self._get_dict(head_attrs)
        self.body_attrs = self._get_dict(body_attrs)
        self.encoding = encoding
        self.lang = lang
        self.title = title
        self.xml_version = xml_version

    def html5(self):
        doctype = self.doctype or Doctype().html5()

    def html5_xml(self):
        xml_declaration = tags.xml_declaration(self.xml_version, self.encoding)

    def xhtml1(self):
        doctype = self.doctype or Doctype().xhtml1()
        xml_declaration = tags.xml_declaration(self.xml_version, self.encoding)

    def html4(self):
        doctype = self.doctype or Doctype().html4()

    # XXX Allow subclassing for custom heads. Refactor into superclass with
    # get_head method?

    #### Private methods
    def _get_dict(self, dic):
        if dic is None:
            return {}
        return dic.copy()

    is_xml = bool(xml_version)
    if lang:
        html_attrs.setdefault("lang", lang)
        if is_xml:
            html_attrs.setdefault("xmlns", "http://www.w3.org/1999/xhtml")
    body = HTML.body(body, _nl=True, **body_attrs)
    html = HTML(doctype, "\n", head, body, **html_attrs)
    if is_xml:
        html = HTML(tags.xml_declaration(xml_version, encoding), "\n", html)
    return html

