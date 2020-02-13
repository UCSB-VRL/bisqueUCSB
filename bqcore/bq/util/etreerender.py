import logging
from lxml import etree

log = logging.getLogger("bq.util.etreerender")

def render_etree(template_name, template_vars, **kwargs):
    #log.debug ('etree rendering %s=%s' %(template_name, str(template_vars)))
    log.debug ('etree rendering %s' %(template_name))
    return etree.tostring (template_vars[template_name])
