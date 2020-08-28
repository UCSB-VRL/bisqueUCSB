#########################################
###    Botanicam Module for Bisque    ###
#########################################
import os
import tables
import time
import sys
import logging
import zipfile
from lxml import etree
import numpy as np
from optparse import OptionParser
from bqapi.comm import BQSession, BQCommError
from bqapi.bqfeature import Feature, ParallelFeature, FeatureResource, FeatureError
from sklearn.externals import joblib

#Constants
PARALLEL                        = True
NUMBER_OF_THREADS               = 4 #number of concurrent requests
IMAGE_BLOCK_SIZE                = 64 #block size of the image to have features extracted from
MAX_NUM_OF_FEATURES_PER_REQUEST = 500
IMAGE_SERVICE                   = 'image_service'
FEATURES_SERVICE                = 'features'
FEATURE_NAME                    = 'HTD'
FEATURE_TABLE_DIR               = 'Outputs'
TEMP_DIR                        = 'Temp'
MODEL_QUERY                     = {'tag_query':'"module_identifier":"Botanicam" AND "Classification Method":"Bush Descriptor"',
                                   'tag_order':'@ts:desc',
                                   'limit':'1',
                                   'wpublic':'1'}

DEMO_MODEL_XML = ''
DEMO_MODEL_PATH = ''

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('bq.modules')


class BotanicamError(Exception):
    
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message
        

def unzip_model_file(path):
    """
        Unzips model file and places it in
        a directory containing all the zip 
        file's files.
        
        @param: path to zip file
        
        @return: path to the unzipped dir
    """
    with zipfile.ZipFile(path) as zfile:
        (dirname, ext) = os.path.splitext(path)
        for name in zfile.namelist():
            #idenfity model name
            if not os.path.splitext(name)[1]:
                model_name = name
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            zfile.extract(name, dirname)
        return os.path.join(dirname, model_name)


def image_tiles(bqsession, image_service_url, tile_size=64):
    """
        Breaks an image service request into non overlapping tiles
        
        @param: bqsession - initalized BQSession
        @param: image_service_url - url to the image serivce resource
        @param: tile_size - the size of the tiles in pixels the image 
        will be broken into (default: 64)
        
        @yield: urls for images service that tile the entire image
    """
    dims = bqsession.fetchxml(image_service_url, dims='')
    x = int(dims.xpath('//tag[@name="image_num_x"]')[0].attrib[ 'value'])
    y = int(dims.xpath('//tag[@name="image_num_y"]')[0].attrib[ 'value'])
    
    for ix in range(int(x/tile_size)-1):
        for iy in range(int(y/tile_size)-1):
            yield bqsession.c.prepare_url(image_service_url, tile='0,%s,%s,%s' % (str(ix), str(iy), str(tile_size)))


def extract_bush_feature(bqsession, image_url):
    """
        Makes a feature request for the bush feature which is 
        tiled blocks of the image with Homogenious Texture 
        Descriptor (HTD) extracted from them.
        
        @param: bqsession - initalized BQSession
        @param: query - dataset value list or data_service query
        
        @return: hdf5 filename containing all the features
        from the images in the query
    """
    resource_list = []
    for url in image_tiles(bqsession, image_url, tile_size=IMAGE_BLOCK_SIZE):
        resource_list.append(FeatureResource(image=url))
    if PARALLEL:
        feature = ParallelFeature()
    else:
        feature = Feature()
        
    return feature.fetch_vector(bqsession, FEATURE_NAME, resource_list)
    

