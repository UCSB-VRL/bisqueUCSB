# Preliminary code for webhelpers.misc.sanitize_filename().


BAD_FILENAME_CHAR_RX = re.compile(R"[^A-Za-z0-9_-]")

def strip_path(filename):
    """Delete the directory prefix from 'filename' if present.
    Use the code below.
    """

def sanitize_filename(filename, bad_char_rx=BAD_FILENAME_CHAR_RX, 
    repl="_", exts=None, prefix=None, suffix=None, lower=True):
    """Sanitize filname helper for uploaded files.

    - Strip directory prefix.
    - Lowercase filename if lower=True.
    - Split base name and extension. (Allow a few double extensions
    like ".tar.gz" and ".tar.bz2")
    - Deny if extension not in ``exts`` (a list/tuple/set of strings).
    - If ``bad_char_rx`` and ``repl`` are both not None, apply re.sub to the 
    base name and extension separately. 
    - Add prefix and suffix to the base name if specified.
    - Join the base and extension and return the new filename.
    
    What about collision with an existing file? Could pass a list of existing
    files, and it could make a numbered suffix or deny it in that case.
    """
    filename = strip_path(filename)

def old_sanitize_filename(filename):
    """Sanitize unsafe characters in upload filename. 
    Delete directory prefix too."""

    filename = unidecode(filename)
    filename = Path(filename).name
    # On Unix, strip Windows-style directory prefix manually.
    slash_pos = filename.rfind("\\")
    if slash_pos != -1:
        filename = Path(filename[slash_pos+1:])
    # On Windows, strip Unix-style directory prefix manually.
    slash_pos = filename.rfind("/")
    if slash_pos != -1:
        filename = Path(filename[slash_pos+1:])
    # Convert unsafe characters.
    repl = "_"
    orig_ext = filename.ext
    stem = BAD_FILENAME_CHAR_RX.sub(repl, filename.stem)
    ext = BAD_FILENAME_CHAR_RX.sub(repl, filename.ext)
    if orig_ext.startswith(".") and ext.startswith(repl):
        ext = "." + ext[len(repl):]
    return stem + ext
