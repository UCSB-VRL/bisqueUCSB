import logging
import requests

from bs4 import BeautifulSoup as soupy

def login_elements(tag):
    """A filter to find cas login form elements"""
    return tag.has_key('name') and tag.has_key('value')

def caslogin(session, caslogin, username, password, service=None):
    if service:
        params = {'service' : service}
    else:
        params = None

    cas_page = session.get(caslogin, params = params)
    # Move past any redirects
    caslogin = cas_page.url
    cas_doc = soupy(cas_page.text)
    form_inputs = cas_doc.find_all(login_elements)
    login_data = dict()
    for tag in form_inputs:
        login_data[tag['name']] = tag['value']
    login_data['username'] = username
    login_data['password'] = password

    signin_page = session.post(caslogin, login_data, cookies=cas_page.cookies, params = params)
    if signin_page.status_code != requests.codes.ok: #pylint: disable=no-member
        logging.warn ("ERROR on CAS signin headers %s cookies %s text %s",
                      signin_page.headers, signin_page.cookies, signin_page.text)
    return  signin_page.status_code == requests.codes.ok #pylint: disable=no-member
