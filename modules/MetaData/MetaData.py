try:
    from lxml import etree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from bqapi import BQSession, BQTag
from bqapi.blockable_module import BlockableModule

import logging



logging.basicConfig(filename='MetaData.log',level=logging.DEBUG)

wanted_tags = [
    'data_time',
    'pixel_resolution_x',
    'pixel_resolution_unit_x',
    'pixel_resolution_y',
    'pixel_resolution_unit_y',
    'pixel_resolution_z',
    'pixel_resolution_unit_z',
    'pixel_resolution_t',
    'pixel_resolution_unit_t',
    'image_num_x',
    'image_num_y',
    'image_num_z',
    'image_num_t',
    'image_num_c',
    'image_num_p',
    'image_pixel_depth',
    ]


class MetaData(BlockableModule):
    """Example Python module
    Read tags from image server and store tags on image directly
    """
    
    def process_single(self, bq, image_url, **kw):
        logging.debug("processing single %s", str(kw))
        
        # Fetch the image metadata
        image = bq.load(image_url)

        # Fetch embedded tags from image service
        meta = image.pixels().meta().fetch()
        meta = ET.XML(meta)
        tags = []
        # Create a new tag 'MetaData' to be placed on the image
        md = BQTag(name='MetaData')
        # Filter the embedded metadata and place subtags in MetaData
        for t in meta.getiterator('tag'):
            if t.get('name') in wanted_tags:
                md.addTag (name=t.get('name'),
                           value=t.get('value'))
        # Add the new tag to the image
        image.addTag(tag = md)
        metadata_tag = bq.save(md, image.uri + "/tag")
        if metadata_tag is None:
            bq.fail_mex ("could not write tag: no write access")
            return
        
        # mark single mex as finished
        bq.finish_mex(tags = [{ 'name': 'outputs',
                                'tag' : [{ 'name': 'metadata',
                                           'value': metadata_tag.uri,
                                           'type' : 'tag' }]}])

    def start_block(self, bq, all_kw):
        logging.debug("starting block %s", str(all_kw))
        
    def end_block(self, bq):
        logging.debug("ending block")
        # mark block as finished
        bq.finish_mex()



if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-c", "--credentials", dest="credentials",
                      help="credentials are in the form user:password")
    #parser.add_option('--image_url')
    #parser.add_option('--mex_url')
    #parser.add_option('--auth_token')

    (options, args) = parser.parse_args()

    M = MetaData()
    if options.credentials is None:
        image_url, mex_url,  auth_token  = args[:3]
        M.main(mex_url, auth_token)
    else:
        image_url = args.pop(0)

        if not options.credentials:
            parser.error('need credentials')
        user,pwd = options.credentials.split(':')

        bq = BQSession().init_local(user, pwd)
        M.main(image_url, bq=bq)

