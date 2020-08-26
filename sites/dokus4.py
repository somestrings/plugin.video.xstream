# -*- coding: utf-8 -*-
from resources.lib import logger
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser

SITE_IDENTIFIER = 'dokus4'
SITE_NAME = 'Dokus4'
SITE_ICON = 'dokus4.png'
SITE_GLOBAL_SEARCH = False
URL_MAIN = 'http://www.dokus4.me/'
URL_SEARCH = URL_MAIN + '?s=%s'

def load():
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_MAIN)
    cGui().addFolder(cGuiElement('Dokus', SITE_IDENTIFIER, 'showEntries'), params)
    cGui().addFolder(cGuiElement('Kategorien', SITE_IDENTIFIER, 'showGenre'), params)
    cGui().addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    cGui().setEndOfDirectory()

def showGenre():
    params = ParameterHandler()
    entryUrl = params.getValue('sUrl')
    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = 'cat-item.*?href="([^"]+)">([^<]+)</a>'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        cGui().showInfo()
        return

    for sUrl, sName in aResult:
        params.setParam('sUrl', sUrl)
        cGui().addFolder(cGuiElement(sName, SITE_IDENTIFIER, 'showEntries'), params)
    cGui().setEndOfDirectory()

def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl: entryUrl = params.getValue('sUrl')
    sHtmlContent = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False)).request()
    pattern = 'tbl_titel.*?title="([^"]+).*?href="([^"]+)/"><img src="([^"]+).*?vid_desc">([^<]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sName, sUrl, sThumbnail, sDesc in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'getHosterUrl')
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setFanart(sThumbnail)
        oGuiElement.setDescription(sDesc)
        params.setParam('url', sUrl)
        oGui.addFolder(oGuiElement, params, False, total)
    if not sGui:
        pattern = 'rel="next" href="([^"]+)'
        isMatchNextPage, sNextUrl = cParser.parseSingleResult(sHtmlContent, pattern)
        if isMatchNextPage:
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setEndOfDirectory()

def getHosterUrl(sUrl=False):
    sHtmlContent = cRequestHandler(sUrl).request()
    isMatch, sUrl = cParser.parseSingleResult(sHtmlContent, '<p><iframe.*?src="([^"]+)"')
    if isMatch:
        import xbmc, xbmcgui
        if not xbmc.getCondVisibility("System.HasAddon(%s)" % "plugin.video.youtube"):
            xbmc.executebuiltin("InstallAddon(%s)" % "plugin.video.youtube")
        return [{'streamUrl': sUrl, 'resolved': False}]

def showSearch():
    sSearchText = cGui().showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    cGui().setEndOfDirectory()

def _search(oGui, sSearchText):
    showEntries(URL_SEARCH % cParser().quotePlus(sSearchText), oGui, sSearchText)
