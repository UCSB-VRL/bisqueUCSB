import itertools
import logging
import zope

from webob import Request, Response

from paste.httpheaders import REQUEST_METHOD #pylint: disable=no-name-in-module
from paste.httpheaders import CONTENT_TYPE   #pylint: disable=no-name-in-module
from paste.httpheaders import USER_AGENT     #pylint: disable=no-name-in-module
from paste.httpheaders import WWW_AUTHENTICATE #pylint: disable=no-name-in-module

from zope.interface import implements
from repoze.who.interfaces import IChallenger, IIdentifier, IAuthenticator
from repoze.who.interfaces import IRequestClassifier, IChallengeDecider
from repoze.who.classifiers import default_request_classifier

log = logging.getLogger('bq.auth.challenge')

NO_CHALLENGE = [
    "application/xml", "text/xml"
    "application/json"
]


def bisque_challenge_decider(environ, status, headers):

    #log.info ('challange_decider')
    # we do the default if it's a 401, probably we show a form then
    if status.startswith('401 '):
        request = Request(environ)
        response = Response(environ)

        #log.debug ('401 INFO header=%s environ=%s' % (headers, environ))

        req_content = request.headers['content-type']
        accept = request.headers.get('accept')
        content_type = response.headers.get('content-type')

        # By default several browser send accept : application/xml
        # http://www.grauw.nl/blog/entry/470
        if accept and 'text/xml' in accept: #or 'application/xml' in accept:
            return False

        if content_type in NO_CHALLENGE:
            log.info ("CHALLENGE FALSE")
            return False
        #if content_type and 'text/xml' in content_type \
        #    or 'application/xml' in content_type \
        #    or 'text/xml' in req_content \
        #    or 'application/xml' in req_content:
        #    return False
        log.debug ('challange requested')
        log.debug ('req %s resp %s' % (req_content, content_type))
        return True
    elif environ.has_key('repoze.whoplugins.openid.openid'):
        # in case IIdentification found an openid it should be in the environ
        # and we do the challenge
        return True
    elif environ.has_key('repoze.who.plugins.cas'):
        # in case IIdentification found an cas it should be in the environ
        # and we do the challenge
        return True
    return False

zope.interface.directlyProvides(bisque_challenge_decider, IChallengeDecider)


def bisque_request_classifier(environ):
    request_method = REQUEST_METHOD(environ)
    content_type = CONTENT_TYPE(environ)
    if request_method == "POST" and content_type.startswith ("application/json"):
        return "json"
    if content_type.startswith ("application/xml"):
        return "xml"
    return  default_request_classifier(environ)

zope.interface.directlyProvides(bisque_request_classifier, IRequestClassifier)
