#
# Simple test of tostring iterator

from lxml import etree

def tostring_iter(root):
    '''iterator for lxml.etree.tostring  function'''
    yield head(root)
    for n in root:
        for cn in  tostring_iter(n):
            yield cn
    if len(root):
        yield tail(root)
    return


def head(node):
    attributes =''
    if node.attrib:
        attributes = ' '.join(['']+['%s="%s"' %(x,y) for x,y in node.items() ])
    if len(node):
        return "<%s%s>" % (node.tag, attributes)
    return "<%s%s/>" % (node.tag, attributes)

def tail(node):
    return "<%s/>" % node.tag


if __name__ == '__main__':
    r = etree.XML('<x a="1" b="2"><i/><i/><y/></x>')
    for p in tostring_iter(r):
        print p





