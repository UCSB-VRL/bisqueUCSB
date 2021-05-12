# MODULE DEVELOPMENT

> BisQue Modules are analysis extensions to the bisque system that allow users to incorporate their own custom analysis scripts written in `Python, C++, Java, MATLAB, etc.` that perform high-end computations such as deep learning based methods for use by the system and others. 

One of the main reasons to convert your source code into a BisQue module is for reproducibility. Researchers in the field have exceptional work, but poor coding practices hinders the widespread adoption and justification of their findings. This is by no means their fault, but luckily help is here. 


![__Module Files.__ There are six files that are needed for a module to be built and deployed on the BisQue platform. ](images/moduleexplanation.svg)


### __How to Begin Building Modules__ {-}

#### __STEP 1.__ Source Code Prep {-}

__[Source Code](#source-code)__

Building modules requires, of course, source code. Your first order of business is to upload your code to GitHub so you have a copy of your entire codebase in the event `rm -rf *` happens. Next, verify that your source code and `README` are clear enough for someone to run and understand. _Do not skip this step_. I have provided an [example `README` here](https://github.com/UCSB-VRL/bisqueUCSB/blob/master/example_README.md) to help you get started. You solved a problem, now share the solution!

Once you have working source code that others have tested to make sure it runs, you can begin the process of building your very own BisQue module. 

#### STEP 2.  Fill Out the Module XML {-}

__[Module XML](#module-xml)__

This file should tell the user what to input. For example, if your module segments pictures of cats and dogs, you should probably have something like this:
```xml
<tag name="accepted_type" value="image" />
```
Similarly, you should define your output to be what you are outputting. For example, if the output is a segmented image of a dog, you should have something like this:
```xml
<tag name="Segmentation" type="image">
```
The main purpose of the XML is to put your focus on filling out relevant information instead of learning `HTML`. BisQue uses the information in the XML to build the user interface for your module so you don't have to.

#### STEP 3.  Write the Dockerfile {-}

__[Dockerfile](#dockerfile)__

Probably the most important part to your module---the `Dockerfile`. Feel free to use example Dockerfiles from the community to get started. The main tasks you need to do are define your working directory as `module` and COPY all the necessary files needed to run your source code:
```sh 
WORKDIR /module
COPY predict_strength.py /module/
#  COPY ./source /module/source   <--- If you have a source folder
```

There is plenty to do while creating and building the Dockerfile so please read the full description carefully. The best tip we can give you is try to replicate your current setup where your code ran successfully. If you are using Ubuntu 16.04, define that as your base image and continue to build your Dockerfile from there. Now, do not go crazy and add every pip install package you have on your system. Remember, keep your container as light as possible. Only install the necessary packages needed for your source code to run in the container. 

#### STEP 4.  Modify the Python Script Wrapper {-}

__[Python Script Wrapper](#python-script-wrapper)__

Similar to how you would run your source code locally, the `PythonScriptWrapper.py` will help communicate the input from and output to BisQue. The main change to make is what file does the module need to run for the analysis. For instance, let's say I have a `predict_strength.py` file with a `predict` function that will do everything. Then I would simply import the file and modify the outputs variable to be:
```python
outputs = predict( bq, log, **self.options.__dict__ )
```

Feel free to add any logging and catches you wish while diagnosing your module. This script will be your main point of contact when attempting to pinpoint missing files and dependencies, Python related issues, and many more. Look for the `PythonScript.log` file when testing your module.


#### STEP 5.  Modify the Runtime Config File {-}

__[Runtime Module Configuration](#runtime-module-configuration)__

Give a name to the module docker container. The other arguments can be left alone. Use this as a means to control versioning. For instance, 
```sh
docker.image = cellseg-3dunet-v2  #  --->  cellseg-3dunet-v{}
```








## Dockerfile 

> __FILENAME: __ `Dockerfile` This file will be used for the docker build process so try to keep the default naming convention. 

#### Defining a Base Image {-}

Typically, a `Dockerfile` will include a base image such as `FROM ubuntu:xenial` at the top of the file. We highly recommend using the Ubuntu Xenial 16.04 image for your module as it has been tested rigorously and is the base image we use for BisQue. 

__NOTE.__ If you would like to use a different Ubuntu flavor like 18.04 Bionic, we encourage you to do so and let us know of any problems you encounter. 

We typically start off our module Dockerfiles with the following lines:

```sh
FROM ubuntu:xenial
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get -y update   && \
    apt-get -y upgrade  && \
    apt-get -y install python
```

#### APT-GET Installs {-}

After these lines, we need to add dependencies for our module such as pip, headers, and any compilers. The next few lines are where we put any `apt-get` installs. Usually this is good practice since some pip install packages require a compiler. If one is not present in the container, it might be hard to debug what is missing.

```sh
RUN apt-get -y install python-pip liblapack3 libblas-dev liblapack-dev gfortran
RUN apt-get update   # <--- Run before pip installs
```

#### PIP Installs {-}

Now we add any pip installs that our module may need such as `numpy`, `pandas`, `Tensorflow`, and any others. If you used a virtual environment to develop module locally, and hopefully you did, then simply use `pip freeze > requirements.txt`. This will give you a text file with all the packages you are using in your virtual environment for your module. If you are a diligent person, you probably do not use one virtual environment for all your development in, say, Python 3.6. Hence, you will only have the necessary packages in the `requirements.txt` file. From this file, fill in the necessary pip installs within the Dockerfile. 

```sh
RUN pip install numpy pandas tensorflow
RUN pip install scikit-learn==0.19.1   # <--- For specific versions
RUN pip install -i https://biodev.ece.ucsb.edu/py/bisque/prod/+simple bisque-api==0.5.9
```

#### Working Directory, Source Code {-}

We typically define the working directory as follows:

```sh
WORKDIR /module
```
After this, you can put all of your source code along with the `PythonScriptWrapper` inside the `/modules` directory.

```sh
COPY PythonScriptWrapper /module/
COPY PythonScriptWrapper.py /module/
COPY YOUR_MODULE_SCRIPT.py /module/  #  <--- Source folders welcome too
COPY pydist /module/pydist/
ENV PATH /module:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```
The last line is the `ENV` instruction which sets the environment variable `<key>` to the value `<value>`. This value will be in the environment for all subsequent instructions in the build stage and can be replaced inline in many as well.

#### What Should My Last Line Be? {-}

Your last line in the Dockerfile should be the `CMD` command. There can only be one `CMD` instruction in a Dockerfile. If you list more than one `CMD` then only the last `CMD` will take effect. 

> The main purpose of a `CMD` is to provide defaults for an executing container. 

For us, we will use the `PythonScriptWrapper` as our `CMD` command as follows:

```sh
CMD [ 'PythonScriptWrapper' ]
```

Simple, am I right? Let's put all this together in a concrete example.

***

### __Example: Composite Strength__ {-}

The Composite Strength module requires a variety of special packages, such as a very specific version of `scikit-learn==0.19.1`. Please be aware that if you do pickle files using `scikit-learn`, you might have to use the same exact version to unpickle the file. Some of us found that out the hard way, hence the word of caution. 

This simple mistake can be extended to any number of machine learning tasks. We recommend that for _maximum reproducibility_, use the exact same version of all pip install packages as you did on your local development environment.

#### Step 1. Define Base Image, Run apt-gets, Install Python {-}

Similar to before, we will define our base image of Ubuntu Xenial, run the necessary `apt-gets` which is crucial, and install `Python`.
```sh
FROM ubuntu:xenial
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get -y update                                            && \
    apt-get -y upgrade                                           && \
    apt-get -y install                                              \
      python
```

#### Step 2. Install Needed apt-get Packages and Dependencies {-}

```sh
RUN apt-get -y install python-lxml python-numpy
RUN apt-get -y install python-pip liblapack3 libblas-dev liblapack-dev gfortran
RUN apt-get -y install python-scipy python-configparser python-h5py
RUN apt-get update
```

#### Step 3. Install Needed PIP Packages and Dependencies {-}

Best practice is always to have your pip installs defined in the Dockerfile instead of in a `requirements.txt`. The more self-contained, the better.

Additionally, __do not forget to install the `BQAPI` inside the container.__
```
RUN pip install pymks tables scipy
RUN pip install --user --install-option="--prefix=" -U scikit-learn==0.19.1
RUN pip install -i https://biodev.ece.ucsb.edu/py/bisque/prod/+simple bisque-api==0.5.9
RUN pip install requests==2.10.0
```

#### Step 4. Set Working Directory and COPY Source files {-}

The working directory should be defined as `/module` and in there, dump all your source code. If you want to be clean, use a `/source` folder in the `/module` directory. This is your module container and you have the control to customize the structure in any way that seems feasible to you. In this example, there is only one script that performs the entire analysis pipeline. Some might say too simple, others say efficient. 

```
WORKDIR /module
COPY PythonScriptWrapper /module/
COPY PythonScriptWrapper.py /module/
COPY predict_strength.py /module/
COPY pydist /module/pydist/
ENV PATH /module:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```
#### Step 5. Lastly, the Final Command. {-}

Your final command should come as no surprise. The reason we use the PythonScriptWrapper is because it makes life easier for you. Your focus should be on developing breakthrough methods, not how to handshake between a cloud platform and a Docker container.
```
CMD [ 'PythonScriptWrapper' ]
```

## Module XML

> __FILENAME: __ `NAME_OF_MODULE.xml`, where `NAME_OF_MODULE` is replaced by the name of your module, i.e. `Dream3D.xml`.

The module definition file lays out the interface that the system can call the module with. The simplest form simply lists the name, location and arguments needed to run the modules. Here is an example of a module definition document:

***

### __Example__ {-}

```xml
<?xml version="1.0" encoding="utf-8"?>
<module name="MetaData" type="runtime">

    <!-- Comments are OK -->
    <tag name="inputs">
        <tag name="image_url" type="resource">
            <template>
                <tag name="accepted_type" value="image" />
                <tag name="accepted_type" value="dataset" />
                <tag name="label" value="Image to extract metadata" />
                <tag name="prohibit_upload" value="true" type="boolean" />
            </template>
        </tag>

        <tag name="mex_url"  type="system-input" />
        <tag name="bisque_token"  type="system-input" />
    </tag>

    <tag name="outputs">
         <tag name="metadata" type="tag">
            <template>
                <tag name="label" value="Extracted metadata" />
            </template>
         </tag>
    </tag>

    <tag name="execute_options">
        <tag name="iterable" value="image_url" type="dataset" />
        <!-- Example for a blocked iteration -->
        <tag name="blocked_iter" value="true" />
    </tag>

    <tag name="module_options" >
        <tag name="version" value="3" />
    </tag>

    <tag name="display_options" >
       <tag name="group" value="Examples" />
    </tag>

    <tag name="help" type="file" value="public/help.html" />
    <tag name="thumbnail" type="file" value="public/thumbnail.png" />

    <tag name="title" type="string" value="MetaData" />
    <tag name="authors" type="string" value="The Bisque team" />
    <tag name="description" type="string" value="This module annotates an image with its embedded metadata." />
</module>
```

The definition above allows the BisQue system to call the module by creating a MEX.

The module definition document is actually a templated MEX document. The template parameters in this case are used to render the UI for this module if the user does not want to fully implement the UI. More about this will follow.

A module can define inputs and outputs and rely on the automated interface generation or can provide a fully customized user interface delivered by the module server by proxying the data made available by the engine service. Input configurations may also be used by the modules that define their own interfaces since they can call renderers provided by the module service.

***

### Module Description {-}
Each module has to be described in various ways to be useful. Each module has a number of required, as well as optional parameters it has/may contain. Type in this case can control where the data is coming from, for example default "string" suggests the data is in-place. "file" directs the engine server to look for the file starting in the module root directory.


__Title__
```xml
<tag name="title" value="MetaData" />  
```

__Description__
```xml
<tag name="description" value="This module annotates an image with its embedded metadata." />   
```

__Authors__
```xml
<tag name="authors" value="The Bisque team" /> 
```
__Thumbnail__
```xml
<tag name="thumbnail" type="file" value="public/thumbnail.png" />   
```

__Help__

An HTML document with a module help that the user can be directed to the document can be inline.
```xml
<tag name="help" type="file" value="public/help.html" /> 
```
__Module Options__:
```xml
<tag name="module_options" >
    <tag name="version" value="2" />
</tag>
```

### Configurations for Images, Datasets, and Resources {-}

__Label__ 

Specifies the label rendered before asking for a resource.
```xml
<tag name="label" value="Select input image" />
```

__Accepted Type__ 

Defines multiple allowed types of input resource.
```xml
<tag name="accepted_type" value="dataset" />
<tag name="accepted_type" value="image" />
```


__Prohibit Upload__

Used with resources of type image or dataset to specify that the uploader should not be allowed.
```xml
<tag name="prohibit_upload" value="true" type="boolean" />
```

__Example Query__

Allow a button "from Example" specifies the query string.
```xml
<tag name="example_query" value="*GFAP*" />
```

__Allow Blank__ 

Makes resource optional.
```xml
<tag name="allow_blank" value="true" type="boolean" />
```



***

#### `Image` Specific Configurations {-}

__Require Geometry__

Enforce input _image_ geometry.

Here the `z` or `t` value may be:

  - null or undefined - means it should not be enforced
  - 'single' - only one plane is allowed
  - 'stack' - only stack is allowed

```xml
<tag name="require_geometry">
    <tag name="z" value="stack" />
    <tag name="t" value="single" />
    <tag name="fail_message" value="Only supports 3D images!" />
</tag>
```

__Fail Message__

Specify a message to show if failed requires validation.

```xml
<tag name="fail_message" value="Only supports 3D images!" />
```
***



#### `gobject` Specific Configurations {-}

__Example__
```xml
<gobject name="tips">
  <template>
    <tag name="gobject" value="point" />
    <tag name="require_gobjects">              
        <tag name="amount" value="many" />
        <tag name="fail_message" value="Requires selection of root tips" />
    </tag>              
  </template>
</gobject>
```

__gobject__

Defines multiple allowed types of input gobject.
```xml
<tag name="gobject" value="point" />
<tag name="gobject" value="polygon" />
```
Semantic types can also be specified here:
```xml
<tag name="gobject" value="foreground">
    <tag name="color" value="#00FF00" type="color" />
</tag>
<tag name="gobject" value="background">
    <tag name="color" value="#FF0000" type="color" />
</tag>
```

Moreover, colors could be proposed for these semantic types to differentiate graphical annotations in modules visually.

Users can also force only semantic annotations to be created basically prohibiting creation of primitive graphical elements without semantic meaning:
```xml
<tag name="semantic_types" value="require" />
```

__Require gobjects__

Validate input _gobject_.

```xml
<tag name="require_gobjects">
    <tag name="amount" value="many" />
    <tag name="fail_message" value="Requires select of root tips" />
</tag>
```

Configuration for `require_gobjects` consists of:

  - __amount__ - constraint on the amount of objects of allowed type. The amount can take the following values:
    - null or undefined - means it should not be enforced
    - 'single' - only one object is allowed
    - 'many' - only more than one object allowed
    - 'oneornone' - only one or none
    - number - exact number of objects allowed
    - $\leq X$ - operand followed by a number, accepts: $<,>,<=,>=,==$ 

      
      Example. Note that $<$ sign should be encoded in an XML attribute.
      ```xml
      <tag name="amount" value="3" type="number" />
      or
      <tag name="amount" value=">=2" />
      or
      <tag name="amount" value="&lt;30" />
      ```



__Fail Message__

Specify a message to show if failed requires validation.

```xml
<tag name="fail_message" value="Requires select of root tips" />
```

__Color__

Specify a default color for created gobjects

```xml
<tag name="color" value="#00FFFF" type="color" />
```
Example with semantic types and other configuration:
```xml
<gobject name="stroke">
    <template>
        <tag name="gobject" value="freehand_line" />
        <tag name="gobject" value="foreground">
            <tag name="color" value="#00FF00" type="color" />
        </tag>
        <tag name="gobject" value="background">
            <tag name="color" value="#FF0000" type="color" />
        </tag>
        <tag name="semantic_types" value="require" />
        
        <tag name="require_gobjects">
            <tag name="amount" value=">=2" />
            <tag name="fail_message" value="Requires two polylines; 
            first one inside object of interest (foreground)
            and second across background." />
        </tag>
    </template>
</gobject>
```
***

#### `string` Specific Configurations {-}

__Label__

Specifies the label rendered before asking for a resource:
```xml
<tag name="label" value="Select input image" />
```

__Description__

Provides larger description shown in the tool-tip:

```xml
<tag name="description" value="This variable is very important..." />
```

__Units__ 

Provides the string and possibly defines conversions, not all types support units, for example boolean does not:

```xml
<tag name="units" value="microns" />
```

__Fail Message__ 

Message that will be displayed if failed the check:
```xml
<tag name="fail_message" value="We need a time series image" />
```

__Minimum Length__ 

Minimum length of the required string:

```xml
<tag name="minLength" value="10" type="number" />
```

__Maximum Length__

Maximum length of the required string:

```xml
<tag name="maxLength" value="100" type="number" />
```

__Allow Blank__ 

Used to allow empty strings, true by default:

```xml
<tag name="allowBlank" value="true" type="boolean" />
```

__Regex__

Regular expression used to validate input string:

```xml
<tag name="regex" value="[\w]" />
```

__Default Value__ 

Default value of this field:

```xml
<tag name="defaultValue" value="" />
```

__Editable__

Whether this field is editable by the user, true by default:
```xml
<tag name="editable" value="true" type="boolean" />
```

***

#### `number` Specific Configurations {-}

A number can select one or more values, in case of selecting multiple values they will be selected using a multi-slider.

__Label__ 

Simply specifies the label rendered before asking for a resource:
```xml
<tag name="label" value="Select input image" />
```

__Description__ 

Provides larger description shown in the tool-tip:
```xml
<tag name="description" value="This variable is very important..." />
```

__Units__ 

Provides the string and possibly defines conversions, not all types support units, for example boolean does not:
```xml
<tag name="units" value="microns" />
```

__Fail Message__ 

Message that will be displayed if failed the check:
```xml
<tag name="fail_message" value="We need a time series image" />
```
__Minimum Value__ 

Lowest allowed value:
```xml
<tag name="minValue" value="10" type="number" />
```

__Maximum Value__

Highest allowed value:
```xml
<tag name="maxValue" value="100" type="number" />
```
__Allow Decimals__ 

Allow to acquire floating point numbers:
```xml
<tag name="allowDecimals" value="true" type="boolean" />
```
__Decimal Precision__ 

How many digits after the dot are allowed:
```xml
<tag name="decimalPrecision" value="4" type="number" />
```
__Default Value__ 

Default value of this field:
```xml
<tag name="defaultValue" value="" />
```
__Editable__

Whether this field is editable by the user, true by default:
```xml
<tag name="editable" value="true" type="boolean" />
```
__Step__ 

Step to be used by increment/decrement buttons:
```xml
<tag name="step" value="1" type="number" />
```
__Show Slider__ 

Allows hiding the slider in case of single value picking:
```xml
<tag name="showSlider" value="false" type="boolean" />
```

__Hide Number Picker__ 

Allows hiding the number selection box if only slider is preferred:
```xml
<tag name="hideNumberPicker" value="true" type="boolean" />
```

__Multiple Values__

Using multiple values:
```xml
<tag name="myrange" type="number" >
    <value>5.6</value>
    <value>12</value>
    <value>14</value>                        
</tag>
```

***

#### `combo` Specific Configurations {-}

__Label__ 

Simply specifies the label rendered before asking for a resource:

```xml
<tag name="label" value="Select input image" />
```
__Description__

Provides larger description shown in the tool-tip:

```xml
<tag name="description" value="This variable is very important..." />
```

__Units__ 

Provides the string and possibly defines conversions, not all types support units, for example boolean does not:

```xml
<tag name="units" value="microns" />
```
__Select__ 

Specifies a list of select elements, provide as many as you need, this might have to be implemented as a list of values?:

```xml
<tag name="select" value="Alaska" />
<tag name="select" value="California" />
```

__Passed Values__ 

Specifies a list of values passed for the corresponding select elements, this might have to be implemented as a list of values?:

```xml
<tag name="select" value="AL" />
<tag name="select" value="CA" />
```

__Failed Value__ 

If the combo's value is same as fail_value, combo's input is considered invalid and the fail_message is displayed:

```xml
<tag name="fail_value" value="Select a choice..." />
```

__Fail Message__ 

Error message that will be displayed if combo's value is null or same as fail_value:

```xml
<tag name="fail_message" value="User needs to select a choice!" />
```

__Editable__ 

Allows a combo box string to be edited directly and would allow input of values not existent in the select list:

```xml
<tag name="editable" value="true" type="boolean" />
```

***

#### `boolean` Specific Configurations {-}


__Label__ - simply specifies the label rendered before asking for a resource:
```xml
<tag name="label" value="Select input image" />
```
__Description__

Provides larger description shown in the tool-tip:
```xml
<tag name="description" value="This variable is very important..." />
```

__Fail Message__

Message that will be displayed if failed the check:

```xml
<tag name="fail_message" value="We need a time series image" />
```

__Default Value__ 

Default value of this field:

```xml
<tag name="defaultValue" value="" type="boolean" />
```

__Editable__

Whether this field is editable by the user, true by default:

```xml
<tag name="editable" value="true" type="boolean" />
```

***



#### `date` Specific Configurations {-}

This renderer allow you to pick both date and time.

> __NOTE.__ _Value_ contains a string in ISO standard, ex: __YYYY:MM:DDThh:mm:ss__

__No Date__ 

Can hide the date picker:

```xml
<tag name="nodate" value="true" type="boolean" />
```
__No Time__ 

Can hide the time picker:

```xml
<tag name="notime" value="true" type="boolean" />
```
__Label__ 

Simply specifies the label rendered before asking for a resource:

```xml
<tag name="label" value="Select input image" />
```

__Description__

Provides larger description shown in the tool-tip:
```xml
<tag name="description" value="This variable is very important..." />
```

__Fail Message__ 

Message that will be displayed if failed the check:

```xml
<tag name="fail_message" value="We need a time series image" />
```

__Format__ 

Date format used by this field, default value is : YYYY:MM:DDThh:mm:ss
```xml
<tag name="format" value="YYYY:MM:DDThh:mm:ss" />
```
__Editable__

Whether this field is editable by the user, true by default:

```xml
<tag name="editable" value="true" type="boolean" />
```

***

#### `hyperlink` Specific Configurations {-}

__Default Value__

Default value of this field:

```xml
<tag name="defaultValue" value="" />
```
__Editable__

Whether this field is editable by the user, true by default:


```xml
<tag name="editable" value="true" type="boolean" />
```
***
#### `email` Specific Configurations {-}


__Default Value__

Default value of this field:

```xml
<tag name="defaultValue" value="" />
```

__Editable__

Whether this field is editable by the user, true by default:

```xml
<tag name="editable" value="true" type="boolean" />
```
***

#### `bisqueresource` Specific Configurations {-}


__Resource Type__ 

Type of bisque resource to be selected, image by default:

```xml
<tag name="resourceType" value="image" />
```

__Default Value__

Default value of this field:

```xml
<tag name="defaultValue" value="" />
```

__Editable__

Whether this field is editable by the user, true by default:

```xml
<tag name="editable" value="true" type="boolean" />
```

***

#### `annotation_status` Specific Configurations {-}

This element allows marking resources with annotation status as: 

- __STARTED__
- __FINISHED__ 
- __APPROVED__

***

#### `image_channel` Specific Configurations {-}

__Example:__

```xml
<tag name="nuclear_channel" value="1" type="image_channel">
    <template>
        <tag name="label" value="Nuclear channel" />
        <tag name="reference" value="resource_url" />
        <tag name="guess" value="nuc|Nuc|dapi|DAPI|405|dna|DNA|Cy3" />
        <tag name="fail_message" value="You need to select image channel" />
        <tag name="allowNone" value="false" type="boolean" />
        <tag name="description" value="Select an image channel representing nulcei" />
    </template>
</tag>
```

__Label__ 

Simply specifies the label rendered before asking for a resource:
```xml
<tag name="label" value="Select input image" />
```

__Description__ 

Provides larger description shown in the tool-tip:
```xml
<tag name="description" value="This variable is very important..." />
```

__Fail Message__

Message that will be displayed if failed the check:

```xml
<tag name="fail_message" value="You need to select a channel" />
```

__Reference__

Name of the input resource that should be used to initialize this selector:
```xml
<tag name="reference" value="resource_url"/>
```
__Guess__ 

Regular expression used to guess which channel should be selected by default:
```xml
<tag name="guess" value="nuc|Nuc|dapi|DAPI|405|dna|DNA|Cy3"/>
```

__Allow None__

Allows selection of 'None' channel, used for optional channel selection:

```xml
<tag name="allowNone" value="true" type="boolean" />
```

***

#### `pixel_resolution` Specific Configurations {-}

This element must have for values that represent X, Y, Z and T resolution values in microns, microns, microns and seconds respectively.

__Example:__

```xml
<tag name="pixel_resolution" type="pixel_resolution">
    <value>0</value>
    <value>0</value>
    <value>0</value>             
    <value>0</value>               
    <template>
        <tag name="label" value="Voxel resolution" />
        <tag name="reference" value="resource_url" />
        <tag name="units" value="microns" />                
        <tag name="description" value="This is a default voxel resolution and is only used during the dataset run if the image does not have one." />   
    </template>
</tag>
```

__Label__

Simply specifies the label rendered before asking for a resource:

```xml
<tag name="label" value="Select input image" />
```

__Description__ 

Provides larger description shown in the tool-tip:

```xml
<tag name="description" value="This variable is very important..." />
```

__Fail Message__ 

Message that will be displayed if failed the check:

```xml
<tag name="fail_message" value="You need to select a channel" />
```

__Reference__ 

Name of the input resource that should be used to initialize this selector:

```xml
<tag name="reference" value="resource_url"/>
```

__Units__ 

Provides the string and possibly defines conversions, not all types support units, for example boolean does not:
```xml
<tag name="units" value="microns" />
```

__Description__ 

Used to show tool tip information:

```xml
<tag name="description" value="This is a default voxel resolution and is only used during the dataset run if the image does not have one." />
```

***

#### `annotation_attr` Specific Configurations {-}


This element allows select attributes of annotations (tags/gobjects) from either whole database or constrained by a dataset. For example it can be used to select a type out of a list of all types of graphical annotations.

__Example:__
```xml
<tag name="gob_types" value="" type="annotation_attr"> 
    <tag name="template" type="template"> 
 	    <tag name="label" value="Graphical types" /> 
            <tag name="allowBlank" value="false" type="boolean" /> 
 		 
 	    <tag name="reference_dataset" value="dataset_url" /> 
 	    <tag name="reference_type" value="annotation_type" /> 
 	    <tag name="reference_attribute" value="annotation_attribute" /> 
 	
 	    <tag name="element" value="gobject" /> 
 	    <tag name="attribute" value="type" /> 
 	    <tag name="dataset" value="/data_service/" /> 
     </tag>
</tag> 
```

__Label__ 

Simply specifies the label rendered before asking for a resource:

```xml
<tag name="label" value="Select input image" />
```

__Description__

Provides larger description shown in the tool-tip:

```xml
<tag name="description" value="This variable is very important..." />
```

__Reference Dataset__ 

Name of the input resource that can be used to initialize this selector's constrained query:

```xml
<tag name="reference_dataset" value="resource_url"/>
```

__Reference Type__ 

Name of the type selector that can be used to initialize this selector's constrained query:

```xml
<tag name="reference_type" value="type_combo"/>
```

__Reference Attribute__ 

Name of the attribute selector that can be used to initialize this selector's constrained query:

```xml
<tag name="reference_attribute" value="attrib_combo"/>
```

__Element__ 

Default value for the element to constraine query:

```xml
<tag name="element" value="gobject" /> 
```

__Attribute__ 

Default value for the attribute to constrain query:

```xml
<tag name="attribute" value="type" />  
```

__Dataset__

Default value for the dataset to constrain query:
```xml
<tag name="dataset" value="/data_service/" /> 
```
***

#### `mex` Specific Configurations {-}

This element selects a previously run module execution in order to chain modules.

__Example:__
```xml
<tag name="mex_url" type="mex">
    <template>
        <tag name="label" value="Select input MEX" />
        <tag name="query" value="&amp;name=NuclearDetector3D" /> 
    </template>
</tag>    
```

__Label__ 

Simply specifies the label rendered before asking for a resource:
```xml
<tag name="label" value="Select input image" />
```

__Description__ 

Provides larger description shown in the tool-tip:

```xml
<tag name="description" value="This variable is very important..." />
```

__Query__

A query string that would narrow MEX search:

```xml
<tag name="query" value="&amp;name=NuclearDetector3D" /> 
```

__Query Selected Resource__ 

This option allows MEX selector to pretend it is an image resource selector by finding the name of the required resource in the selected MEX and emitting selection signal. This can be used for MEX selectors that would like to init image resolution or image channel pickers based on an input MEX:

```xml
<tag name="query_selected_resource" value="resource_url" /> 
```


***

### Data-Parallel Execution {-}

It is possible to execute any module in a data-parallel way by passing a dataset instead of an individual image. In order to do this you need to:

  1. Indicate the resource that can be iterated on
  2. Allow that resource to accept datasets and possibly
  3. Configure renderers for iterated run
  

```xml
<!-- allow iterable resource to accept datasets -->
<tag name="inputs">
    <tag name="image_url" type="resource">
        <template>
            <tag name="accepted_type" value="image" />
            <tag name="accepted_type" value="dataset" />
            ...
        </template>
    </tag> 
    ...
</tag> 

...
<!-- configure renderers for iterated run -->
<tag name="outputs">
    ...         
    <!-- Iterated outputs -->
    <tag name="mex_url" type="mex" />
    <tag name="resource_url" type="dataset" />
</tag>

.....

<!-- indicate the resource that can be iterated -->
<tag name="execute_options">
    <tag name="iterable" value="image_url" type="dataset" />
</tag> 
```
This definition is used by the module UI to add a dataset selector for this image and let module server know by sending a proper MEX that this resource should be iterated upon. Module server will create a parallel execution iterating over the selected dataset and creating an output MEX with sub MEXes for each individual image.

__Other Data-Parallel Types__

One can also request parallel execution over resource types other than `dataset`. For example a very useful would be to request iteration over a MEX, where a module could accept parallelized MEX as input and iterate over sub-MEXs for parallelized processing of results. In order to do that we need to indicate the type of the input resource and additionally provide an xpath expression within that resource to find elements we would like to iterate over:

```xml
<tag name="execute_options">
    <tag name="iterable" value="input_mex" type="mex" >
        <tag name="xpath" value="./mex/@uri" />
    </tag>
</tag> 
```




## Python Script Wrapper

> __FILENAME: __ `PythonScriptWrapper.py`

### _Example._  Python Script Wrapper {-}

#### Imports {-}

The main imports for the `PythonScriptWrapper` are mostly for logging and communicating with BisQue. In this code snippet, the line `from NAME_OF_MODULE import predict_function` is importing a prediction function from a single `Python` file. If multiple functions need to be imported from a source folder, make sure there is an `__init__.py` or there will be import errors. 


```python
import sys
import io
from lxml import etree
import optparse
import logging


from NAME_OF_MODULE import predict_function


logging.basicConfig(filename='PythonScript.log',filemode='a',level=logging.DEBUG)
log = logging.getLogger('bq.modules')


from bqapi.comm import BQCommError
from bqapi.comm import BQSession
```


#### Python Script Wrapper Class {-}

The class contains all of the functions needed to initialize, run, and save the module results back to BisQue as a resource. For instance, if the output is an image, the resource would be of type image and uploaded to BisQue as an image.


```python
class PythonScriptWrapper(object):
    def run(self):
        """
        Run Python script
        """
        bq = self.bqSession
        
        # call script
        outputs = predict_function( bq, log, **self.options.__dict__ )
        
        # save output back to BisQue
        for output in outputs:
            self.output_resources.append(output)
    
    def setup(self):
        """
        Pre-run initialization
        """
        self.bqSession.update_mex('Initializing...')
        self.mex_parameter_parser(self.bqSession.mex.xmltree)
        self.output_resources = []

    def teardown(self):
        """
        Post the results to the mex xml
        """
        self.bqSession.update_mex( 'Returning results')

        outputTag = etree.Element('tag', name ='outputs')
        for r_xml in self.output_resources:
            if isinstance(r_xml, basestring):
                r_xml = etree.fromstring(r_xml) 
            res_type = r_xml.get('type', None) or r_xml.get('resource_type', None) or r_xml.tag
            # append reference to output
            if res_type in ['table', 'image']:
                outputTag.append(r_xml)
                #etree.SubElement(outputTag, 'tag', name='output_table' if res_type=='table' else 'output_image', type=res_type, value=r_xml.get('uri',''))
            else:
                outputTag.append(r_xml)
                #etree.SubElement(outputTag, r_xml.tag, name=r_xml.get('name', '_'), type=r_xml.get('type', 'string'), value=r_xml.get('value', ''))
        self.bqSession.finish_mex(tags=[outputTag])

    def mex_parameter_parser(self, mex_xml):
        """
            Parses input of the xml and add it to options attribute (unless already set)

            @param: mex_xml
        """
        # inputs are all non-"script_params" under "inputs" and all params under "script_params"
        mex_inputs = mex_xml.xpath('tag[@name="inputs"]/tag[@name!="script_params"] | tag[@name="inputs"]/tag[@name="script_params"]/tag')
        if mex_inputs:
            for tag in mex_inputs:
                if tag.tag == 'tag' and tag.get('type', '') != 'system-input': #skip system input values
                    if not getattr(self.options,tag.get('name', ''), None):
                        log.debug('Set options with %s as %s'%(tag.get('name',''),tag.get('value','')))
                        setattr(self.options,tag.get('name',''),tag.get('value',''))
        else:
            log.debug('No Inputs Found on MEX!')

    def validate_input(self):
        """
            Check to see if a mex with token or user with password was provided.

            @return True is returned if validation credention was provided else
            False is returned
        """
        if (self.options.mexURL and self.options.token): #run module through engine service
            return True

        if (self.options.user and self.options.pwd and self.options.root): #run module locally (note: to test module)
            return True

        log.debug('Insufficient options or arguments to start this module')
        return False
```

#### Main Function {-}

The main function enables the communication between BisQue and the module. For example, when a module is run under a user, we need to make sure that the unique ID is registered with the user.


```python
def main(self):
    parser = optparse.OptionParser()
    parser.add_option('--mex_url'         , dest="mexURL")
    parser.add_option('--module_dir'      , dest="modulePath")
    parser.add_option('--staging_path'    , dest="stagingPath")
    parser.add_option('--bisque_token'    , dest="token")
    parser.add_option('--user'            , dest="user")
    parser.add_option('--pwd'             , dest="pwd")
    parser.add_option('--root'            , dest="root")
        
    (options, args) = parser.parse_args()

    fh = logging.FileHandler('scriptrun.log', mode='a')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)8s --- %(message)s ' +
                              '(%(filename)s:%(lineno)s)',datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    log.addHandler(fh)

    try: #pull out the mex

        if not options.mexURL:
            options.mexURL = sys.argv[-2]
        if not options.token:
            options.token = sys.argv[-1]

    except IndexError: #no argv were set
        pass

    if not options.stagingPath:
        options.stagingPath = ''

    log.info('\n\nPARAMS : %s \n\n Options: %s' % (args, options))
    self.options = options

    if self.validate_input():

        #initalizes if user and password are provided
        if (self.options.user and self.options.pwd and self.options.root):
            self.bqSession = BQSession().init_local( self.options.user, self.options.pwd, bisque_root=self.options.root)
            self.options.mexURL = self.bqSession.mex.uri

        #initalizes if mex and mex token is provided
        elif (self.options.mexURL and self.options.token):
            self.bqSession = BQSession().init_mex(self.options.mexURL, self.options.token)

        else:
            raise ScriptError('Insufficient options or arguments to start this module')

        try:
            self.setup()
        except Exception as e:
            log.exception("Exception during setup")
            self.bqSession.fail_mex(msg = "Exception during setup: %s" %  str(e))
            return

        try:
            self.run()
        except (Exception, ScriptError) as e:
            log.exception("Exception during run")
            self.bqSession.fail_mex(msg = "Exception during run: %s" % str(e))
            return

        try:
            self.teardown()
        except (Exception, ScriptError) as e:
            log.exception("Exception during teardown")
            self.bqSession.fail_mex(msg = "Exception during teardown: %s" %  str(e))
            return
    
        self.bqSession.close()

if __name__=="__main__":
    PythonScriptWrapper().main()
```

## Source Code

> You can have all your files in a `/source` folder or have one `Python, MATLAB, C++,` etc. file.

In the case where the source code is in one file, it makes less sense to put the file in a `/source` directory. However, when the source code is spread across multiple files and directories, using a `/source` directory will make life easier and more organized.

### _Example._ Composite Strength Module {-}

Let's take a look at the structure of the Composite Strength module. In this example, we only have one `Python` file that contains all of our source code, `predict_strength.py`. 

```sh
TwoPhasePrediction/
├── Dockerfile
├── PythonScriptWrapper
├── PythonScriptWrapper.py
├── TwoPhasePrediction.xml
├── predict_strength.py   # <----- Source file
├── public
│   ├── help.html
│   ├── marat_workflow.png
│   ├── thumbnail.png
│   ├── webapp.css
│   └── webapp.js
├── runtime-module.cfg
└── setup.py
```


## Runtime Module Configuration

> __FILENAME: __ `runtime-module.cfg`

The runtime module configuration file only has one line that needs to be changed: 

- `docker.image = NAME_OF_MODULE` This should be the name of the docker image of the module. Hence, when the module is run, it will look for that specific docker image. Good practice would be to use different names when the module is updated `NAME_OF_MODULE-v2` or include a tag, such as `stable` or `latest`. 

```sh
#  Module configuration file for local execution of modules
runtime.platforms = command

#  Module configuration file for local execution of modules
module_enabled = True
runtime.platforms=command

[command]
docker.image = NAME_OF_MODULE
environments = Staged,Docker
executable = python PythonScriptWrapper.py
files = pydist, PythonScriptWrapper.py
```

### _Example._ Composite Strength Module {-}

In this example, we see that the name of the docker image is `predict_strength`. So, when a user hits __Run__ on the Composite Strength module page, BisQue will always pull the latest image of `predict_strength`.

```sh
#  Module configuration file for local execution of modules
runtime.platforms = command

#  Module configuration file for local execution of modules
module_enabled = True
runtime.platforms=command

[command]
docker.image = predict_strength
environments = Staged,Docker
executable = python PythonScriptWrapper.py
files = pydist, PythonScriptWrapper.py
```


## Python Setup

> __FILENAME: __ `setup.py`

The only changes to make in this file are naming. Specifically, this line:

```python
docker_setup('Composite_Strength', 'TwoPhasePrediction', 'twophaseprediction', params=params)
```

__NOTE:__ Before running `python setup.py`, please make sure that all the files are created and configured correctly. If not, save yourself hours of troubleshooting by going through the other file tutorials.




```python
import sys
from bq.setup.module_setup import python_setup, docker_setup, require, read_config


def setup(params, *args, **kw):
    python_setup('PythonScriptWrapper.py', params=params)
    docker_setup('Composite_Strength', 'TwoPhasePrediction', 'twophaseprediction', params=params)
    
if __name__ =="__main__":
    params = read_config('runtime-bisque.cfg')
    if len(sys.argv)>1:
        params = eval (sys.argv[1])
    sys.exit(setup(params))
```


## __How to Run Modules Locally__ {-}

Whether you have finished building your module and are ready to test it out or you simply want to run one of the preexisting modules locally, we got you covered with this tutorial.

### __Step 1.__ Pull the Latest Dev Container {-}

Assuming you already have [Docker](https://docs.docker.com/get-docker/) installed on your local system, this developer image has everything you need to install BisQue locally. Since this image is updated weekly, file an issue on GitHub and we will look at it within a day.

```sh
docker pull amilworks/bisque-module-dev:git
```


### __Step 2.__ Run the Dev Container {-}

Running the command below will launch BisQue on http://localhost:8080/, name the container `bq-module-dev`, and `-v /var/run/docker.sock:/var/run/docker.sock` will enable access to your local docker containers within the BisQue dev container. This is crucial because modules are ran as containers themselves so if you cannot run a container within a container, you will get a big red module error at runtime.

```sh
docker run -idp 8080:8080 -p 27000:27000 --name bq-module-dev 
    -v /var/run/docker.sock:/var/run/docker.sock 
    --ipc=host --net=host amilworks/bisque-module-dev:git
```

If you run into any port allocation issues, double check to see if there are any __running containers__ 

```sh
docker ps
```
You can __stop any running containers__ that are using port 8080 or 27000 with

```sh
docker stop CONTAINER ID or NAME
```

If you run into any issues with __dangling containers__, you can safely remove them by running 

```sh
docker container prune
```

### __Step 3.__ Register Modules {-}

Navigate to http://localhost:8080/ on your favorite web browser and BisQue should be up and running. If BisQue is not, check the logs and report any issues on GitHub. Login using the credentials

__Username__: admin

__Password__: admin

You should now be logged in as admin. In the top right hand corner, go to `Administrator --> Module Manager`. In the right pane, __Engine Modules__, fill in the __Engine URL__ with 

```
http://localhost:8080/engine_service
```

Hit __Load__ and all the modules should pop up, and hopefully your module if you are building one. Navigate to your module or any module using the __Analysis__ tab on the menu bar and you should see the respective module's landing page. For instance, if I go to CellECT 2.0, I should see the following page.

![__CellECT 2.0 Module Homepage.__ Here is the landing page for the GPU-enabled CellECT 2.0 module.](images/CellECT.png)


### __Step 4.__ Run the Module {-}


Upload a sample image or table to the module of your choice, modify any necessary hyperparameters, and then hit __Run__. Your module should start initializing and providing updates on what its doing.

#### What's Happening on the Backend? {-}

On the backend, the module will first check to see if the image is up-to-date. If not, it will pull the latest. Next, it will Initialize the module by running the `PythonScriptWrapper` and jump right into running your module. If there are any errors, the logs will be stored in the `staging` folder. You can access this by ssh-ing into the container and directly accessing that directory.

```sh
> docker exec -it bq-module-dev bash
> cd staging
> ls -ltr   # Get the latest run
> cd [MEX ID] 
> cat PythonScript.log
```




