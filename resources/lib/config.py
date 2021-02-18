# -*- coding: utf-8 -*-
from resources.lib import common
import xbmcaddon


class cConfig:
    def __init__(self):
        self.__oSettings = xbmcaddon.Addon(common.addonID)
        self.__aLanguage = self.__oSettings.getLocalizedString

    def showSettingsWindow(self):
        self.__oSettings.openSettings()

    def getSetting(self, sName, default=''):
        result = self.__oSettings.getSetting(sName)
        if result:
            return result
        else:
            return default

    def getLocalizedString(self, sCode):
        return self.__aLanguage(sCode)
