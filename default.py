# -*- coding: utf-8 -*-
from os.path import join
from sys import path
import platform
from resources.lib import common
from resources.lib import logger

_addonPath_ = common.addonPath
path.append(join(_addonPath_, "resources", "lib"))
path.append(join(_addonPath_, "resources", "lib", "gui"))
path.append(join(_addonPath_, "resources", "lib", "handler"))
path.append(join(_addonPath_, "resources", "art", "sites"))
path.append(join(_addonPath_, "sites"))

from xstream import run
logger.info('*---- Running xStream, version %s ----*' % common.addon.getAddonInfo('version'))
logger.info('Python-Version: %s' % platform.python_version())

try:
    run()
except Exception as err:
    if str(err) == 'UserAborted':
        logger.error("User aborted list creation")
    else:
        import traceback
        import xbmcgui
        logger.debug(traceback.format_exc())
        dialog = xbmcgui.Dialog().ok('Error', str(err.__class__.__name__) + " : " + str(err), str(traceback.format_exc().splitlines()[-3].split('addons')[-1]))
