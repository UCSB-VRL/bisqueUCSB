
from paste.fileapp import FileApp

import logging
import pprint

log = logging.getLogger('bq.util.fileapp')

class BQFileApp(FileApp):

    def get(self, environ, start_response):
        #log.debug ('environ = %s' % pprint.pformat(environ))
        #frontend = environ.get ('FRONTEND')
        frontend = None

        if frontend == 'nginx':
            self.content = '1'
            self.headers.append(('X-Accel-Redirect', "/files" + str(self.filename)))
        elif frontend == 'apache':
            self.content = '1'
            self.headers.append(('X-Sendfile', str(self.filename)))
        elif frontend == 'lighttpd':
            self.content = '1'
            self.headers.append(('X-LIGHTTPD-send-file', str(self.filename)))

        return FileApp.get(self, environ, start_response)



