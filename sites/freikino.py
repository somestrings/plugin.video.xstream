# -*- coding: utf-8 -*-
from resources.lib import logger
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser

SITE_IDENTIFIER = 'freikino'
SITE_NAME = 'FreiKino'
SITE_ICON = 'freikino.png'

URL_MAIN = 'https://freikino.com'
URL_FILME = URL_MAIN + '/top-movies'
URL_RELEASE = URL_MAIN + '/latest-release'
URL_POPULAR = URL_MAIN + '/popular'
URL_SERIE = URL_MAIN + '/top-tv-series'
URL_SEARCH = URL_MAIN + '/search?q=%s'


def load():
    logger.info('Load %s' % SITE_NAME)
    oGui = cGui()
    params = ParameterHandler()
    params.setParam('sUrl', URL_FILME)
    oGui.addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_SERIE)
    oGui.addFolder(cGuiElement('Serien', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_RELEASE)
    oGui.addFolder(cGuiElement('Zuletzt Veröffentlicht', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_POPULAR)
    oGui.addFolder(cGuiElement('Beliebt', SITE_IDENTIFIER, 'showEntries'), params)
    oGui.addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showGenre'), params)
    oGui.addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    oGui.setEndOfDirectory()


def showGenre():
    params = ParameterHandler()
    sHtmlContent = cRequestHandler('https://freikino.com/genre-list').request()
    pattern = 'genreListData">.*?</div><footer>'
    isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, pattern)

    if isMatch:
        isMatch, aResult = cParser.parse(sHtmlContainer, 'href="([^"]+).*?>([^<]+)')
    if not isMatch:
        cGui().showInfo('xStream', 'Es wurde kein Eintrag gefunden')
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
    sHtmlContent = oRequest.request()
    pattern = 'single-list-movie">.*?src="([^"]+).*?href="([^"]+)">([^<]+).*?<li>([^<]+)'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)

    if not isMatch:
        if not sGui: oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    cf = cRequestHandler.createUrl(entryUrl, oRequest)
    total = len(aResult)
    for sThumbnail, sUrl, sName, sDesc in aResult:
        isTvshow = True if '-s-' in sUrl else False
        if sSearchText and not cParser().search(sSearchText, sName):
            continue

        isMatch, sYear = cParser.parse(sName, '(.*?)\((\d*)\)')
        for name, year in sYear:
            sName = name
            sYear = year
            break

        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons' if isTvshow else 'showHosters')
        oGuiElement.setThumbnail(sThumbnail + cf)
        oGuiElement.setFanart(sThumbnail + cf)
        oGuiElement.setYear(sYear)
        oGuiElement.setDescription(sDesc)
        oGuiElement.setMediaType('tvshow' if isTvshow else 'movie')
        params.setParam('entryUrl', URL_MAIN + sUrl)
        params.setParam('sThumbnail', sThumbnail)
        params.setParam('sName', sName)
        oGui.addFolder(oGuiElement, params, isTvshow, total)
    if not sGui:
        isMatchNextPage, sNextUrl = cParser().parseSingleResult(sHtmlContent, 'next"><a href="([^"]+)')
        if isMatchNextPage:
            params.setParam('sUrl', URL_MAIN + sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('tvshow' if isTvshow else 'movie')
        oGui.setEndOfDirectory()


def showSeasons():
    oGui = cGui()
    params = ParameterHandler()
    sUrl = params.getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    sThumbnail = params.getValue('sThumbnail')
    sTVShowTitle = params.getValue('sName')
    pattern = 'episodeBBox([\d]+)'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)

    if not isMatch:
        oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    isDesc, sDesc = cParser.parse(sHtmlContent, 'name="description" content="([^"]+)')
    total = len(aResult)
    for sSeasonNr in aResult:
        oGuiElement = cGuiElement('Staffel ' + sSeasonNr, SITE_IDENTIFIER, 'showEpisodes')
        oGuiElement.setMediaType('season')
        oGuiElement.setSeason(sSeasonNr)
        if isDesc:
            oGuiElement.setDescription(sDesc[0])
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setFanart(sThumbnail)
        params.setParam('sSeasonNr', sSeasonNr)
        oGui.addFolder(oGuiElement, params, True, total)
    oGui.setView('seasons')
    oGui.setEndOfDirectory()


def showEpisodes():
    oGui = cGui()
    params = ParameterHandler()
    sUrl = params.getValue('entryUrl')
    sSeasonNr = params.getValue('sSeasonNr')
    sThumbnail = params.getValue('sThumbnail')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = 'episodeBBox%s">.*?</div>' % sSeasonNr
    isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, pattern)

    if isMatch:
        pattern = 'href="([^"]+).*?">(\d+)'
        isMatch, aResult = cParser.parse(sHtmlContainer, pattern)
    if not isMatch:
        oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    isDesc, sDesc = cParser.parse(sHtmlContent, 'name="description" content="([^"]+)')
    total = len(aResult)
    for sUrl, sEpisodeNr in aResult:
        oGuiElement = cGuiElement('Folge ' + sEpisodeNr, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setFanart(sThumbnail)
        if isDesc:
            oGuiElement.setDescription(sDesc[0])
        params.setParam('entryUrl', URL_MAIN + sUrl)
        oGui.addFolder(oGuiElement, params, False, total)
    oGui.setView('episodes')
    oGui.setEndOfDirectory()


def showHosters():
    params = ParameterHandler()
    sUrl = params.getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = 'mirror_box">.*?data-end="([\d]+).*?data-server="([\d]+).*?data-episode="([\d]+).*?<span>([^<]+)'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    hosters = []
    if isMatch:
        for sEnd, sServer, sEpisode, sName in aResult:
            mirror = 1
            mirror = int(sEnd)
            for i in range(1, mirror + 1):
                mirrorName = ''
                if mirror > 1:
                    mirrorName = '  Mirror ' + str(i)
                params.setParam('id', str(i))
                sUrl = 'https://freikino.com/mirror?episode=' + sEpisode + '&next=' + str(i) + '&server=' + sServer
                hoster = {'link': sUrl, 'name': sName + mirrorName}
                hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    oRequest = cRequestHandler(sUrl)
    sHtmlContent = oRequest.request()
    isMatch, aResult = cParser().parse(sHtmlContent, 'response":"([^"]+)')
    if aResult[0].startswith('//'):
        aResult[0] = 'https:' + aResult[0]
    return [{'streamUrl': aResult[0], 'resolved': False}]


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    oGui.setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_SEARCH % sSearchText, oGui, sSearchText)
