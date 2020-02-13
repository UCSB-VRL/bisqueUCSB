

from bq import data_service

def registration_cb (action, user=None):
    data_service.cache_invalidate('/data_service/user')






