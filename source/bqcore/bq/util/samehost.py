
###############################################################################
##  Bisquik                                                                  ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007 by the Regents of the University of California     ##
##                            All rights reserved                            ##
##                                                                           ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions are    ##
## met:                                                                      ##
##                                                                           ##
##     1. Redistributions of source code must retain the above copyright     ##
##        notice, this list of conditions, and the following disclaimer.     ##
##                                                                           ##
##     2. Redistributions in binary form must reproduce the above copyright  ##
##        notice, this list of conditions, and the following disclaimer in   ##
##        the documentation and/or other materials provided with the         ##
##        distribution.                                                      ##
##                                                                           ##
##     3. All advertising materials mentioning features or use of this       ##
##        software must display the following acknowledgement: This product  ##
##        includes software developed by the Center for Bio-Image Informatics##
##        University of California at Santa Barbara, and its contributors.   ##
##                                                                           ##
##     4. Neither the name of the University nor the names of its            ##
##        contributors may be used to endorse or promote products derived    ##
##        from this software without specific prior written permission.      ##
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS "AS IS" AND ANY ##
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED ##
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, ARE   ##
## DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR  ##
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL    ##
## DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS   ##
## OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)     ##
## HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,       ##
## STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN  ##
## ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE           ##
## POSSIBILITY OF SUCH DAMAGE.                                               ##
##                                                                           ##
###############################################################################
"""
SYNOPSIS
========


DESCRIPTION
===========

"""

import socket

from tg import config


def fqdn(h=None):
    ''' return the fqdn and port'''

    if not h:
        h = socket.gethostname()
        port = config.get('server.socket_port')
    else:
        h, port = h.split(':')

    nm, aliases, ipaddr = socket.gethostbyaddr(h)
    if nm.find('.')>0: return nm, int(port)
    for a in aliases:
        if a.find('.')>0: return a, int(port)

def same_host(h1, h2=None):
    '''
    Return true when host name represents same host
    '''
    fqdn1, port1 = fqdn(h1)
    fqdn2, port2 = fqdn(h2)
    same = ( (fqdn1 == fqdn2) and (port1 == port2) )
    #log.debug ("same: " +str(same)+' ' + fqdn1+':'+str(port1) +'||'+ fqdn2 +':'+str(port2))
    return same


# UNUSED
# def whataremyips():
#     """
#     Get the machine's ip addresses
#     :returns: list of Strings of ip addresses
#     """
#     import netifaces
#     addresses = []
#     for interface in netifaces.interfaces():
#         iface_data = netifaces.ifaddresses(interface)
#         for family in iface_data:
#             if family not in (netifaces.AF_INET, netifaces.AF_INET6):
#                 continue
#             for address in iface_data[family]:
#                 addresses.append(address['addr'])
#     return addresses
