class BQException(Exception):
    """
        BQException
    """

class BQApiError(BQException):
    """Exception in API usage"""



class BQCommError(BQException):

    def __init__(self, response):
        """
            @param: status - error code
            @param: headers - dictionary of response headers
            @param: content - body of the response (default: None)

        """
        #print 'Status: %s'%status
        #print 'Headers: %s'%headers
        self.response = response


    def __str__(self):
        content = "%s...%s" % (self.response.content[:64], self.response.content[-64:]) if len (self.response.content) > 64 else self.response.content
        return "BQCommError(%s, status=%s, req headers=%s)%s" % (self.response.url,
                                                                 self.response.status_code,
                                                                 self.response.request.headers,
                                                                 content )
