"""Helpers for images, PDFs, etc.

This module is in 'unfinished' because the functions have various dependencies,
file naming conventions, and cache conventions which may not be appropriate for
WebHelpers.  This module was written by Mike Orr, except
``make_pdf_thumbnail2()`` which was written by Chris Barker.

``static_image()`` takes a path relative to the Python application's public
directory, extracts the width and height from the image file, and returns an
<img> tag based on the expected public URL, using webhelpers.html.tags.image.

``get_dimensions()`` extracts the width and height from an image file using
PIL.  It uses an optional dimensions cache for speed.  The cache is a memory
dict.  Because the files are on disk they're independent of the thread or
process, so this is sufficiently thread-safe/multiprocess-safe.  It doesn't
recognize changes to the files unless you invalidate the cache or restart the
application, but it's assumed the files won't change frequently enough for this
to be an issue.

``open_image()`` returns a PIL Image object, or None if PIL doesn't recognize
the file type.

``make_thumb()`` creates a thumbnail of an image in the same directory as the
original.  The thumbnail is named FILENAME_STEM + "_thumb.jpg".

``get_thumb_path()`` returns the thumbnail path based on the original image
path, using the naming conventions of ``make_thumb``.

``make_pdf_thumbnail()`` and ``make_pdf_thumbnail2`` create a thumbnail image
of the first page of a PDF file.  The former depends on ImageMagick which uses
Ghostscript, the latter depends on Ghostscript directly.  The former seems to
be more reliable currently.


"""

import glob
import logging
import os
import re
import subprocess
import sys
import traceback
import warnings

import Image     # Python Imaging Library (PIL)

warn = logging.getLogger("multimedia").warn

# Suppress FutureWarning from PIL; we can't do anything about it.
warnings.filterwarnings('ignore', '.*return a long.*')

THUMB_PIL_TYPE = "JPEG"   # Thumbnail type; one of PIL's output formats.
THUMB_EXT = ".jpg"        # The filename extension for that type.

# Caches image dimensions for reuse.
_dimensions_cache = {}

RX_DECODER_NOT_AVAILABLE = re.compile( R"decoder .* not available" )

def static_image(relative_path, alt, **html_attrs):
    """Create an <img> tag for a path relative to the public directory.
       
    If keyword arg ``use_cache`` is false, don't use the global dimensions
    cache.
    """
    use_cache = html_attrs.pop("use_cache", True)
    if "width" not in html_attrs or "height" not in html_attrs:
        try:
            path = Path(config["pylons.paths"]["public_files"], relative_path)
            width, height = get_dimensions(path, use_cache)
        except IOError:
            pass
        else:
            if width:
                html_attrs.setdefault("width", width)
            if height:
                html_attrs.setdefault("height", height)
    # @@MO Temporary kludge due to url_for ambiguity in Routes 1.
    src = "/" + relative_path
    return image(src, alt=alt, **html_attrs)


def open_image(image_path):
    """Open an image file in PIL, return the Image object.
       Return None if PIL doesn't recognize the file type.
    """
    try:
        im = Image.open(image_path)
    except IOError, e:
        if str(e) == "cannot identify image file":
            return None
        else:
            raise
    except:
        m = "caught exception identifying '%s', assuming non-image:\n%s"
        e = traceback.format_exc()
        warn(m, image_path, e)
        return None
    return im

def make_thumb(image_path, width):
    """Make a thumbnail and save it in the same directory as the original.

       See get_thumb_path() for the arguments.
       @return The thumbnail filename, or None if PIL
           didn't recognize the image type.

       Does NOT work with PDF originals; use make_thumb_from_pdf for those.
    """
    dst = get_thumb_path(image_path, width)
    im = open_image(image_path)
    if im is None:
        return None
    orig_width, orig_height = im.size
    height = choose_height(width, orig_width, orig_height)
    if im.mode == 'P':
        im = im.convert()   # Convert GIF palette to RGB mode.
    try:
        im.thumbnail((width, height), Image.ANTIALIAS)
    except IOError, e:
        reason = str(e)
        if RX_DECODER_NOT_AVAILABLE.search(reason):
            return None   # PIL error, cannot thumbnail.
        else:
            raise
    im.save(dst, THUMB_PIL_TYPE)
    return dst

def choose_height(new_width, width, height):
    """Return the height corresponding to 'new_width' that's proportional
       to the original size.
    """
    proportion = float(height) / float(width)
    return int(new_width * proportion)

