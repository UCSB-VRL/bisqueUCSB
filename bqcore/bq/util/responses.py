"""
typical response codes
"""

__author__    = "Dmitry Fedorov"
__version__   = "1.0"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

# 200s
OK                      = 200
CREATED                 = 201 # The request has been fulfilled, resulting in the creation of a new resource
ACCEPTED                = 202 # The request has been accepted for processing, but the processing has not been completed.
                              # The request might or might not be eventually acted upon, and may be disallowed when processing occurs.
NO_CONTENT              = 204 # The server successfully processed the request and is not returning any content
RESET_CONTENT           = 205 # The server successfully processed the request, but is not returning any content.
                              # Unlike a 204 response, this response requires that the requester reset the document view

# 300s
SEE_OTHER               = 303 # The response to the request can be found under another URI using a GET method.
                              # When received in response to a POST (or PUT/DELETE), the client should presume that the
                              # server has received the data and should issue a redirect with a separate GET message
NOT_MODIFIED            = 304 # Indicates that the resource has not been modified since the version specified by the
                              # request headers If-Modified-Since or If-None-Match. In such case, there is no need to
                              # retransmit the resource since the client still has a previously-downloaded copy.
TEMPORARY_REDIRECT      = 307 # In this case, the request should be repeated with another URI; however, future requests
                              # should still use the original URI. In contrast to how 302 was historically implemented,
                              # the request method is not allowed to be changed when reissuing the original request.
                              # For example, a POST request should be repeated using another POST request.
PERMANENT_REDIRECT      = 308 # The request and all future requests should be repeated using another URI.
                              # 307 and 308 parallel the behaviors of 302 and 301, but do not allow the HTTP method to change.
                              # So, for example, submitting a form to a permanently redirected resource may continue smoothly.

# 400s
BAD_REQUEST             = 400 # The server cannot or will not process the request due to an apparent client error
                              # (e.g., malformed request syntax, too large size, invalid request message framing, or deceptive request routing).
UNAUTHORIZED            = 401 # Similar to 403 Forbidden, but specifically for use when authentication is required and has
                              # failed or has not yet been provided. The response must include a WWW-Authenticate header
                              # field containing a challenge applicable to the requested resource.
FORBIDDEN               = 403 # The request was valid, but the server is refusing action. The user might not have the necessary
                              # permissions for a resource
NOT_FOUND               = 404 # The requested resource could not be found but may be available in the future.
                              # Subsequent requests by the client are permissible
METHOD_NOT_ALLOWED      = 405 # A request method is not supported for the requested resource; for example, a GET request
                              # on a form that requires data to be presented via POST, or a PUT request on a read-only resource
CONFLICT                = 409 # Indicates that the request could not be processed because of conflict in the request,
                              # such as an edit conflict between multiple simultaneous updates
UNSUPPORTED_MEDIA_TYPE  = 415 # The request entity has a media type which the server or resource does not support.
UNPROCESSABLE_ENTITY    = 422 # The request was well-formed but was unable to be followed due to semantic errors
LOCKED                  = 423 # The resource that is being accessed is locked

# 500s
INTERNAL_SERVER_ERROR   = 500 # A generic error message, given when an unexpected condition was encountered and no
                              # more specific message is suitable
NOT_IMPLEMENTED         = 501 # The server either does not recognize the request method, or it lacks the ability
                              # to fulfill the request. Usually this implies future availability
GATEWAY_TIMEOUT         = 504 # The server was acting as a gateway or proxy and did not receive a timely response from the upstream server.
INSUFFICIENT_STORAGE    = 507 # The server is unable to store the representation needed to complete the request