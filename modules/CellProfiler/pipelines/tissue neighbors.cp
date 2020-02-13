CellProfiler Pipeline: http://www.cellprofiler.org
Version:1
SVNRevision:11000

LoadImages:[module_num:1|svn_version:\'10951\'|variable_revision_number:11|show_window:True|notes:\x5B"Load the color image by matching files in the folder against the text \'.JPG\'"\x5D]
    File type to be loaded:individual images
    File selection method:Text-Exact match
    Number of images in each group?:3
    Type the text that the excluded images have in common:Do not use
    Analyze all subfolders within the selected folder?:None
    Input image file location:Default Input Folder\x7C.
    Check image sets for missing or duplicate files?:No
    Group images by metadata?:No
    Exclude certain files?:No
    Specify metadata fields to group by:
    Select subfolders to analyze:
    Image count:1
    Text that these images have in common (case-sensitive):1.JPG
    Position of this image in each group:1.JPG
    Extract metadata from where?:None
    Regular expression that finds metadata in the file name:None
    Type the regular expression that finds metadata in the subfolder path:None
    Channel count:1
    Group the movie frames?:No
    Grouping method:Interleaved
    Number of channels per group:2
    Load the input as images or objects?:Images
    Name this loaded image:Original
    Name this loaded object:Nuclei
    Retain outlines of loaded objects?:No
    Name the outline image:NucleiOutlines
    Channel number:1
    Rescale intensities?:Yes

Crop:[module_num:2|svn_version:\'10804\'|variable_revision_number:2|show_window:True|notes:\x5B\'Crop the color image to exclude the text labels by entering specific cropping coordinates.\'\x5D]
    Select the input image:Original
    Name the output image:Cropped
    Select the cropping shape:Rectangle
    Select the cropping method:Coordinates
    Apply which cycle\'s cropping pattern?:First
    Left and right rectangle positions:45,629
    Top and bottom rectangle positions:1,445
    Coordinates of ellipse center:500,500
    Ellipse radius, X direction:400
    Ellipse radius, Y direction:200
    Use Plate Fix?:No
    Remove empty rows and columns?:No
    Select the masking image:None
    Select the image with a cropping mask:None
    Select the objects:None

ColorToGray:[module_num:3|svn_version:\'10318\'|variable_revision_number:2|show_window:True|notes:\x5B\'Retain the red channel for later segmentation.\'\x5D]
    Select the input image:Cropped
    Conversion method:Split
    Image type\x3A:RGB
    Name the output image:OrigGray
    Relative weight of the red channel:1
    Relative weight of the green channel:1
    Relative weight of the blue channel:1
    Convert red to gray?:Yes
    Name the output image:OrigRed
    Convert green to gray?:No
    Name the output image:OrigGreen
    Convert blue to gray?:No
    Name the output image:OrigBlue
    Channel count:1
    Channel number\x3A:Red\x3A 1
    Relative weight of the channel:1
    Image name\x3A:Channel1

ImageMath:[module_num:4|svn_version:\'10718\'|variable_revision_number:3|show_window:True|notes:\x5B\'Since object identification assumes light objects against a dark background, invert the grayscale intensities of the red channel so the dark areas appear bright and vice versa.\'\x5D]
    Operation:Invert
    Raise the power of the result by:1.0
    Multiply the result by:1.0
    Add to result:0
    Set values less than 0 equal to 0?:
    Set values greater than 1 equal to 1?:
    Ignore the image masks?:No
    Name the output image:InvertedRed
    Image or measurement?:Image
    Select the first image:OrigRed
    Multiply the first image by:1.0
    Measurement:
    Image or measurement?:Image
    Select the second image:
    Multiply the second image by:1
    Measurement:

IdentifyPrimaryObjects:[module_num:5|svn_version:\'10826\'|variable_revision_number:8|show_window:True|notes:\x5B\'Identify the individual cells. Three-class thresholding works better than the default two-class method. Some adjustment of the correction factor, smoothing filter size and maxima supression distance is required to optimize segmentation.\'\x5D]
    Select the input image:InvertedRed
    Name the primary objects to be identified:Cells
    Typical diameter of objects, in pixel units (Min,Max):5,99999
    Discard objects outside the diameter range?:Yes
    Try to merge too small objects with nearby larger objects?:No
    Discard objects touching the border of the image?:Yes
    Select the thresholding method:Otsu Global
    Threshold correction factor:0.8
    Lower and upper bounds on threshold:0,1
    Approximate fraction of image covered by objects?:10%
    Method to distinguish clumped objects:Intensity
    Method to draw dividing lines between clumped objects:Intensity
    Size of smoothing filter:4
    Suppress local maxima that are closer than this minimum allowed distance:4
    Speed up by using lower-resolution image to find local maxima?:Yes
    Name the outline image:CellOutlines
    Fill holes in identified objects?:Yes
    Automatically calculate size of smoothing filter?:No
    Automatically calculate minimum allowed distance between local maxima?:No
    Manual threshold:0.0
    Select binary image:Otsu Global
    Retain outlines of the identified objects?:Yes
    Automatically calculate the threshold using the Otsu method?:Yes
    Enter Laplacian of Gaussian threshold:.5
    Two-class or three-class thresholding?:Three classes
    Minimize the weighted variance or the entropy?:Weighted variance
    Assign pixels in the middle intensity class to the foreground or the background?:Foreground
    Automatically calculate the size of objects for the Laplacian of Gaussian filter?:Yes
    Enter LoG filter diameter:5
    Handling of objects if excessive number of objects identified:Continue
    Maximum number of objects:500
    Select the measurement to threshold with:None

OverlayOutlines:[module_num:6|svn_version:\'10672\'|variable_revision_number:2|show_window:True|notes:\x5B\'Overlay the cell outlines in the inverted image.\'\x5D]
    Display outlines on a blank image?:No
    Select image on which to display outlines:InvertedRed
    Name the output image:InvertedRedOutlines
    Select outline display mode:Color
    Select method to determine brightness of outlines:Max of image
    Width of outlines:1
    Select outlines to display:CellOutlines
    Select outline color:Red

MeasureObjectNeighbors:[module_num:7|svn_version:\'Unknown\'|variable_revision_number:1|show_window:True|notes:\x5B\'Obtain neighborhood metrics by expanding the cells until they touch. Retain an output image for later export.\'\x5D]
    Select objects to measure:Cells
    Method to determine neighbors:Expand until adjacent
    Neighbor distance:0
    Retain the image of objects colored by numbers of neighbors for use later in the pipeline (for example, in SaveImages)?:Yes
    Name the output image:ColorNeighbors
    Select colormap:hot
    Retain the image of objects colored by percent of touching pixels for use later in the pipeline (for example, in SaveImages)?:No
    Name the output image:PercentTouching
    Select a colormap:Default

MeasureObjectSizeShape:[module_num:8|svn_version:\'1\'|variable_revision_number:1|show_window:True|notes:\x5B\'Measure morphological features from the cell objects.\'\x5D]
    Select objects to measure:Cells
    Calculate the Zernike features?:No

MeasureObjectIntensity:[module_num:9|svn_version:\'10816\'|variable_revision_number:3|show_window:True|notes:\x5B\'Measure intensity features from cell objects against the red channel.\'\x5D]
    Hidden:1
    Select an image to measure:OrigRed
    Select objects to measure:Cells

SaveImages:[module_num:10|svn_version:\'10822\'|variable_revision_number:7|show_window:True|notes:\x5B"Save the neighbor output image as an 8-bit TIF, appending the text \'colorneighbors\' to the original filename of the color image."\x5D]
    Select the type of image to save:Image
    Select the image to save:ColorNeighbors
    Select the objects to save:None
    Select the module display window to save:NeighborImage
    Select method for constructing file names:From image filename
    Select image name for file prefix:Original
    Enter single file name:Original
    Do you want to add a suffix to the image file name?:Yes
    Text to append to the image name:_ColorNeighbors
    Select file format to use:tif
    Output file location:Default Output Folder\x7CNone
    Image bit depth:8
    Overwrite existing files without warning?:No
    Select how often to save:Every cycle
    Rescale the images? :No
    Save as grayscale or color image?:Grayscale
    Select colormap:gray
    Store file and path information to the saved image?:No
    Create subfolders in the output folder?:No

SaveImages:[module_num:11|svn_version:\'10822\'|variable_revision_number:7|show_window:True|notes:\x5B"Save the overlay image as an 8-bit TIF, appending the text \'invertedred\' to the original filename of the color image."\x5D]
    Select the type of image to save:Image
    Select the image to save:InvertedRedOutlines
    Select the objects to save:None
    Select the module display window to save:InvertedRed
    Select method for constructing file names:From image filename
    Select image name for file prefix:Original
    Enter single file name:Original
    Do you want to add a suffix to the image file name?:Yes
    Text to append to the image name:_InvertedRed
    Select file format to use:tif
    Output file location:Default Output Folder\x7CNone
    Image bit depth:8
    Overwrite existing files without warning?:No
    Select how often to save:Every cycle
    Rescale the images? :No
    Save as grayscale or color image?:Grayscale
    Select colormap:gray
    Store file and path information to the saved image?:No
    Create subfolders in the output folder?:No

ExportToSpreadsheet:[module_num:12|svn_version:\'10880\'|variable_revision_number:7|show_window:True|notes:\x5B\'Export any measurements to a comma-delimited file (.csv). The measurements made for the cell objects and the image will be saved to separate .csv files. Mean per-image cell measurements will also be exported to the image .csv.\'\x5D]
    Select or enter the column delimiter:Comma (",")
    Prepend the output file name to the data file names?:Yes
    Add image metadata columns to your object data file?:No
    Limit output to a size that is allowed in Excel?:No
    Select the columns of measurements to export?:No
    Calculate the per-image mean values for object measurements?:Yes
    Calculate the per-image median values for object measurements?:No
    Calculate the per-image standard deviation values for object measurements?:No
    Output file location:Default Output Folder\x7C.
    Create a GenePattern GCT file?:No
    Select source of sample row name:Metadata
    Select the image to use as the identifier:None
    Select the metadata to use as the identifier:None
    Export all measurements, using default file names?:No
    Press button to select measurements to export:None\x7CNone
    Data to export:Image
    Combine these object measurements with those of the previous object?:No
    File name:Summary.csv
    Use the object name for the file name?:No
    Data to export:Cells
    Combine these object measurements with those of the previous object?:No
    File name:Objects.csv
    Use the object name for the file name?:No