def get_dimensions(image_path, use_cache=False):
    """Return the width and height of an image.
       Returns (None, None) if PIL doesn't recognize the file type.

       @param use_cache bool If true, use the cached dimensions if
       available.  This cuts down on filesystem accesses, but the cache may
       be wrong if the image has changed.  If false, update the cache anyway
       so it's correct.

       @exc IOError raised by PIL if the image file is missing or you don't
       have read permission for it.
    """
    image_path = str(image_path)   # Don't need a path object.
    if use_cache and image_path in _dimensions_cache:
        return _dimensions_cache[image_path]
    im = open_image(image_path)
    if im is None:
        size = (None, None)
    else:
        size = im.size
    _dimensions_cache[image_path] = size
    return size

def changed(image_path=None):
    """Delete all cached data regarding this path because the file has
       changed.  If arg is unspecified or None, delete all cached data
       for all paths.
    """
    if image_path is None:
        _dimensions_cache.clear()
        return
    if image_path in _dimensions_cache:
        del _dimensions_cache[image_path]

def get_thumb_path(image_path, width):
    """Return the thumbnail path for the given image.
       
       @parm image_path str The original image filename.
       @param width int The thumbnail width in pixels.
       @return path The thumbnail path.
       For "a/foo.jpg", returns path("a/foo_thumbWIDTH.jpg").
       The return value always ends with THUMB_EXT regardless of the original
       extension.
    """
    dir, old_name = os.path.split(image_path)
    base, ext = os.path.splitext(old_name)
    new_name = "%s_thumb%d%s" % (base, width, THUMB_EXT)
    return os.path.join(dir, new_name)

def test():
    print "Height for 600x480 @ width 200 is", choose_height(200, 600, 480)
    print "Path 200 for a/foo.jpg is", get_thumb_path('a/foo.jpg', 200)
    print "Path 200 for a/foo.png is", get_thumb_path('a/foo.png', 200)

if __name__ == "__main__":  test()

def make_pdf_thumbnail(path, width):
    """Make a thumbnail from a PDF file.

       @parm image_path str The original image filename.
       @param width int The thumbnail width in pixels. (Will be approximate.)
       @return path The thumbnail path.
       For "a/foo.jpg", returns path("a/foo_thumbWIDTH.jpg").
       The return value always ends with THUMB_EXT regardless of the original
       extension.

       Requires the "imagemagick" package to be installed.  By Mike Orr.
    """
    width_str = str(width)
    dir, name = os.path.split(path)
    base, ext = os.path.splitext(name)
    newbase = "%s_thumb%s" % (base, width_str)
    dst = os.path.join(dir, newbase + THUMB_EXT)

    def page(n):
        """Return the filename for page n's thumbnail, n >= 0.
           'n' may also be a string (e.g., "*" for wildcard patterns).
           If 'n' is None, return value has no page suffix.
        """
        if n is not None:
            suffix = "-%s" % n
        else:
            suffix = ""
        return os.path.join(dir, newbase + suffix + THUMB_EXT)

    trashcan = open("/dev/null", "w")
    cmd = ["/usr/bin/convert", "-geometry", width_str, path, dst]
    status = subprocess.call(cmd, shell=False, stderr=trashcan)
    if status:
        warn("make_pdf_thumbnail subcommand exited with status %s: %s", 
            status, cmd)
    trashcan.close()
    found = False
    if os.path.exists(dst):
        found = True
    page0_fn = page(0)
    other_files = glob.glob(page("*"))
    for fn in other_files:
        if fn == page0_fn and not found:
            os.rename(fn, dst)
            found = True
        else:
            os.remove(fn)
    if found:
        return dst
    else:
        return None

