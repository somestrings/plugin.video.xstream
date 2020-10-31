# -*- coding: utf-8 -*-
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.gui import cGui
from resources.lib.config import cConfig

SITE_IDENTIFIER = 'cinenator'
SITE_NAME = 'Cinenator'
SITE_ICON = 'cinenator.png'
URL_MAIN = 'https://cinenator.to/'
URL_FILME = URL_MAIN + 'movies'
URL_SEARCH = URL_MAIN + '?s=%s'


def load():
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_FILME)
    cGui().addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('Value', 'Genres')
    cGui().addFolder(cGuiElement('Genres', SITE_IDENTIFIER, 'showValue'), params)
    params.setParam('Value', 'Release year')
    cGui().addFolder(cGuiElement('Erscheinungsjahr', SITE_IDENTIFIER, 'showValue'), params)
    cGui().addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    cGui().setEndOfDirectory()


def showValue():
    params = ParameterHandler()
    sHtmlContent = cRequestHandler(URL_MAIN).request()
    pattern = '<h2>%s</h2>.*?</ul></nav>' % params.getValue('Value')
    isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = '<a[^>]*href="([^"]+)".*?>([^"]+)</a>'
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
    sHtmlContent = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False)).request()
    pattern = 'class="item[^>]movies">.*?src="([^"]+).*?class="data.*?href="([^"]+)">([^<]+)(.*?)class="texto">(.*?)</div>'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        pattern = '<div[^>]*class="search_page_form">.*?</div></div></div>'
        isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, pattern)
        if isMatch:
            pattern = 'src="([^"]+).*?href="([^"]+).*?>([^<]+)(.*?)contenido">([^"]+)</p>'
            isMatch, aResult = cParser.parse(sHtmlContainer, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sThumbnail, sUrl, sName, sValue, sDesc in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        sThumbnail = cParser.replace('-\d+x\d+\.', '.', sThumbnail)
        isTvshow = True if "tvshow" in sUrl else False
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons' if isTvshow else 'showHosters')
        oGuiElement.setMediaType('tvshow' if isTvshow else 'movie')
        oGuiElement.setThumbnail(sThumbnail)
        isYear, sYear = cParser.parse(sValue, '>([\d]+)<')
        isDuration, sDuration = cParser.parse(sValue, '<span>([\d]+)[^>]min')
        if isYear:
            oGuiElement.setYear(sYear[0])
        if isDuration:
            oGuiElement.addItemValue('duration', int(sDuration[0]) * 60)
        oGuiElement.setDescription(sDesc)
        params.setParam('entryUrl', sUrl)
        params.setParam('sName', sName)
        params.setParam('sThumbnail', sThumbnail)
        oGui.addFolder(oGuiElement, params, isTvshow, total)
    if not sGui and not sSearchText:
        pattern = "current[^>]>\d+</span>[^>]*href='([^']+)"
        isMatchNextPage, sNextUrl = cParser.parseSingleResult(sHtmlContent, pattern)
        if isMatchNextPage:
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('tvshows' if 'serien' in entryUrl else 'movies')
        oGui.setEndOfDirectory()


def showSeasons():
    params = ParameterHandler()
    entryUrl = params.getValue('entryUrl')
    sThumbnail = params.getValue('sThumbnail')
    sTVShowTitle = params.getValue('sName')
    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = '<span[^>]class="title">.*?([\d]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        cGui().showInfo()
        return

    total = len(aResult)
    for sSeasonNr in aResult:
        oGuiElement = cGuiElement('Staffel ' + sSeasonNr, SITE_IDENTIFIER, 'showEpisodes')
        oGuiElement.setMediaType('season')
        oGuiElement.setTVShowTitle(sTVShowTitle)
        oGuiElement.setSeason(sSeasonNr)
        oGuiElement.setThumbnail(sThumbnail)
        params.setParam('sSeasonNr', int(sSeasonNr))
        cGui().addFolder(oGuiElement, params, True, total)
    cGui().setView('seasons')
    cGui().setEndOfDirectory()


def showEpisodes():
    params = ParameterHandler()
    sTVShowTitle = params.getValue('TVShowTitle')
    entryUrl = params.getValue('entryUrl')
    sSeasonNr = params.getValue('sSeasonNr')
    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = '<span[^>]*class="se-t[^"]*">%s</span>.*?<ul[^>]*class="episodios"[^>]*>(.*?)</ul>' % sSeasonNr
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = '<a[^>]*href="([^"]+)"[^>]*>\s*(?:<img[^>]*src="([^"]+)?).*?<div[^>]*class="numerando">[^-]*-\s*(\d+)\s*?</div>.*?<a[^>]*>([^<]*)</a>'
        isMatch, aResult = cParser.parse(sContainer, pattern)
    if not isMatch:
        cGui().showInfo()
        return

    total = len(aResult)
    for sUrl, sThumbnail, sEpisodeNr, sName in aResult:
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setTVShowTitle(sTVShowTitle)
        oGuiElement.setSeason(sSeasonNr)
        oGuiElement.setEpisode(sEpisodeNr)
        sThumbnail = cParser.replace('-\d+x\d+\\.', '.', sThumbnail)
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setMediaType('episode')
        params.setParam('entryUrl', sUrl)
        cGui().addFolder(oGuiElement, params, False, total)
    cGui().setView('episodes')
    cGui().setEndOfDirectory()


def showHosters():
    hosters = []
    sUrl = ParameterHandler().getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = "domain=([^']+).*?href='([^']+).*?quality'>([^<]+).*?<td>([^<]+)"
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if isMatch:
        for sName, sUrl, sQualy, sLang in aResult:
            if 'filecrypt' not in sName:
                if cConfig().getSetting('hosterSelect') == 'Auto':
                    sUrl = getlinks(sUrl)
                hoster = {'link': sUrl, 'name': sName + ' ' + sLang + ' ' + sQualy}
                hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getlinks(sUrl):
    sHtmlContent = cRequestHandler(sUrl).request()
    isMatch, sUrl = cParser.parseSingleResult(sHtmlContent, 'id="link.*?href="([^"]+)"')
    if isMatch:
        return sUrl


def getHosterUrl(sUrl=False):
    if not cConfig().getSetting('hosterSelect') == 'Auto':
        sUrl = getlinks(sUrl)
    return [{'streamUrl': sUrl, 'resolved': False}]


def showSearch():
    sSearchText = cGui().showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    cGui().setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_SEARCH % cParser().quotePlus(sSearchText), oGui, sSearchText)
