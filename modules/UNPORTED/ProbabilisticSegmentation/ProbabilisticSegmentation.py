import os
import sys
import getopt
from BQInterface import *


class ProbabilisticSegmentation:


       
    def main(self, client_server, imgurl, r, thresh, user=None, password=None):
    
        format = "tiff"
        cellcnt = ""
        cellurl = []
        cellcenter = ""
        dburl = ''
        cells = []
        
        OPT_IMAGEIN  = 'image.tiff'
        OPT_IMAGEOUT = ''
        OPT_CELLS    = 'cells.data'
        OPT_SEGCELL  = 'all'
        OPT_RESTART  = r
        OPT_THRESHOLD= thresh
        PATH = '../modules/ProbabilisticSegmentation/'
        #PATH = './'
        
        if (OPT_RESTART != "None"):
            OPT_RESTART = '-r ' + OPT_RESTART
        else:
            OPT_RESTART = ''
         
        if (OPT_THRESHOLD != "None"):
            OPT_THRESHOLD = '-thresh'
        else:
            OPT_THRESHOLD = ''
            
        
        currentp = os.getcwd()
        os.chdir(PATH)
        
        
        try:
            bq = BQInterface()
            # Read image from url, store as binary in a temp file
            imgdata = bq.getImage(imgurl, user, password)
            image = bq.getImagePixels(imgdata['src'], format, user, password)
            tmpfile = open(OPT_IMAGEIN, 'wb')
            tmpfile.write(image)
            tmpfile.close()
            
            # Grabs all Gobject points
            gobs = bq.getGObjects(imgurl, 'point', user, password)
            
            cellcenters = [];
            for cell in gobs:
                cellcenters.append(bq.getGObjectVertices(cell))
            
            if len(cellcenters) > 0:
                tmpfile = open(OPT_CELLS, 'w')
                tmpfile.write(str(len(cellcenters)) + '\n')
                for cell in cellcenters:
                    for v in cell:
                        tmpfile.write(repr(int(float(v['x']))) + ',' + repr(int(float(v['y']))) + ',' + repr(int(float(v['z']))) + '\n')
                tmpfile.close()
                
                
                # Call the Solver program
                cmd = './RWalk  -in ' + OPT_IMAGEIN + ' -cells ' + OPT_CELLS + ' -seg all ' + OPT_THRESHOLD + ' ' +  OPT_RESTART
                print cmd
                #print os.system('pwd')
                os.system(cmd)
        
        
                newimg = bq.newImageFile(client_server, 'image/cell0/stack.tif', 'tif', user, password);
                #print newimg
                segtag = bq.addTag('reference', imgurl, 'string')
                txt = bq.postTag(newimg, segtag, user, password);
                segtag = bq.addTag('probabilistic_segmented', newimg, 'string')
                txt = bq.postTag(imgurl, segtag, user, password);
            
            os.chdir(currentp)
        except:
            os.chdir(currentp)

        
    

