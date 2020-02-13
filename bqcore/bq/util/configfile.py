#!/usr/bin/env python
"""Allows line editing of simple config file that are .ini style
"""

import os
import re
import StringIO
import string

# Bracketed name i.e. [section]
section_re = re.compile (r'^\[(.*)\]')
# Remove # comments exception those that are in "  chracters
line_re = re.compile (r'#(?=(?:[^"]*"[^"]*")*[^"]*$).*', re.MULTILINE)

GLOBAL_SECTION="__GLOBAL__"

class peekable(object):
    def __init__(self, it):
        self.iter = it
        self.buffer = []
    def __iter__(self):
        return self
    def next(self):
        if self.buffer:
            return self.buffer.pop(0)
        else:
            return self.iter.next()
    def peek(self, n, default=None):
        while n >= len(self.buffer):
            try:
                self.buffer.append(self.iter.next())
            except StopIteration:
                return default
        return self.buffer[n]

def filterfluff(lines):
    '''Remove empty lines and comments'''
    if isinstance(lines, str):
        lines = lines.splitlines()
    lines = peekable (iter(lines))
    for  l in lines:
        #line, sep, comment = l.partition ('#')
        line = line_re.sub('', l)
        while line.endswith("\\"):
            line = line[:-1] + line_re.sub ('', lines.next())
        while lines.peek(0, '').startswith( (' ', '\t') ):
            line = line[:] + line_re.sub ('', lines.next())
        line = line.strip()
        if line:
            yield line

class ConfigFile(object):
    """Allows editing of simple config file that are .ini style

    Parses simple config file (.ini style) and maintains
    ordered lines for editing.
    """

    def __init__(self, config = None, **kw):
        """Create and editor and read the option config

        @type config: string or file-like object
        @param config: The name of the file or a file-like object
        """
        # Keep the sections ordered
        self.section_order = [ GLOBAL_SECTION ]
        # Each section in the hash is a list of single lines..
        self.sections = { GLOBAL_SECTION : [] }
        self.options = kw
        if isinstance(config, basestring) and os.path.exists(config):
            config = open(config)
        if hasattr(config, 'read'):
            self.read (config)
            config.close()

    def read(self, f):
        """Reads .ini file, remembering the section order"""
        section = self.sections.get (GLOBAL_SECTION)
        for l in f:
            m =  section_re.match (l)
            if m:
                name = m.group(1)
                section = self.sections.setdefault (name, [])
                self.section_order.append (name)
                continue
            section.append (l)


    def edit_config (self, section, key, line, env = None, append=True):
        """Edit a single config file entry

        @param section: required section title. It will be created if required
        @param key:  The entry key i.e. the key in key = value
        @param line: The enture replacement line i.e. 'key = value'
        @param env: None or A dictionary of possible variables in the line. For example
        if the line root=%(local_path), then the env = { 'local_path' : '/home/' }
        """
        if line is not None and env is not None:
            for k,v in env.items():
                line = line.replace ("%%(%s)" % k, v)

        if not section:
            section = GLOBAL_SECTION
        sections = section.split (',')
        if sections == ['*']:
            sections = self.sections.keys()

        for section in sections:
            # Find the sections
            s = self.sections.get (section, None)
            if s is None:
                # new section
                if line is not None:
                    self.section_order.append(section)
                    self.sections[section] = [ line ]
                return
            # append a line to section if no key
            if key is None:
                self.sections[section].append(line)
                return

            # Search sections for key
            n = []
            found = False
            for l in s:
                # Skip continuation lines and comments
                if l.startswith((' ', '\t' )):
                    #n.append(l)
                    continue
                # match the key looked for
                k,p,v = l.partition('=')
                if (k.strip() == key    # Match lines
                    or (k.strip('#').strip() == key) and not any (ll.startswith(key) for ll in s)) :  # OR commented lines
                    if line is not None:
                        n.append(line)
                    found = True
                    continue
                # append all other lines
                n.append (l)
            # At end of section
            if not found and append:
                if line is not None:
                    n.append (line)
            self.sections[section] = n

    def edit_update (self, section, dic, env=None):
        """Update the section given the key value pairs of a dictionary
        @type section: string
        @param section: The section name or None
        @type dic:  dict
        @param dic: A dictionary of values to be inserted into the section
        """
        items = dict(dic)
        lines = self.get (section)
        for l in lines:
            k,p,ov = [ x.strip() for x in l.partition('=') ]
            if p and k in items:
                rv = string.Template(ov).safe_substitute(items)
                nv = items.pop(k)
                if rv != ov:
                    nv = rv
                # !v?'k':'v=k'
                #line = not v and str(k) or "=".join([str(k),str(v)])
                line = "=".join([str(k),str(nv)]) if nv else str(k)
                self.edit_config(section, k, line, env)
        for k,v in items.items():
            line = "=".join([str(k),str(v)]) if v else str(k)
            self.edit_config(section, k, line, env)

    def get (self, section, key=None, asdict = False, filterlines = True):
        """Retrieve the lines or a keyed valued of a section,
        Find the value of some key
        """
        if not section:
            section = GLOBAL_SECTION

        s = self.sections.get (section, [])
        if filterlines:
            s =filterfluff(s)
        if key is None and asdict is False:
            return list(s)
        s =dict([(x[0].strip(), x[2].strip(' \'\"'))
                 for x in [a.partition('=') for a in s]])
        if  key is None:
            return s

        return s.get (key, None)

    def section_names(self):
        return list(self.section_order)

    def update_values (self, section, dic):
        """Given a dict of known keys, extract from the
        given section the associated values
        """
        for key in dic.keys():
            v = self.get( section, key)
            #print 'key: [%s] value: [%s]'%(str(key), str(v))
            if v is not None:
                dic[key] = v
        return dic


    def write(self, f):
        """Write the .ini file out in section order

        @type f: a string or file-like object
        @param f: Name or file to write to
        """
        if isinstance(f, basestring):
            f = open(f, 'wb')
        for section in self.section_order:
            if section != GLOBAL_SECTION:
                f.write ("[%s]\n" % section)
            s = self.sections[section]
            s = "\n".join ( [ l.strip('\n') for l in s ] )
            #s = "\n".join ( s )
            f.write (s)
            f.write ("\n")

    def __str__(self):
        s = StringIO.StringIO()
        self.write (s)
        return s.getvalue()








configfile = """
[basic]
option1 = 1
option2 = http://aaaa

# Comment
[advanced]
options1 = 2

"""


def test_edit():
    f = StringIO.StringIO (configfile)
    c = ConfigFile()
    c.read (f)
    print "------ read i the following ----- "
    print c
    print "------ edit the following ----- "
    c.edit_config ('advanced', 'options1', 'options1 = 1', {})
    print c


    print "------ edit the following ----- "
    c.edit_config ('advanced', 'options3', 'options3 = 2', {})
    c.edit_config ('test', 'options1', 'options1 = 2', {})
    print c