def make_pdf_thumbnail2(path, width):
    """Make a thumbnail from a PDF file.

       This version uses just ghostscript, rather than ImageMagik
       -- chb

       @parm image_path str The original image filename.
       @param width int The thumbnail width in pixels. (Will be approximate -- assumes 8.5in wide paper.)
       @return path The thumbnail path.
       For "a/foo.jpg", returns path("a/foo_thumbWIDTH.jpg").
       The return value always ends with THUMB_EXT regardless of the original
       extension.

       Requires ghostscript to be installed.  By Chris Barker.
    """
    width_str = str(width)
    dir, name = os.path.split(path)
    base, ext = os.path.splitext(name)
    newbase = "%s_thumb%s" % (base, width_str)
    dst = os.path.join(dir, newbase + THUMB_EXT)

    def page(n):
        """Return the filename for page n's thumbnail, n >= 0.
           'n' may also be a string (e.g., "*" for wildcard patterns).
           If 'n' is None, return value has no page suffix.
        """
        if n is not None:
            suffix = "-%s" % n
        else:
            suffix = ""
        return os.path.join(dir, newbase + suffix + THUMB_EXT)

    trashcan = open("/dev/null", "w")
    
    ## A few settable options
    if THUMB_EXT == ".jpg":
        filetype = "jpeg" # jpeg
    elif THUM_EXT == ".png":
        filetype = "png16m" # 24 bit png
    else:
        filetype = "jpeg" # should this be default
    
    gs_path = "/usr/local/bin/gs"
    ps_cmd = "save pop currentglobal true setglobal false/product where{pop product(Ghostscript)search{pop pop pop revision 600 ge{pop true}if}{pop}ifelse}if{/pdfdict where{pop pdfdict begin/pdfshowpage_setpage[pdfdict/pdfshowpage_setpage get{dup type/nametype eq{dup/OutputFile eq{pop/AntiRotationHack}{dup/MediaBox eq revision 650 ge and{/THB.CropHack{1 index/CropBox pget{2 index exch/MediaBox exch put}if}def/THB.CropHack cvx}if}ifelse}if}forall]cvx def end}if}if setglobal"
    cmd = [gs_path, "-dSAFER","-dBATCH","-dNOPAUSE","-dLastPage=1","-dTextAlphaBits=4"]
    cmd.append("-sDEVICE=%s"%filetype)
    #dpi  = int(width / 8.5) ## this assumes an 8.5in wide piece of paper.
    dpi = 20
    cmd.append("-r%i"%dpi)
    
    cmd.append("-sOutputFile=%s"% dst)
    cmd.extend(("-c", ps_cmd, "-f"),)
    cmd.append(path)
    
    ## the desired command string
    ## gs -dSAFER -dBATCH -dNOPAUSE -r150 -sDEVICE=jpeg -dTextAlphaBits=4 -sOutputFile=$1-%02d.jpg $1
    status = subprocess.call(cmd, shell=False) #, stdout=trashcan, stderr=trashcan)
    if status:
        warn("make_pdf_thumbnail subcommand exited with status %s: %s", 
            status, cmd)
    trashcan.close()
    found = False
    if os.path.exists(dst):
        return dst
    else:
        return None
    

def get_pdf_text(path):
    raise NotImplementedError

def get_word_text(path):
    raise NotImplementedError


if __name__ == "__main__":
    import optparse
    logging.basicConfig()
    parser = optparse.OptionParser(usage="%prog PDF_FILE")
    opts, args = parser.parse_args()
    if len(args) != 1:
        parser.error("wrong number of command-line arguments")
    source_file = args[0]
    
    width = 200
    dst = make_pdf_thumbnail2(source_file, width)
    print "Thumbnail made:", dst

#ps_cmd = "save pop currentglobal true setglobal false/product where{pop product(Ghostscript)search{pop pop pop revision 600 ge{pop true}if}{pop}ifelse}if{/pdfdict where{pop pdfdict begin/pdfshowpage_setpage[pdfdict/pdfshowpage_setpage get{dup type/nametype eq{dup/OutputFile eq{pop/AntiRotationHack}{dup/MediaBox eq revision 650 ge and{/THB.CropHack{1 index/CropBox pget{2 index exch/MediaBox exch put}if}def/THB.CropHack cvx}if}ifelse}if}forall]cvx def end}if}if setglobal"

#gs -dLastPage=1 -dTextAlphaBits=4 -dGraphicsAlphaBits=4 -dNOPAUSE -dBATCH -sDEVICE=jpeg -r20 -sOutputFile=Chem_Sheet_LPG.jpg -c "save pop currentglobal true setglobal false/product where{pop product(Ghostscript)search{pop pop pop revision 600 ge{pop true}if}{pop}ifelse}if{/pdfdict where{pop pdfdict begin/pdfshowpage_setpage[pdfdict/pdfshowpage_setpage get{dup type/nametype eq{dup/OutputFile eq{pop/AntiRotationHack}{dup/MediaBox eq revision 650 ge and{/THB.CropHack{1 index/CropBox pget{2 index exch/MediaBox exch put}if}def/THB.CropHack cvx}if}ifelse}if}forall]cvx def end}if}if setglobal" -f Chem_Sheet_LPG.pdf

#gs -dTextAlphaBits=4 -dGraphicsAlphaBits=4 -dNOPAUSE -dBATCH -sDEVICE=png16m -r9.06531732174037 -sOutputFile=thb%d.png -c "save pop currentglobal true setglobal false/product where{pop product(Ghostscript)search{pop pop pop revision 600 ge{pop true}if}{pop}ifelse}if{/pdfdict where{pop pdfdict begin/pdfshowpage_setpage[pdfdict/pdfshowpage_setpage get{dup type/nametype eq{dup/OutputFile eq{pop/AntiRotationHack}{dup/MediaBox eq revision 650 ge and{/THB.CropHack{1 index/CropBox pget{2 index exch/MediaBox exch put}if}def/THB.CropHack cvx}if}ifelse}if}forall]cvx def end}if}if setglobal" -f Chem_Sheet_LPG.pdf


