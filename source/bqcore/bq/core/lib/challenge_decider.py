import itertools
import logging

import zope
from paste.httpheaders import (
    CONTENT_TYPE,  # pylint: disable=no-name-in-module
    REQUEST_METHOD,  # pylint: disable=no-name-in-module
    USER_AGENT,  # pylint: disable=no-name-in-module
    WWW_AUTHENTICATE,  # pylint: disable=no-name-in-module
)
from repoze.who.classifiers import default_request_classifier

# from zope.interface import implements # !!! not in use
from repoze.who.interfaces import (
    IAuthenticator,
    IChallengeDecider,
    IChallenger,
    IIdentifier,
    IRequestClassifier,
)
from webob import Request, Response

log = logging.getLogger("bq.auth.challenge")

NO_CHALLENGE = ["application/xml", "text/xmlapplication/json"]


def bisque_challenge_decider(environ, status, headers):

    # log.info ('challange_decider')
    # we do the default if it's a 401, probably we show a form then
    if status.startswith("401 "):
        request = Request(environ)
        response = Response(environ)

        # log.debug ('401 INFO header=%s environ=%s' % (headers, environ))

        req_content = request.headers["content-type"]
        accept = request.headers.get("accept")
        content_type = response.headers.get("content-type")

        # By default several browser send accept : application/xml
        # http://www.grauw.nl/blog/entry/470
        if accept and "text/xml" in accept:  # or 'application/xml' in accept:
            return False

        if content_type in NO_CHALLENGE:
            log.info("CHALLENGE FALSE")
            return False
        # if content_type and 'text/xml' in content_type \
        #    or 'application/xml' in content_type \
        #    or 'text/xml' in req_content \
        #    or 'application/xml' in req_content:
        #    return False
        log.debug("challange requested")
        log.debug("req %s resp %s" % (req_content, content_type))
        return True
    elif "repoze.whoplugins.openid.openid" in environ:
        # in case IIdentification found an openid it should be in the environ
        # and we do the challenge
        return True
    elif "repoze.who.plugins.cas" in environ:
        # in case IIdentification found an cas it should be in the environ
        # and we do the challenge
        return True
    return False


zope.interface.directlyProvides(bisque_challenge_decider, IChallengeDecider)


def bisque_request_classifier(environ):
    request_method = REQUEST_METHOD(environ)
    content_type = CONTENT_TYPE(environ)
    if request_method == "POST" and content_type.startswith("application/json"):
        return "json"
    if content_type.startswith("application/xml"):
        return "xml"
    return default_request_classifier(environ)


zope.interface.directlyProvides(bisque_request_classifier, IRequestClassifier)
