Development
===========

WebHelpers development is coordinated on the 
`pylons-discuss <http://groups.google.com/pylons-discuss>`_ list.  Proposals
for new helpers and offers to help with coding or documentation are always
welcome.  Please post any bug reports or outlines for new helpers to the
`bug tracker <http://bitbucket.org/bbangert/webhelpers/issues>`_.

New helpers are considered if they conform to the following criteria:

* Is it useful in a wide variety of applications, especially web applications?

* Does it avoid dependencies outside the Python standard library, especially
  C extensions which are hard to install on Windows and Macintosh?

* Is it too small to be released as its own project, and is there no other
  Python project more appropriate for it?

* Does it work on all Python versions from 2.4 to the latest 2.x? 
  (Python 3 is not yet supported.)

* A small number of Pylons-specific helpers are accepted for the
  ``webhelpers.pylonslib`` package. These are ones that offer significant
  advantages over framework-neutral implementations, are too peripheral for the
  Pylons core, and are too widely useful to exclude. The docstring should
  explain how to port it to another web framework.
