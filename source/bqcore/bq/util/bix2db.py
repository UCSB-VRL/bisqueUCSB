###############################################################################
##  Bisquik                                                                  ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007 by the Regents of the University of California     ##
##                            All rights reserved                            ##
##                                                                           ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions are    ##
## met:                                                                      ##
##                                                                           ##
##     1. Redistributions of source code must retain the above copyright     ##
##        notice, this list of conditions, and the following disclaimer.     ##
##                                                                           ##
##     2. Redistributions in binary form must reproduce the above copyright  ##
##        notice, this list of conditions, and the following disclaimer in   ##
##        the documentation and/or other materials provided with the         ##
##        distribution.                                                      ##
##                                                                           ##
##     3. All advertising materials mentioning features or use of this       ##
##        software must display the following acknowledgement: This product  ##
##        includes software developed by the Center for Bio-Image Informatics##
##        University of California at Santa Barbara, and its contributors.   ##
##                                                                           ##
##     4. Neither the name of the University nor the names of its            ##
##        contributors may be used to endorse or promote products derived    ##
##        from this software without specific prior written permission.      ##
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS "AS IS" AND ANY ##
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED ##
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, ARE   ##
## DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR  ##
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL    ##
## DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS   ##
## OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)     ##
## HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,       ##
## STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN  ##
## ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE           ##
## POSSIBILITY OF SUCH DAMAGE.                                               ##
##                                                                           ##
###############################################################################
"""
SYNOPSIS
========


DESCRIPTION
===========

"""

import traceback, sys
from time import strptime
from StringIO import StringIO
from datetime import datetime, time, date
from lxml import etree

from bq import blob_service
from bq import image_service
from bq import data_service

from bq.exceptions import BQException
BIXLOG='biximport.log'


class BIXError(BQException):
    pass

import logging
log = logging.getLogger('bq.bix2db')

class BIXImporter(object):
    """Converter class for parsing Bix file and coverting to bisquik tags
    """
    pmap = {'public': 'published',
            'private': 'private',
            'group': 'private' }



    def __init__(self, updir, **kw):
        self.upload_dir= updir
        self.flags = kw
        self.permission_flag = 'private'
        self.image_info = {}

    def fullname(self, name):
        if name[0] != '/':
            return '/'.join([self.upload_dir, name])
        return name


    def save_file (self, fn, **kw):
        '''save a file in the image server and return info'''
        with open(self.fullname(fn), 'rb') as src:
            fr = etree.Element ('file', name=fn, permission=str(self.permission_flag) )
            return blob_service.store_blob(fr, src )


    def save_image (self, fn, **kw):
        '''save a file in the image server and return info'''
        log.debug ("Store new image: " + fn + " " + str(self.image_info))

        self.resource = etree.Element('image', name=fn, permission = str(self.permission_flag))

        with open(self.fullname(fn), 'rb') as src:
            self.resource = blob_service.store_blob(self.resource, src )

        if 'uri' in self.resource.attrib:
            self.import_files[fn] = self.resource.get('uri')
        else:
            log.debug ("Image service could not create image %s" % fn)
            raise BIXError ("Image service could not create image %s" % fn)


    def process_bix(self, bixfile, name_map = {} ):
        if bixfile == None or bixfile == '': return '',''
        self.import_files = name_map
        fullname = self.fullname(bixfile)
        log.debug ("BIX:" + fullname)

        self.resource = None
        et = etree.parse(fullname)
        # Scan tree for special nodes.

        try:
            preprocess = [ 'image_visibility', 'image_plane_order', 'image_num_z', 'image_num_t', 'filename' ]

            for tag in preprocess:
                log.debug ('trying tag:' + tag)
                items = et.getroot().xpath ('./item[name="%s"]' % tag )
                log.debug ('got ' + str(items))
                if items and hasattr(self, 'tag_' + tag):
                    handler = getattr(self, 'tag_' + tag)
                    handler(items[0])

            rr = self.save_file (bixfile)
            self.import_files[bixfile] = rr.get('uri')
            self.import_files['BIX'] = rr.get('uri')



            e = etree.SubElement(self.resource, 'tag', name = 'attached-file')
            etree.SubElement (e, 'tag', name='original-name', value=bixfile)
            etree.SubElement (e, 'tag', name='url', type='file', value=rr.get('uri') )

            # Process all other nodes
            for config in et.getroot().getiterator('config'):
                etree.SubElement (self.resource,
                                  'tag', name='image_type', value =config.get ('type'))

            for item in et.getroot().getiterator('item'):
                name = item[0].text                # item[0] == <name>
                value = self.parseValue(item[1])   # item[1] == <value>
                if name in preprocess:
                    continue
                if hasattr(self, 'tag_' + name):
                    # Use a special tag parser
                    handler = getattr(self, 'tag_' + name)
                    handler(item)
                else:
                    # BIX Files come encoded in UTF-8
                    # DO not change encoding here.
                    t = etree.SubElement(self.resource, 'tag',
                                         name=name,
                                         value=value)
                    log.debug ('tag ' + name +':' + value)

            if self.permission_flag == 'published':
                for child in self.resource.iter():
                    child.set('permission', self.permission_flag)
            #  Should check if we have local changes (redirect to DS)
            log.debug ("update image" + etree.tostring(self.resource))
            data_service.update (self.resource)
        except BIXError, e:
            log.error ("Exception" + e)
        except Exception:
            log.exception ("BixImport")
        if  self.resource is None:
            return '', ''

        #try:
        #    bixlog = open(BIXLOG, 'a+')
        #    bixlog.write(str(self.import_files))
        #    bixlog.write("\n")
        #    bixlog.close()
        #except IOError, (errno, strerr):
        #    log.error ("can't append to bixlog: %s" % (strerr) )
        #except Exception:
        #    log.error ("Upexpected %s " % ( sys.exc_info()[0]))
        del et
        return self.resource.get('name'), self.resource.get('uri')

    def parseValue(self, vs):
        if not len(vs): return vs.text
        for v in vs:
            if hasattr(self, 'parse_' + v.tag):
                parser = getattr(self, 'parse_' + v.tag)
                return parser(v)
            else:
                raise KeyError ('No parser available for '+ v.tag)

    def parse_datetime(self, v):
        '''return parsed datetime.. attributes of v must be compatible
        with datetime
        '''
        return str(datetime(**dict([ (x,int(y)) for x,y in v.attrib.items() ])))

    def parse_date(self, v):
        '''return parsed datetime.. attributes of v must be compatible
        with datetime
        '''
        return str(date(**dict([ (x,int(y)) for x,y in v.attrib.items() ])))

    def parse_time(self, v):
        '''return parsed datetime.. attributes of v must be compatible
        with datetime
        '''
        return str(time(**dict([ (x,int(y)) for x,y in v.attrib.items() ])))


    #####
    ## Special tags are listed below
    def tag_dataset(self, item, **kw):
        '''add the listed image to dataset  v'''
        pass

    def tag_filemetadata(self, item, **kw):
        '''Deal with long metadata string stored in meta'''
        pass

    def tag_filename(self, item, **kw):
        '''associate the values from the parsed file with image v'''

        # Import the file and set the resource.
        fn = item[1].text
        log.debug ("filename: " + fn + ':')
        self.filename = fn
        self.save_image(fn)

    def tag_image_visibility(self, item, **kw):
        '''set visibability (public, private) for image v'''
        perm = item[1].text
        log.debug ('setting permission by ' + perm)
        self.permission_flag = BIXImporter.pmap.get(perm, 'private')

    def tag_microtubule_tracks(self, item, **kw):
        self.tag_graphics_annotation(item, **kw)

    def tag_graphics_annotation(self, item, **kw):
        '''parse the embedded gobjects'''
        v = item[1].text
        log.debug ("BIX: parsing '%s' " % ( v ))
        if v:
            bfi = etree.parse (StringIO(v))
            for g in bfi.getroot():
                log.debug ("adding to " + str(type(self.resource)))
                self.resource.append(g)
                #data_service.append_resource(self.resource, tree = g)

