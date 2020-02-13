
def bq_challenge_decider(environ, status, headers):
    """ Return true if challenge is needed """
    return status.startswith('401 ')

    if not status.startswith('401 '):
        return False
    h_dict = dict(headers)
    if 'WWW-Authenticate' in h_dict:
        return False
    ct = h_dict.get('Content-Type', None)
    print "CHALLENGE HEADERS", ct
    return  'xml' not in ct



