# -*- coding: utf-8 -*-

"""WebHelpers used in bqcore."""

from webhelpers import date, feedgenerator, html, number, misc, text
from paste.deploy.converters import asbool
from bq.util.paths import bisque_path
#from minimatic  import *
from .js_includes import generate_css_files, generate_js_files

import bq

def file_root():
    return bisque_path('')
def file_public():
    return bisque_path('public')

def add_global_tmpl_vars ():
    #log.debug ("add_global_tmpl_vars")
    #return dict (widgets = widgets)
    return dict(
        bq = bq,
        asbool = asbool
#         c = dict (
#         commandbar_enabled = True,
#         datasets_enabled =False,
#         organizer_enabled = False,
#         search_enabled = False,
#         analysis_enabled = False,
#         visualization_enabled = False,
#         upload_enabled = False    ,
#             )
        )
