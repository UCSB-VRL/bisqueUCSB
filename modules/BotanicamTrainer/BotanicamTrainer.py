#################################################
###    Botanicam Trainer Module for Bisque    ###
#################################################
import os
import re
import tables
import sys
import time
import urllib
import logging
import itertools
from lxml import etree
from sklearn import svm
from sklearn.decomposition import RandomizedPCA
import numpy as np
from sklearn.externals import joblib
from optparse import OptionParser
from bqapi.comm import BQSession
from bqapi.bqfeature import Feature, ParallelFeature, FeatureResource, FeatureError

#constants
PARALLEL                        = True
IMAGE_BLOCK_SIZE                = 64 #block size of the image to have features extracted from
IMAGE_SERVICE                   = 'image_service'
FEATURES_SERVICE                = 'features'
DATA_SERVICE                    = 'data_service'
FEATURE_NAME                    = 'HTD'
FEATURE_TABLE_DIR               = 'Outputs'
MODEL_DIR                       = 'Model'


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('bq.modules')

def _mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
        """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                          "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            try:
                os.mkdir(newdir)
            except OSError, e:
                log.warn ('mkdir: %s', str(e))
                

def image_tiles(bqsession, image_service_url, tile_size=64):
    """
        Breaks an image service request into non overlapping tiles
        
        @param: bqsession - initalized BQSession
        @param: image_service_url - url to the image serivce resource
        @param: tile_size - the size of the tiles in pixels the image 
        will be broken into (default: 64)
        
        @yield: urls for images service that tile the entire image
    """
    meta = bqsession.fetchxml(image_service_url, meta='')
    x = int(meta.xpath('tag[@name="image_num_x"]')[0].attrib[ 'value'])
    y = int(meta.xpath('tag[@name="image_num_y"]')[0].attrib[ 'value'])
    
    for ix in range(int( x/tile_size)-1):
        for iy in range(int( y/tile_size)-1):
            yield bqsession.c.prepare_url(image_service_url, tile='0,%s,%s,%s' % (str(ix), str(iy), str(tile_size)))


def extract_bush_feature(bqsession, query):
    """
        Makes a feature request for the bush feature which is 
        tiled blocks of the image with Homogenious Texture 
        Descriptor (HTD) extracted from them.
        
        @param: bqsession - initalized BQSession
        @param: query - dataset value list or data_service query
        
        @return: hdf5 filename containing all the features
        from the images in the query
    """
    resource_xml = bqsession.fetchxml(query)
    resource_list = []
    for image in resource_xml.xpath('image'):
        image_url = bqsession.c.prepare_url('/%s/image/%s'%(IMAGE_SERVICE, image.attrib['resource_uniq']))
        for url in image_tiles(bqsession, image_url, tile_size=IMAGE_BLOCK_SIZE):
            resource_list.append(FeatureResource(image=url))
        
    if PARALLEL:
        feature = ParallelFeature()
    else:
        feature = Feature()
        
    return feature.fetch(bqsession, FEATURE_NAME, resource_list)


class BotanicamTrainerError(Exception):
    
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message
  

class BotanicamTrainer(object):
    """
        Botanicam Trainer Module
    """

    def mex_parameter_parser(self, mex_xml):
        """
            Parses input of the xml and add it to BotanicamTrainer's options attribute
            
            @param: mex_xml
        """
        mex_inputs = mex_xml.xpath('tag[@name="inputs"]')
        if mex_inputs:
            for tag in mex_inputs[0]:
                if tag.tag == 'tag' and tag.attrib['type'] != 'system-input': #skip system input values
                    log.debug('Set options with %s as %s'%(tag.attrib['name'],tag.attrib['value']))
                    setattr(self.options,tag.attrib['name'],tag.attrib['value'])
        else:
            log.debug('BotanicamFS: No Inputs Found on MEX!')
    

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
        
        log.debug('BotanicamTrainer: Insufficient options or arguments to start this module')
        return False
    
    
    def setup(self):
        """
            Fetches the mex and appends input_configurations to the option
            attribute of BotanicamTrainer
        """
        #initalizes if user and password are provided
        if (self.options.user and self.options.pwd and self.options.root):
            self.bqSession = BQSession().init_local( self.options.user, self.options.pwd, bisque_root=self.options.root)
            self.options.mexURL = self.bqSession.mex.uri

        #initalizes if mex and mex token is provided
        elif (self.options.mexURL and self.options.token):
            self.bqSession = BQSession().init_mex(self.options.mexURL, self.options.token)
        
        else:
            raise BotanicamTrainerError('BotanicamTrainer: Insufficient options or arguments to start this module')
        
        self.bqSession.update_mex('Initializing...')
        self.mex_parameter_parser(self.bqSession.mex.xmltree)
        return
    
    
    def run(self):
        """
            The core of the Botanicam Trainer
            
            Parses the tags and find all the corresponding values to from classes.
            Classes that have no images in them are removed. Features are requested
            on all the images and then trained using the tag value classes. The 
            resulting model file is stored on bisque as a zip file.
        """
        

        #retieve tags
        self.bqSession.update_mex('Parse Tags...')
        
        if not self.options.tag_names:
            raise BotanicamTrainerError('Tags are a required input!')
        
        self.tag_names = self.options.tag_names.split(',')


        #type check
        resource_short = self.bqSession.fetchxml(self.options.resource_url,view='short')
        if resource_short.tag=='dataset':
            resource_url_values = '%s/value'%self.options.resource_url
        else:
            resource_url_values = self.options.resource_url
        
        
        
        all_images = self.bqSession.fetchxml(resource_url_values, view='full,clean')
        
        tag_query_list = []
        for name in self.tag_names:
            name_list = []
            for u in np.unique(all_images.xpath('image/tag[@name="%s"]/@value'%name)):
                name_list.append('"%s":"%s"' % (name,u))
            tag_query_list.append(name_list)

        #need to find the unique values to create lists of images
        #hopefully the tag names and lists are not too complicated
        tag_query_list = [list(element) for element in itertools.product(*tag_query_list)] #cartesian product
        
        self.complete_tag_list = []
        tag_query_url_list = []
        #search for classes with images
        #query all the values to see if images return 
        
        #removing query_tag from the resource_url and adding it back in later
        resource_url_wo_query = resource_url_values
        resource_query = None
        from urlparse import urlsplit, urlunsplit, parse_qs
        from urllib import urlencode
        o = urlsplit(resource_url_values)
        q = parse_qs(o.query)
        if q.get('tag_query'):
            resource_query = q['tag_query']
            del q['tag_query']
            query = urlencode(q)
            resource_url_wo_query = urlunsplit((o.scheme,o.netloc,o.path,query,o.fragment))
            
        log.debug(tag_query_list)
        for tag_query in tag_query_list:
            encoded_tag_query = tag_query
            if resource_query: encoded_tag_query+=resource_query #adding back in the query_tag from the resource_url
            encoded_tag_query = map(urllib.quote, tag_query)
            encoded_tag_query='%s' % ' AND '.join(encoded_tag_query)
            query_xml = self.bqSession.fetchxml(resource_url_wo_query, tag_query=encoded_tag_query, view='full,clean')
            if len(query_xml.xpath('image'))>0:
                name_value_pairs = {}
                for t in tag_query: #create dictionary of clases with list of name value pairs
                    m = re.match('"(?P<name>[^"]+)":"(?P<value>[^"]+)"',t)
                    name_value_pairs[m.group('name')] = m.group('value')
                self.complete_tag_list.append(name_value_pairs)
                tag_query_url_list.append(query_xml.attrib['uri'])

        feature_length = Feature().length(self.bqSession, FEATURE_NAME)

        if len(tag_query_url_list)<2:
            raise BotanicamTrainerError('Requires atleast 2 classes to train found %s' % len(tag_query_url_list))

         #extracts all the features and then appends it to a larger table
        _mkdir(os.path.join(self.options.stagingPath, FEATURE_TABLE_DIR))
        main_table = os.path.join(self.options.stagingPath, FEATURE_TABLE_DIR, 'feature_table.h5')

        with tables.open_file(main_table, 'w') as h5file:
            columns = {'label'   : tables.Int64Col(),
                       'feature' : tables.Float32Col(shape=(feature_length))}
            table = h5file.create_table('/','values', columns)
            table.flush()
            
        self.bqSession.update_mex('Calculated features on (0/%s) spieces...' % (len(tag_query_url_list)))
        
        for i, tag_url_query in enumerate(tag_query_url_list):
            try:
                vectors = extract_bush_feature(self.bqSession, tag_url_query) #may need to be moved into local temp
                feature_table = vectors.root.values
                with tables.open_file(main_table, 'a') as h5file:
                    table = h5file.root.values
                    r = table.row
                    for fr in feature_table:
                        r['feature'] = fr['feature']
                        r['label']   = i
                        r.append()
                    table.flush()
                vectors.close()
                os.remove(vectors.filename)
            except FeatureError as e:
                raise BotanicamTrainerError(str(e))
            
            self.bqSession.update_mex('Calculated features on (%s/%s) spieces...' % (i+1,len(tag_query_url_list)))
       
        self.bqSession.update_mex('Classifying')
        log.debug('Training model')
        #classify the features
        pca = RandomizedPCA(whiten=True)
        clf = svm.SVC()
        
        with tables.open_file(main_table,'r') as h5file:
            table = h5file.root.values
            pca.fit(table[:]['feature'])
            clf.fit(pca.transform(table[:]['feature']), table[:]['label'])
        
        self.bqSession.update_mex('Posting model to bisque...')
        
        log.debug('Storing and Zipping model')
        self.model_dir = os.path.join(self.options.stagingPath, MODEL_DIR)
        self.svm_model_file = os.path.join(self.options.stagingPath, MODEL_DIR, 'svm_model')
        self.pca_model_file = os.path.join(self.options.stagingPath, MODEL_DIR, 'pca_model')
        
        _mkdir(self.model_dir)
        svm_files = joblib.dump(clf, self.svm_model_file)
        pca_files = joblib.dump(pca, self.pca_model_file)
        
        #zip file
        import zipfile
        with zipfile.ZipFile('%s.zip'%self.model_dir, 'w') as fzip:
            for f in svm_files:
                fzip.write(f, os.path.basename(f))
            for f in pca_files:
                fzip.write(f, os.path.basename(f))
    
    
    def teardown(self):
        """
            Post the results to the mex xml.
        """
        #save the model and upload it to the data service with all the meta data
        self.bqSession.update_mex( 'Returning results...')
        #self.bqSession.update_mex('Returning home after a long day...')
        
        #constructing and storing model file
        
        #does not accept no name on the resource
        cl_model = etree.Element('resource', name=os.path.basename('%s.zip' % MODEL_DIR))
        
        #classes
        tag_classes = etree.SubElement(cl_model, 'tag', name='Classes')
        for i, name_value_pairs in enumerate(self.complete_tag_list) :
            tag_labels = etree.SubElement(tag_classes, 'tag', name='Class_%s'%str(i), value=str(i))
            for n in name_value_pairs.keys():
                etree.SubElement(tag_labels, 'tag', name=n, value=name_value_pairs[n])
                
        etree.SubElement(cl_model, 'tag', name='Number of Classes', value=str(len(self.complete_tag_list)))
        
        #module identifier (a descriptor to be found by the botanicam model)
        etree.SubElement(cl_model, 'tag', name='module_identifier', value='Botanicam')        
        
        #model filename
        etree.SubElement(cl_model, 'tag', name='filename', value=os.path.basename('%s.zip' % MODEL_DIR))
        
        #classification method
        etree.SubElement(cl_model, 'tag', name='Classification Method', value='Bush Descriptor')
        
        #Resource url
        etree.SubElement(cl_model, 'tag', name='Resource', value=self.options.resource_url)
        
        #description
        etree.SubElement(cl_model, 'tag', name='description', value = 'Model File for the Botanicam Module')
        
        #storing the model file in blobservice
        r = self.bqSession.postblob('%s.zip'%self.model_dir, xml = cl_model)
        r_xml = etree.fromstring(r)
        outputTag = etree.Element('tag', name ='outputs')
        etree.SubElement(outputTag, 'tag', name='classification_file', value=r_xml[0].attrib['uri'], type='model_viewer')

        self.bqSession.finish_mex(tags=[outputTag])
        self.bqSession.close()
    
    
    def main(self):
        """
            The main function that runs everything
        """
        log.debug('sysargv : %s' % sys.argv )
        parser = OptionParser()

        parser.add_option('--resource_url'    , dest="resource_url") #for now only datasets
        parser.add_option('--Tags'            , dest="tag_names") #labels on the images
        parser.add_option('--ClassifierMethod', dest="classifier_methods")
        parser.add_option('--FeatureName'     , dest="feature_name")
        parser.add_option('--mex_url'         , dest="mexURL")
        parser.add_option('--module_dir'      , dest="modulePath")
        parser.add_option('--staging_path'    , dest="stagingPath")
        parser.add_option('--bisque_token'    , dest="token")
        parser.add_option('--user'            , dest="user")
        parser.add_option('--pwd'             , dest="pwd")
        parser.add_option('--root'            , dest="root")

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

        log.debug('\n\nPARAMS : %s \n\n Options: %s' % (args, options))
        self.options = options
        
        if self.validate_input():
            
            try:
                self.setup()
            except Exception as e:
                log.exception("Exception during setup")
                self.bqSession.fail_mex(msg = "Exception during setup: %s" %  str(e))
                return
            
            try:
                self.run()
            except (Exception, BotanicamTrainerError) as e:
                log.exception("Exception during run")
                self.bqSession.fail_mex(msg = "Exception during run: %s" % str(e))
                return

            try:
                self.teardown()
            except (Exception, BotanicamTrainerError) as e:
                log.exception("Exception during teardown %s")
                self.bqSession.fail_mex(msg = "Exception during teardown: %s" %  str(e))
                return
                   
    
if __name__=="__main__":
    BotanicamTrainer().main()
