
1.  How to write a module:


    Module for bisquik can be written in any language.  Currently
included are python, matlab, and C++


2. Creating a module


  See INTERFACE..


2.1 Creating a module definition


 Modules are declared using an XML definition file. 

 The file defines:
  1. The module name.
  2. Where the code can be found.
  3. The type of interpreter to use to run the code
  4. The list input parameters
  5. The 'declared' list of output results

 An example file might look like:

 <module name="my_module" codeurl="./MyModule.py" type="python">
    <tag name="formal-input"  value="count" >
 </module>

2.2 Declaring parameters and results

   Parameters are declared as tag using a special syntax
   input parameters (parameters passed to the main routine)
   are declared with:

    <tag name="formal-input" value="p1:string='aaaa'" index="0" >
    
   The name attribute of "formal-input" declares an
   input parameter, the value give the parameter and name of 
   "p1" of type string and the index attribute say that it 
   is in position 1 of the argument list.

   We could also have simply declared the parameter as follows

    <tag name="formal-input" value="p1:number='5'" >


2.2.1  Parameter names

       Name can be any string, but should be valid identifiers
   in the programming language.  For example, in python
   the names are used to pass the parameters as named parameters.
   Given an actual input for the above parameter, it would be passed
    as
    main (p1="...")


     
  

2.2.2  Parameter and return types

   Parameter and return types are declared using ':' type-name
   The type-name can be used by client software to enforce
   rules about the input or provide easier input selection.

   The basic type-name are:

    1. string
    2. number
    3. image
    4. tag 
    5. gobject
    6. dataset

   type-name of image, tag and gobject may be used by the user interface
  to allow the user to select the proper objects.  All values are
  delivered to the module as string
   


2.2.1 Using special variable names

     The following is a list special named variable.  These variables
  will be filled in by the system before the module is run

     1. $image_url     : the currently selected image (as url)
     2. $dataset_url   : the currently selected dataset
     3. $gobjects      : active gobjects on the image (string of XML)
     4. $data_server   : The data server url 
     5. $module_server :
     6. $image_server  :
     7. $client_server : 

3. Testing a module

4. Installing a module

  New modules are placed in the project module directory
for automatic registration.




