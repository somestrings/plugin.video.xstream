# -*- coding: UTF-8 -*-

import os
import xbmc
import xbmcaddon
import xbmcgui

AddonID = xbmcaddon.Addon().getAddonInfo('id')
AddonName = xbmcaddon.Addon().getAddonInfo('name')
NIGHTLY_VERSION_CONTROL = os.path.join(xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'), "update_sha")

def infoDialog(message, heading=AddonName, icon='', time=5000, sound=False):
    if icon == '': icon = xbmcaddon.Addon().getAddonInfo('icon')
    elif icon == 'INFO': icon = xbmcgui.NOTIFICATION_INFO
    elif icon == 'WARNING': icon = xbmcgui.NOTIFICATION_WARNING
    elif icon == 'ERROR': icon = xbmcgui.NOTIFICATION_ERROR
    xbmcgui.Dialog().notification(heading, message, icon, time, sound=sound)

#if os.path.isfile(NIGHTLY_VERSION_CONTROL)== False or xbmcaddon.Addon().getSetting('DevUpdateAuto') == 'true':
from resources.lib import updateManager
status = updateManager.devAutoUpdates(True)
if status == True: infoDialog("Auto Update abgeschlossen", sound=False, icon='INFO', time=3000)
if status == False: infoDialog("Auto Update mit Fehler beendet", sound=True, icon='ERROR')
#if status == None: infoDialog("Keine neuen Updates gefunden", sound=False, icon='INFO', time=3000)

# "setting.xml" wenn notwendig Indexseiten aktualisieren
try:
    if xbmcaddon.Addon().getSetting('newSetting') == 'true':
        from resources.lib.handler.pluginHandler import cPluginHandler
        cPluginHandler().getAvailablePlugins()
except:
    pass

##ka - remove parent directory (..) in lists
#if not 'false' in xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Settings.GetSettingValue", "params":{"setting":"filelists.showparentdiritems"}}'):
#    xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.SetSettingValue","id":1,"params":{"setting":"filelists.showparentdiritems","value":false}}')
#    xbmc.executebuiltin("ReloadSkin()")

exit(0)
