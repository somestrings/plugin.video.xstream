# -*- coding: utf-8 -*-
from resources.lib import logger
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser

SITE_IDENTIFIER = 'streamking'
SITE_NAME = 'MovieKing.cc'
SITE_ICON = 'streamking.png'
URL_MAIN = 'https://movieking.cc/'
URL_FILME = URL_MAIN + 'movies.html'
URL_SERIEN = URL_MAIN + 'tv-series.html'
URL_SEARCH = URL_MAIN + 'search?q=%s'

def load():
    logger.info("Load %s" % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_FILME)
    cGui().addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_SERIEN)
    cGui().addFolder(cGuiElement('Serien', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN)
    cGui().addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showGenre'), params)
    params.setParam('sUrl', 'https://movieking.cc/year.html')
    cGui().addFolder(cGuiElement('Jahr', SITE_IDENTIFIER, 'showGenre'), params)
    cGui().addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    cGui().setEndOfDirectory()

def showGenre():
    params = ParameterHandler()
    entryUrl = params.getValue('sUrl')
    sHtmlContent = cRequestHandler(entryUrl).request()
    if 'year' in entryUrl:
        pattern = 'section-opt.*?id="footer">'
        isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    else:
        pattern = '>Genre.*?.*?class="dropdown">'
        isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = 'href="([^"]+)">([^<]+)'
        isMatch, aResult = cParser.parse(sHtmlContainer, pattern)
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
    oRequest = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False))
    sHtmlContent = oRequest.request()
    pattern = 'data-src="([^"]+)(.*?)href="([^"]+)">([^<]+)'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)

    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    cf = cRequestHandler.createUrl(entryUrl, oRequest)
    total = len(aResult)
    for sThumbnail, sType, sUrl, sName in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        isTvshow = True if 'EPISODE' in sType else False
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons' if isTvshow else 'showHosters')
        oGuiElement.setThumbnail(sThumbnail + cf)
        oGuiElement.setFanart(sThumbnail + cf)
        oGuiElement.setMediaType('tvshow' if isTvshow else 'movie')
        params.setParam('entryUrl', sUrl)
        params.setParam('sThumbnail', sThumbnail + cf)
        oGui.addFolder(oGuiElement, params, isTvshow, total)
    if not sGui:
        isMatchNextPage, sNextUrl = cParser().parseSingleResult(sHtmlContent, 'pagination.*?<a href="([^"]+)" data-ci-pagination-page="\d" rel="next">')
        if isMatchNextPage:
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('tvshow' if isTvshow else 'movie')
        oGui.setEndOfDirectory()

def showSeasons():
    params = ParameterHandler()
    sUrl = cParser.urlEncode(params.getValue('entryUrl'),':|/')
    sThumbnail = params.getValue('sThumbnail')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = 'Staffel.*?([\d]+)'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, '<p>([^<]+)')

    if not isMatch:
        cGui().showInfo()
        return

    total = len(aResult)
    for sSeasonNr in aResult:
        oGuiElement = cGuiElement('Staffel ' + sSeasonNr, SITE_IDENTIFIER, 'showEpisodes')
        oGuiElement.setMediaType('season')
        oGuiElement.setSeason(sSeasonNr)
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setFanart(sThumbnail)
        if isDesc:
            oGuiElement.setDescription(sDesc)
        params.setParam('sSeasonNr', sSeasonNr)
        cGui().addFolder(oGuiElement, params, True, total)
    cGui().setView('seasons')
    cGui().setEndOfDirectory()

def showEpisodes():
    params = ParameterHandler()
    sUrl = cParser.urlEncode(params.getValue('entryUrl'),':|/')
    sSeasonNr = params.getValue('sSeasonNr')
    sThumbnail = params.getValue('sThumbnail')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = 'Staffel[^>]*%s.*?</div>' % sSeasonNr
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)

    if isMatch:
        isMatch, aResult = cParser.parse(sContainer, 'href="([^"]+).*?>([\d]+)')
        isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, '<p>([^<]+)')
    if not isMatch:
        cGui().showInfo()
        return

    total = len(aResult)
    for sUrl, sEpisodeNr in aResult:
        oGuiElement = cGuiElement('Folge ' + sEpisodeNr, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setMediaType('episode')
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setFanart(sThumbnail)
        oGuiElement.setEpisode(sEpisodeNr)
        if isDesc:
            oGuiElement.setDescription(sDesc)
        params.setParam('entryUrl', sUrl)
        cGui().addFolder(oGuiElement, params, False, total)
    cGui().setView('episodes')
    cGui().setEndOfDirectory()

def showHosters():
    hosters = []
    sUrl = ParameterHandler().getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = 'embed-item".*?src="(http[^"]+)'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if isMatch:
        for sUrl in aResult:
            hoster = {'link': sUrl, 'name': sUrl}
            hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters

def getHosterUrl(sUrl=False):
    Request = cRequestHandler(sUrl, caching=False)
    Request.request()
    return [{'streamUrl': Request.getRealUrl(), 'resolved': False}]

def showSearch():
    sSearchText = cGui().showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    cGui().setEndOfDirectory()

def _search(oGui, sSearchText):
    showEntries(URL_SEARCH % cParser().quotePlus(sSearchText), oGui, sSearchText)
