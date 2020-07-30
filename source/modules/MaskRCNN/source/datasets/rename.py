import glob, os

def rename(dir, pattern, titlePattern):
    initial_count = 0
    for pathAndFilename in glob.iglob(os.path.join(dir, pattern)):
        title, ext = os.path.splitext(os.path.basename(pathAndFilename))
        # Use a count instead of string as title
        initial_count = initial_count + 1
        title = str(initial_count)
        os.rename(pathAndFilename, 
                  os.path.join(dir, titlePattern % title + ext))


# Usage: ("Base folder", "file type", "target name format")
bdir = "C:/Users/Karma/Documents/workspace/naviz/mrcnn/datasets/windspect-v100/img"
fold = os.path.join(bdir, "flaking/val")
patn = r'flk-vv-%s'
rename(fold, r'*.jpg', patn)

