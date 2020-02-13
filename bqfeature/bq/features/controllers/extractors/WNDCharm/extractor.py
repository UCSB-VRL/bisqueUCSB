# -*- mode: python -*-
""" Initalizes the WNDCharm library from the PyWNDCharmFeatureList
"""

import logging
log = logging.getLogger("bq.features")

from PyWNDCharmFeatureList import feature_list
import sys
import WNDCharmBase

for features_name in feature_list.keys():
    #initalizes a class for each feature in wndcharm
    WNDCharmFeature = type(features_name,
             (WNDCharmBase.WNDCharm,), 
             dict(
                  feature_list = feature_list,
                  file = 'features_'+features_name+'.h5',
                  name = features_name,
                  description = """This is the WNDCharm Library. Input a feature from the WND-Charm library""",
                  length = feature_list[features_name][3], #feature length
                  confidence = feature_list[features_name][6]
                  )
             )
    setattr(sys.modules[__name__], features_name,WNDCharmFeature)
    