class Botanicam(object):
    """
        Botanicam Model
    """

    def mex_parameter_parser(self, mex_xml):
        """
            Parses input of the xml and add it to BotanicamTrainer's options attribute
            
            @param: mex_xml
        """
        mex_inputs = mex_xml.xpath('tag[@name="inputs"]')
        if mex_inputs:
            for tag in mex_inputs[0]:
                if tag.tag == 'tag' and tag.attrib['type'] != 'system-input':
                    log.debug('Set options with %s as %s'%(tag.attrib['name'],tag.attrib['value']))
                    setattr(self.options,tag.attrib['name'],tag.attrib['value'])
        else:
            log.debug('BotanicamFS: No Inputs Found on MEX!')

    def validateInput(self):
        """
            Parses input of the xml and add it to Botanicam's options attribute
            
            @param: mex_xml
        """        
        if (self.options.mexURL and self.options.token): #run module through engine service
            return True
        
        if (self.options.user and self.options.pwd and self.options.root): #run module locally (note: to test module)
            return True
        
        log.debug('Botanicam: Insufficient options or arguments to start this module')
        return False


    def setup(self):
        """
            Fetches the mex, appends input_configurations to the option
            attribute of Botanicam and looks up the model on bisque to 
            classify the provided resource.
        """
        log.debug('Initializing Mex...')
        if (self.options.user and self.options.pwd and self.options.root):
            self.bqSession = BQSession().init_local( self.options.user, self.options.pwd, bisque_root=self.options.root)
            self.options.mexURL = self.bqSession.mex.uri

        elif (self.options.mexURL and self.options.token):
            self.bqSession = BQSession().init_mex(self.options.mexURL, self.options.token)
        else:
            return
        
        self.mex_parameter_parser(self.bqSession.mex.xmltree)
        
        #finds and opens model file
        self.bqSession.update_mex('Initializing Classification Model...')
        log.debug('Forming Feature Requests...')

        
        #no options currently
        #combo = mex_xml.xpath('tag[@name="plant_part"]/@value')[0]
        combo = 'bush'
        if combo:
            if combo=='bush':
                MODEL_QUERY['tag_query'] = '"module_identifier":"Botanicam" AND "Classification Method":"Bush Descriptor"'
            elif combo=='leaf':
                MODEL_QUERY['tag_query'] = '"module_identifier":"Botanicam" AND "Classification Method":"Leaf Descriptor"'
            else:
                raise BotanicamError('The incorrect model type was found -> Model Type: %s'%combo)
        else:
            raise BotanicamError('No model type was choosen')
        
        query_xml = self.bqSession.fetchxml('/data_service/file', **MODEL_QUERY)

        self.options.model_url = None
        if len(query_xml)>0:
            try:
                model_url = query_xml[0].attrib['uri']
                self.options.model_url = model_url
                log.debug('Fetching Model @ %s' % model_url)
                self.model_xml = self.bqSession.fetchxml(model_url, view='deep')
                self.model_path = os.path.join(self.options.stagingPath, 'model')
                model = self.bqSession.load(model_url)
                model_url = self.bqSession.service_url('blob_service', path=model.resource_uniq)
                self.bqSession.fetchblob(model_url, path=self.model_path+'.zip')
                with zipfile.ZipFile(self.model_path+'.zip') as dirzip:
                    dirzip.extractall(self.model_path)
            except BQCommError:
                raise BotanicamError('Model file was not found! Ask admin to set the correct model file')
        else: #run demo classifier model store in the module
            raise BotanicamError('No model file was found. Ask your admin to train a new model with \
             the Botanicam Trainer.')

        self.bqSession.update_mex('Initialized...')
        log.debug('Botanicam: image URL: %s, mexURL: %s, stagingPath: %s, token: %s' % (self.options.image_url, self.options.mexURL, self.options.stagingPath, self.options.token))
        

    def run(self):
        """
            The core of the Botanicam Module
            
            Requests features on the image provided. Classifies each tile
            and picks a majority among the tiles. 
        """
        #parse requests
        self.bqSession.update_mex('Calculating Features...')
        log.debug('Forming Feature Requests...')
        #get rectanle gobjects for roi
        r_xml = self.bqSession.fetchxml(self.options.mexURL, view='deep')

        rectangles = r_xml.xpath('//tag[@name="inputs"]/tag[@name="image_url"]/gobject[@name="roi"]/rectangle')
        image_xml = self.bqSession.fetchxml(self.options.image_url)
        image_url = self.bqSession.service_url('image_service',path=image_xml.attrib['resource_uniq'])
        if rectangles: #On chooses the first rectangle
            #construct operation node
            x1 = int(float(rectangles[0][0].attrib['x']))
            y1 = int(float(rectangles[0][0].attrib['y']))
            x2 = int(float(rectangles[0][1].attrib['x']))
            y2 = int(float(rectangles[0][1].attrib['y']))
            log.debug('Adding Crop: roi=%s,%s,%s,%s' % (x1, y1, x2, y2))
            image_url = self.bqSession.c.prepare_url(image_url, roi='%s,%s,%s,%s' % (x1, y1, x2, y2))
            
        try:
            feature_vectors = extract_bush_feature(self.bqSession, image_url)
        except FeatureError as e:
            raise BotanicamError(str(e))
                
        #parse features
        self.bqSession.update_mex('Classifying Results...')
        log.debug('Classifying Results...')
        results= []
        pca = joblib.load(os.path.join(self.model_path,'pca_model'))
        clf = joblib.load(os.path.join(self.model_path,'svm_model'))
        
        for f in feature_vectors:
            f_norm = pca.transform(f)
            results.append(int(clf.predict(f_norm)))
        

        class_count = np.bincount(np.array(results))
        self.class_number = np.argmax(class_count)
        self.confidence = float(class_count[self.class_number])/np.sum(class_count)
        log.debug('Found Class %s'%str(self.class_number))


    def teardown(self):
        """
            Posting results to the mex
        """
        self.bqSession.update_mex('Returning results...')
        log.debug('Returning results...')
        tag_list = self.model_xml.xpath('tag[@name="Classes"]/tag[@value="%s"]'%str(self.class_number))[0]
        
        outputTag = etree.Element('tag', name='outputs')
        outputSubTag = etree.SubElement(outputTag, 'tag', name='summary')
        
        if self.options.model_url:
            etree.SubElement(outputSubTag, 'tag',name='Model File', value=self.options.model_url, type='url')
        else:
            etree.SubElement(outputSubTag, 'tag',name='Model File', value='Internal Model File')
        
        etree.SubElement(outputSubTag, 'tag',name='Class', value=str(self.class_number))
        
        query = []
        for t in tag_list:
            etree.SubElement(outputSubTag, 'tag', name=t.attrib['name'], value=t.attrib['value'])
            query.append('"%s":"%s"'%( t.attrib['name'], t.attrib['value']))
        query = ' & '.join(query)
        etree.SubElement( outputSubTag, 'tag', name='confidence', value=str(self.confidence))

        etree.SubElement(outputTag, 'tag', name='similar_images', value=query, type='browser')

        self.bqSession.finish_mex(tags = [outputTag])
        log.debug('FINISHED')
        self.bqSession.close()


    def main(self):
        """
            The main function that runs everything
        """
        log.debug('sysargv : %s' % sys.argv )
        
        parser = OptionParser()

        parser.add_option( '--image_url'   , dest="image_url")
        parser.add_option( '--mex_url'     , dest="mexURL")
        parser.add_option( '--module_dir'  , dest="modulePath")
        parser.add_option( '--staging_path', dest="stagingPath")
        parser.add_option( '--bisque_token', dest="token")
        parser.add_option( '--user'        , dest="user")
        parser.add_option( '--pwd'         , dest="pwd")
        parser.add_option( '--root'        , dest="root")

        (options, args) = parser.parse_args()

        try: #pull out the mex
            
            if not options.mexURL:
                options.mexURL = sys.argv[1]
            if not options.token:
                options.token = sys.argv[2]
                
        except IndexError: #no argv were set
            pass
        
        if not options.stagingPath:
            options.stagingPath = ''
        
        log.debug('\n\nPARAMS : %s \n\n Options: %s'%(args, options))
        self.options = options
        
        if self.validateInput():
            
            try: #run setup and retrieve mex variables
                self.setup()
            except Exception, e:
                log.exception("Exception during setup")
                self.bqSession.fail_mex(msg = "Exception during setup: %s" %  str(e))
                return
            
            try: #run module operation
                self.run()
            except BotanicamError, e:
                log.exception("Exception during run")
                self.bqSession.fail_mex(msg = "Exception during run: %s" % str(e.message))
                return                
            except Exception, e:
                log.exception("Exception during run")
                self.bqSession.fail_mex(msg = "Exception during run: %s" % str(e))
                return

            try: #post module
                self.teardown()
            except Exception, e:
                log.exception("Exception during teardown %s")
                self.bqSession.fail_mex(msg = "Exception during teardown: %s" %  str(e))
                return

if __name__ == "__main__":
    Botanicam().main()
    
    