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
    params.setParam('value', 'Genre')
    cGui().addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showValue'), params)
    params.setParam('value', 'Year')
    cGui().addFolder(cGuiElement('Jahr', SITE_IDENTIFIER, 'showValue'), params)
    params.setParam('value', 'Country')
    cGui().addFolder(cGuiElement('Land', SITE_IDENTIFIER, 'showValue'), params)
    cGui().addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'), params)
    cGui().setEndOfDirectory()


def showValue():
    params = ParameterHandler()
    value = params.getValue("value")
    sHtmlContent = cRequestHandler(params.getValue('sUrl')).request()
    pattern = 'class="nav-title">%s</div>(.*?)</ul>' % value
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        isMatch, aResult = cParser.parse(sContainer, 'href="([^"]+)">([^<]+)')
    if not isMatch:
        cGui().showInfo()
        return

    for sUrl, sName in aResult:
        params.setParam('sUrl', URL_MAIN + sUrl)
        cGui().addFolder(cGuiElement(sName, SITE_IDENTIFIER, 'showEntries'), params)
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
    pattern = 'class="th-item.*?href="([^"]+).*?fx-last">([^<]+)(.*?)</article>'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sUrl, sName, sDummy in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showHosters')
        isThumbnail, sThumbnail = cParser.parse(sDummy, 'data-src="([^"]+)')
        if isThumbnail:
            oGuiElement.setThumbnail(URL_MAIN + sThumbnail[0])
        isYear, sYear = cParser.parseSingleResult(sDummy, '">(\d{4})<')
        if isYear:
            oGuiElement.setYear(sYear)
        isDesc, sDesc = cParser.parseSingleResult(sDummy, 'text">([^<]+)')
        if isDesc:
            oGuiElement.setDescription(sDesc)
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
    isMatch, aResult = cParser.parse(sHtmlContent, 'data-src="([^"]+)"\Wf')
    if isMatch:
        for sUrl in aResult:
            if 'youtube' in sUrl:
                continue
            if 'streamcrypt.net' in sUrl:
                oRequest = cRequestHandler(sUrl, caching=False)
                oRequest.request()
                sUrl = oRequest.getRealUrl()
            hoster = {'link': sUrl, 'name': cParser.urlparse(sUrl)}
            hosters.append(hoster)
        if hosters:
            hosters.append('getHosterUrl')
        return hosters


def getHosterUrl(sUrl=False):
    return [{'streamUrl': sUrl, 'resolved': False}]


def showSearch():
    sSearchText = cGui().showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    cGui().setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_SEARCH, oGui, sSearchText)
