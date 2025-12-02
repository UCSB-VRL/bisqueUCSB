:mod:`webhelpers.containers`
================================================

.. automodule:: webhelpers.containers

.. currentmodule:: webhelpers.containers

Classes
-------

.. autoclass:: Counter
   :members:

.. autoclass:: Accumulator
   :members:

.. autoclass:: UniqueAccumulator
   :members:

.. class:: defaultdict(missing_func)

   A dict that automatically creates values for missing keys. This is the same
   as ``collections.defaultdict`` in the Python standard library. It's provided
   here for Python 2.4, which doesn't have that class.

   When you try to read a key that's missing, I call ``missing_func`` without
   args to create a value. The result is inserted into the dict and returned.
   Many Python type constructors can be used as ``missing_func``.  Passing
   ``list`` or ``set`` creates an empty dict or set.  Passing ``int`` creates
   the integer ``0``.  These are useful in the following ways::

       >> d = defaultdict(list);  d[ANYTHING].append(SOMEVALUE)
       >> d = defaultdict(set);  d[ANYTHING].include(SOMEVALUE)
       >> d = defaultdict(int);  d[ANYTHING] += 1

.. autoclass:: DumbObject

Functions
---------
.. autofunction:: correlate_dicts
.. autofunction:: correlate_objects
.. autofunction:: del_quiet
.. autofunction:: distribute
.. autofunction:: except_keys
.. autofunction:: extract_keys
.. autofunction:: only_some_keys
.. autofunction:: ordered_items
.. autofunction:: get_many
.. autofunction:: transpose
.. autofunction:: unique