#    def tag_microtubule_track_file(self, item, **kw):
#        '''special uploaded files manual mt tracks'''
#        v = item[1].text
#        if v:
#            import bisquik.importer.trackimport as trackimport
#            imagemeta = self.parse_image_meta()
#            files = v.split(';')
#            filepaths = []
#            for f in files:
#                path = self.fullname(f)
#                filepaths.append(path)
#                info = self.save_file(f)
#
#            bfis, missing = trackimport.trackimport(filepaths, imagemeta)
#            for bfi in bfis:
#                for tb in bfi:
#                    data_service.append_resource(self.resource, tree = tb)
#                    #log.debug ("BIX: adding tube" + tube.name)
#                    #tube.save()

    def tag_attachments(self, items, **kw):
        attachments = items[1].text
        if attachments:
            files = attachments.split(';')
            filepaths = []
            for f in files:
                path = self.fullname(f)
                filepaths.append(path)
                rr = self.save_file(f)

                e = etree.Element('tag', name='attached-file' )
                etree.SubElement(e, 'tag', name='original-name', value=str(f))
                etree.SubElement(e, 'tag' ,name='url', type='file', value=rr.get('uri'))

                #data_service.append_resource(self.resource, tree=e)
                self.resource.append(e)


    def tag_image_plane_order(self, item, **kw):
        '''set image_plane_order for image v'''
        s = item[1].text
        if s.lower() != 'auto':
            log.debug ('setting image_plane_order to ' + s)
            self.image_info['dimensions'] = s

    def tag_image_num_z(self, item, **kw):
        '''set image_num_z for image v'''
        s = item[1].text
        if s.lower() != '0':
            log.debug ('setting image_num_z to ' + s)
            self.image_info['image_num_z'] = s

    def tag_image_num_t(self, item, **kw):
        '''set image_num_t for image v'''
        s = item[1].text
        if s.lower() != '0':
            log.debug ('setting image_num_t to ' + s)
            self.image_info['image_num_t'] = s

    def parse_image_meta(self):
        doc = image_service.meta(self.resource.get('src'))
        log.debug("bix2db " + self.resource.get('src'))
        response = etree.parse(StringIO(doc))
        meta = []
        image = response.getroot()[0]

        plane_count = image.xpath('./tag[@name="image_num_p"]')
        if plane_count:
            meta = [0] * int(plane_count[0].attrib['value'])
            planes = image.xpath('./tag[@name="time_planes"]')
            if planes:
                for plane in planes[0]:
                    indx = int(plane.attrib['index'])
                    val  = plane.text
                    #log.debug("bix2db " + str(indx) + ':' + val)
                    meta[indx] = datetime(*strptime(val, "%Y-%m-%d %H:%M:%S")[0:6])

        log.debug('bix2db meta:' + str(meta))
        return meta

    # @classmethod
    # def reload_log(logfile = BIXLOG):
    #     # Rename original files and re-execute import
    #     biximport = BIXImporter('./', reimport = True)
    #     for line in open(logfile):
    #         exec ('file_map = ' + line)
    #         for orig, local in file_map:
    #             print orig, local
    #             shutils.move (local, orig)
    #         biximport.process_bix(file_map['BIX'])





if __name__ == '__main__':
    import sys
#    b2b = BIX2Bisquik('')
#    b2b.process_bix(sys.argv[1])

    et = etree.parse(sys.argv[1])
    for item in et.getroot().getiterator('item'):
        print item
