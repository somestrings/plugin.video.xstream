# -*- coding: utf-8 -*-
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.gui import cGui

SITE_IDENTIFIER = 'stream_to'
SITE_NAME = 'Stream.to'
SITE_ICON = 'stream_to.png'
URL_MAIN = 'https://stream.to'
URL_MOVIES = URL_MAIN + '/de/movie?sort='
URL_SHOWS = URL_MAIN + '/de/tvshow?sort='
AJAX = URL_MAIN + '/ajax/load_player/'
HOSTER = URL_MAIN + '/de/out/'
URL_SEARCH = URL_MAIN + '/search/%s'


def load():
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_MOVIES)
    cGui().addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showMenu'), params)
    params.setParam('sUrl', URL_SHOWS)
    cGui().addFolder(cGuiElement('Serien', SITE_IDENTIFIER, 'showMenu'), params)
    cGui().addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showGenre'), params)
    cGui().addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    cGui().setEndOfDirectory()


def showMenu():
    params = ParameterHandler()
    sUrl = params.getValue('sUrl')
    params.setParam('sUrl', sUrl + 'view')
    cGui().addFolder(cGuiElement('Am meisten gesehn', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', sUrl + 'latest')
    cGui().addFolder(cGuiElement('Zuletzt hinzugefügt', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', sUrl + 'favorite')
    cGui().addFolder(cGuiElement('Am meisten favorisiert', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', sUrl + 'rating')
    cGui().addFolder(cGuiElement('Am besten bewertet', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', sUrl + 'imdb')
    cGui().addFolder(cGuiElement('Top IMDb', SITE_IDENTIFIER, 'showEntries'), params)
    cGui().setEndOfDirectory()


def showGenre():
    params = ParameterHandler()
    sHtmlContent = cRequestHandler(URL_MAIN).request()
    pattern = 'title="Genre">.*?</ul>'
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = 'href="([^"]+)[^>]*title="([^"]+)'
        isMatch, aResult = cParser.parse(sContainer, pattern)
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
    sHtmlContent = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False)).request()
    pattern = 'data-movie-id="(\d+)".*?href="([^"]+).*?oldtitle="([^"]+).*?data-original="([^"]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sID, sUrl, sName, sThumbnail in aResult:
        if sSearchText and not cParser.search(sSearchText, sName):
            continue
        isTvshow = True if 'series' in sUrl else False
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons' if isTvshow else 'showHosters')
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setMediaType('tvshow' if isTvshow else 'movie')
        params.setParam('sID', AJAX + sID)
        params.setParam('entryUrl', URL_MAIN + sUrl)
        params.setParam('sThumbnail', sThumbnail)
        oGui.addFolder(oGuiElement, params, isTvshow, total)
    if not sGui:
        isMatchNextPage, sNextUrl = cParser.parseSingleResult(sHtmlContent, 'rel="next" href="([^"]+)')
        if isMatchNextPage:
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('tvshows' if 'series' in sUrl else 'movies')
        oGui.setEndOfDirectory()


def showSeasons():
    params = ParameterHandler()
    entryUrl = params.getValue('entryUrl')
    sHtmlContent = cRequestHandler(entryUrl).request()
    isMatch, aResult = cParser.parse(sHtmlContent, 'id="session-(\d+)"')
    if not isMatch:
        cGui().showInfo()
        return

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, 'class="desc">([^<]+)')
    total = len(aResult)
    for sSeason in aResult:
        oGuiElement = cGuiElement('Staffel ' + sSeason, SITE_IDENTIFIER, 'showEpisodes')
        oGuiElement.setMediaType('season')
        oGuiElement.setSeason(sSeason)
        oGuiElement.setThumbnail(params.getValue('sThumbnail'))
        if isDesc:
            oGuiElement.setDescription(sDesc)
        params.setParam('Season', sSeason)
        cGui().addFolder(oGuiElement, params, True, total)
    cGui().setView('seasons')
    cGui().setEndOfDirectory()


def showEpisodes():
    params = ParameterHandler()
    entryUrl = params.getValue('entryUrl')
    sSeason = params.getValue('Season')
    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = '<div id="session-%s".*?</div></div>' % sSeason
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = 'href="/de/episode/(\d+).*?episode-(\d+)"'
        isMatch, aResult = cParser.parse(sContainer, pattern)
    if not isMatch:
        cGui().showInfo()
        return

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, 'class="desc">([^<]+)')
    total = len(aResult)
    for sID, sEpisode in aResult:
        oGuiElement = cGuiElement('Folge ' + sEpisode, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setMediaType('season')
        oGuiElement.setSeason(sSeason)
        oGuiElement.setEpisode(sEpisode)
        oGuiElement.setMediaType('episode')
        oGuiElement.setThumbnail(params.getValue('sThumbnail'))
        if isDesc:
            oGuiElement.setDescription(sDesc)
        params.setParam('sID', AJAX + sID)
        cGui().addFolder(oGuiElement, params, False, total)
    cGui().setView('episodes')
    cGui().setEndOfDirectory()


def showHosters():
    hosters = []
    sID = ParameterHandler().getValue('sID')
    sHtmlContent = cRequestHandler(sID).request()
    isMatch, aResult = cParser.parse(sHtmlContent, 'id="(link[^"]+)')
    if isMatch:
        for sUrl in aResult:
            oRequest = cRequestHandler(HOSTER + sUrl, caching=False)
            oRequest.request()
            sUrl = oRequest.getRealUrl()
            hoster = {'link': sUrl, 'name': cParser.urlparse(sUrl)}
            hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    if 'thevideos.ga' in sUrl:
        from resources.lib import jsunpacker
        oRequest = cRequestHandler(sUrl, caching=False)
        oRequest.addHeaderEntry('Referer', 'https://stream.to/')
        sHtmlContent = oRequest.request()
        isMatch, sUrl = cParser.parse(sHtmlContent, '(eval\s*\(function.*?)</script>')
        if isMatch:
            sHtmlContent = jsunpacker.unpack(sUrl[0])
            isMatch, sUrl = cParser.parseSingleResult(sHtmlContent, ",src.*?'([^']+)")
            if isMatch:
                oRequest = cRequestHandler('https://thevideos.ga/' + sUrl, caching=False)
                sUrl = _redirectHoster('https://thevideos.ga/' + sUrl)
                return [{'streamUrl': sUrl, 'resolved': True}]
    else:
        return [{'streamUrl': sUrl, 'resolved': False}]


def showSearch():
    sSearchText = cGui().showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    cGui().setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_SEARCH % cParser.quotePlus(sSearchText), oGui, sSearchText)


def _redirectHoster(url):
    try:
        from urllib2 import build_opener, HTTPError
    except ImportError:
        from urllib.error import HTTPError
        from urllib.request import build_opener
    opener = build_opener()
    opener.addheaders = [('Referer', url)]
    try:
        resp = opener.open(url)
        if url != resp.geturl():
            return resp.geturl()
        else:
            return url
    except HTTPError as e:
        if e.code == 403:
            if url != e.geturl():
                return e.geturl()
        raise
