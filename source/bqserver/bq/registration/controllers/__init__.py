#Empty

import pylons
from pylons.i18n.translation import _get_translator

pylons.translator._push_object(_get_translator(pylons.config.get('lang')))
