from lxml import etree as ET
from bqapi import BQSession, BQTag


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

class MyData(object):
    """Example Python module
    Read tags from image server and store tags on image directly
    """
    def main(self, image_url,  mex_url = None, bisque_token=None, bq = None):
        #  Allow for testing by passing an alreay initialized session
        if bq is None:
            bq = BQSession().init_mex(mex_url, bisque_token)
        # Fetch the image metadata
        image = bq.load(image_url)

        # Fetch embedded tags from image service
        meta = image.pixels().meta().fetch()
        meta = ET.XML(meta)
        tags = []
        # Create a new tag 'MyData' to be placed on the image
        md = BQTag(name='MyData')
        # Filter the embedded metadata and place subtags in MyData
        for t in meta.getiterator('tag'):
            if t.get('name') in wanted_tags:
                md.addTag (name=t.get('name'),
                           value=t.get('value'))
        # Add the new tag to the image
        image.addTag(tag = md)
        bq.save(md, image.uri + "/tags")
        bq.close()


if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-c", "--credentials", dest="credentials",
                      help="credentials are in the form user:password")

    (options, args) = parser.parse_args()

    image_url = args.pop(0)

    if not options.credentials:
        parser.error('need credentials')
    user,pwd = options.credentials.split(':')

    bq = BQSession().init_local(user, pwd)
    M = MyData()
    M.main(image_url, bq=bq)



