###############################################################################
##  Bisquik                                                                  ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007,2008,2009,2010                                     ##
##     by the Regents of the University of California                        ##
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

Services for the notifying users.
"""

import logging
import smtplib
import socket
import turbomail


from lxml import etree
from tg import request,  expose, require , config
from repoze.what import predicates


from bq.core.service import ServiceController
from bq.core import identity

log = logging.getLogger('bq.notify')
#admin_email = tg.config.get('bisque.admin_email')


def send_mail(sender_email, recipients_email, subject, body ):
    """Send an email with  info to the user.
    """

    #if not sender_email or not  admin_email:
    #    log.exception('Configuration error: could not send error'
    #      'because sender and/or admin email address is not set.')
    #    raise RuntimeError

    if not isinstance(recipients_email, list):
        recipients_email = [  recipients_email ]

    msg = turbomail.Message(sender_email, ",".join (recipients_email), subject)
    msg.plain = body
    try:
        log.debug ("Sending mail to %s %s" ,  recipients_email, subject)
        turbomail.send(msg)
        return True
    except turbomail.MailNotEnabledException:
        log.warning("Failed sending %s with '%s' turbomail not enabled" , recipients_email,  subject)
    except (smtplib.SMTPException, socket.error) as exc :
        log.warning("Failed sending %s with '%s'" ,  recipients_email, subject, exc_info=True)

    return False

def send_invite(sender_email, recipient_email, subject, body):
    """Create a new user and send them an invitation
    returns the new BQuser
    """
    log.debug ("Creating new user %s" , recipient_email)
    return send_mail(sender_email, recipient_email, subject, body)

    #return newuser


class NotifyServerController(ServiceController):
    service_type = "notify"

    @expose(content_type='text/xml')
    def index(self, **kw):
        descr = etree.Element ('resource', uri = self.uri)
        entry = etree.SubElement (descr, 'method', name='/notify/email', value="Send an email from user")
        etree.SubElement (entry, 'arguments', value = 'recipient,subject')
        etree.SubElement (entry, 'verb', value = 'POST')
        etree.SubElement (entry, 'body', value = 'required')
        return etree.tostring (descr)


    @expose(content_type='text/xml')
    @require(predicates.not_anonymous())
    def email(self, recipients=None, subject=None, body=None): #pylint: disable=no-self-use
        """Send an email for logged in users



        POST application/text   ?subject=required&recipient=required[,required][&body]
             TEXT BODY
        POST applcation/xml   ?subject=required&recipient=required[,required][&body]
        <message>
           <subject>.. </subject>
           <recipient> .. </recipient>
           <body> .. </body>
        </message>
        """
        #sender = identity.get_current_user().resource_value
        sender = config.get ('bisque.admin_email')
        if request.content_type == 'application/xml':
            message = etree.XML (request.body)
            node = message.find ('subject')
            if subject is None and node is not None:
                subject = node.text
            node = message.find ('recipient')
            if recipients is None and node is not None:
                recipients = node.text
            node = message.find ('body')
            if body is None and node is not None:
                body = node.text
        else:  #   if request.content_type == 'application/text':
            if body is None:
                body = request.body

        if not subject:
            return "<failure msg='no subject' />"
        if not body:
            return "<failure msg='no body' />"
        if not recipients:
            return "<failure msg='no recipients' />"

        if send_mail(sender, recipients, subject, body):
            return "<success/>"
        else:
            return "<failure msg='send failed' />"


def initialize(uri):
    """ Initialize the top level server for this microapp"""
    # Add you checks and database initialize
    log.debug ("initialize " + uri)
    service =  NotifyServerController(uri)

    return service

__controller__= NotifyServerController
