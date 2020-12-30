# -*- coding: utf-8 -*-
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.gui import cGui

SITE_IDENTIFIER = 'view4u'
SITE_NAME = 'View4u'
SITE_ICON = 'view4u.png'
URL_MAIN = 'https://view4u.cc/'
URL_FILME = URL_MAIN + 'filme/'
URL_KINO = URL_MAIN + 'kinofilme/'
URL_ANI = URL_MAIN + 'animation/'
URL_FILMNEU = URL_MAIN + 'novum/'
URL_SEARCH = URL_MAIN


def load():
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_KINO)
    cGui().addFolder(cGuiElement('Kinofilme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_FILME)
    cGui().addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_ANI)
    cGui().addFolder(cGuiElement('Animation Filme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_FILMNEU)
    cGui().addFolder(cGuiElement('Film Neuheiten', SITE_IDENTIFIER, 'showEntries'), params)
    cGui().addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'), params)
    cGui().setEndOfDirectory()


def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl: entryUrl = params.getValue('sUrl')
    oRequest = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False))
    if sSearchText:
        oRequest.addParameters('do', 'search')
        oRequest.addParameters('subaction', 'search')
        oRequest.addParameters('story', sSearchText)
        params.setParam('search', sSearchText)
    sHtmlContent = oRequest.request()
    pattern = 'class="th-item.*?href="([^"]+).*?fx-last">([^<]+).*?:?data-src="([^"]+)?'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sUrl, sName, sThumbnail in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setThumbnail(URL_MAIN + sThumbnail)
        oGuiElement.setMediaType('movie')
        params.setParam('entryUrl', sUrl)
        oGui.addFolder(oGuiElement, params, False, total)
    if not sGui:
        isMatchNextPage, sNextUrl = cParser.parseSingleResult(sHtmlContent, 'class="navigation.*?<span>\d+</span> <a href="([^"]+)">\d+<')
        if isMatchNextPage:
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('movies')
        oGui.setEndOfDirectory()


def showHosters():
    hosters = []
    sUrl = ParameterHandler().getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = 'class="tabs-b video-box">.*?</div>'
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        isMatch, aResult = cParser.parse(sContainer, 'data-src="([^"]+)')
    if isMatch:
        for sUrl in aResult:
            hoster = {'link': sUrl, 'name': cParser.urlparse(sUrl)}
            hosters.append(hoster)
        if hosters:
            hosters.append('getHosterUrl')
        return hosters


def getHosterUrl(sUrl=False):
    if 'streamcrypt.net' in sUrl:
        oRequest = cRequestHandler(sUrl, caching=False)
        oRequest.request()
        sUrl = oRequest.getRealUrl()
    return [{'streamUrl': sUrl, 'resolved': False}]


def showSearch():
    sSearchText = cGui().showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    cGui().setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_SEARCH, oGui, sSearchText)
