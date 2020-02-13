BisQue Matlab API

This API is a thin layer over Java XML DOM simplifying BisQue document reading, creation, 
authentication and communication.

Repository contents

/        - root contains simple examples and test cases for various classes of the library
+bim     - contains an OME-TIFF writer used to communicate N-D image bytes to the system
+bq      - contains the Matlab API
examples - contains more elaborate examples demonstrating some image processing uses


Note

The logic of the API is very simple and it chooses efficiency. The very important note is 
that objects created from XML do not guarantee perfect synchronisation with the state in 
the database. For example, if a new resource is created in the API and saved into the database 
it's not re-fetched and updated. If a user needs the object to reflect the latest state, the 
object must be explicitly re-fetched. The major implication of this is that if a large object
is created and stored and then stored again one will observe duplication of sub-elements in 
that resource.
