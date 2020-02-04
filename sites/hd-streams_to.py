# -*- coding: utf-8 -*-
from resources.lib import logger
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler2 import cRequestHandler
from resources.lib.parser import cParser

SITE_IDENTIFIER = 'hd-streams_to'
SITE_NAME = 'HD-Streams.to'
SITE_ICON = 'hd-streams_to.png'
URL_MAIN = 'https://hd-streams.to/de/'
URL_FILME = URL_MAIN + 'movies/'
URL_SERIE = URL_MAIN + 'tvshows/'
URL_SEARCH = URL_MAIN + '?s=%s'


def load():
    logger.info("Load %s" % SITE_NAME)
    oGui = cGui()
    params = ParameterHandler()
    params.setParam('sUrl', URL_FILME)
    oGui.addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_SERIE)
    oGui.addFolder(cGuiElement('Serien', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sCont', 'Genres')
    oGui.addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showValue'), params)
    params.setParam('sCont', 'Jahr')
    oGui.addFolder(cGuiElement('Jahr', SITE_IDENTIFIER, 'showValue'), params)
    oGui.addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    oGui.setEndOfDirectory()


def showValue():
    oGui = cGui()
    params = ParameterHandler()
    sHtmlContent = cRequestHandler(URL_MAIN).request()
    isMatch, sContainer = cParser.parse(sHtmlContent, '">%s<.*?</ul>' % params.getValue('sCont'))

    if isMatch:
        pattern = '<a[^>]*href="([^"]+)".*?>([^"]+)</a>'
        isMatch, aResult = cParser.parse(sContainer[0], pattern)
    if not isMatch:
        oGui.showInfo()
        return

    for sUrl, sName in aResult:
        params.setParam('sUrl', sUrl)
        oGui.addFolder(cGuiElement(sName, SITE_IDENTIFIER, 'showEntries'), params)
    oGui.setEndOfDirectory()


def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl: entryUrl = params.getValue('sUrl')
    oRequest = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False))
    sHtmlContent = oRequest.request()
    pattern = '<article id="post-\d.*?src="([^"]+).*?href="([^"]+)">([^<]+).*?span>([\d]+).*?texto">([^<]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)

    if not isMatch:
        pattern = '<article>.*?<img src="([^"]+).*?href="([^"]+)">([^<]+).*?year">([\d]+).*?contenido">([^"]+)</div>'
        isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    cf = cRequestHandler.createUrl(entryUrl, oRequest)
    total = len(aResult)
    for sThumbnail, sUrl, sName, sYear, sDesc in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        sThumbnail = sThumbnail + cf
        isTvshow = True if 'tvshow' in sUrl else False
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons' if isTvshow else 'showHosters')
        oGuiElement.setMediaType('tvshow' if isTvshow else 'movie')
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setFanart(sThumbnail)
        oGuiElement.setYear(sYear)
        oGuiElement.setDescription(sDesc)
        params.setParam('entryUrl', sUrl)
        params.setParam('sThumbnail', sThumbnail)
        oGui.addFolder(oGuiElement, params, isTvshow, total)
    if not sGui:
        isMatchNextPage, sNextUrl = cParser().parseSingleResult(sHtmlContent, "<span[^>]class=[^>]current.*?</span><a[^>]href='([^']+)")
        if isMatchNextPage:
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('tvshows' if 'tvshow' in sUrl else 'movies')
        oGui.setEndOfDirectory()


def showSeasons():
    oGui = cGui()
    params = ParameterHandler()
    entryUrl = params.getValue('entryUrl')
    sThumbnail = params.getValue('sThumbnail')
    sTVShowTitle = params.getValue('sName')
    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = "<span[^>]class='title'>.*?([\d]+)"
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)

    if not isMatch:
        oGui.showInfo()
        return

    isDesc, sDesc = cParser.parse(sHtmlContent, 'class="wp-content">([^"]+)<div')
    total = len(aResult)
    for sSeasonNr in aResult:
        oGuiElement = cGuiElement("Staffel " + sSeasonNr, SITE_IDENTIFIER, 'showEpisodes')
        oGuiElement.setMediaType('season')
        oGuiElement.setSeason(sSeasonNr)
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setFanart(sThumbnail)
        if isDesc:
            oGuiElement.setDescription(sDesc[0])
        params.setParam('sSeasonNr', int(sSeasonNr))
        oGui.addFolder(oGuiElement, params, True, total)
    oGui.setView('seasons')
    oGui.setEndOfDirectory()


def showEpisodes():
    oGui = cGui()
    params = ParameterHandler()
    sThumbnail = params.getValue('sThumbnail')
    entryUrl = params.getValue('entryUrl')
    sSeasonNr = params.getValue('sSeasonNr')
    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = "title'>Season[^>]%s[^<]<i>.*?<span class='date'" % sSeasonNr
    isMatch, sContainer = cParser.parse(sHtmlContent, pattern)

    if isMatch:
        pattern = "numerando'>[^-]*-\s*(\d+)<.*?<a[^>]*href='([^']+)'>([^<]+)"
        isMatch, aResult = cParser.parse(sContainer[0], pattern)

    if not isMatch:
        oGui.showInfo()
        return

    isDesc, sDesc = cParser.parse(sHtmlContent, 'class="wp-content">([^"]+)<div')
    total = len(aResult)
    for sEpisodeNr, sUrl, sName in aResult:
        oGuiElement = cGuiElement(sEpisodeNr + ' - ' + sName, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setSeason(sSeasonNr)
        oGuiElement.setEpisode(sEpisodeNr)
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setFanart(sThumbnail)
        if isDesc:
            oGuiElement.setDescription(sDesc[0])
        oGuiElement.setMediaType('episode')
        params.setParam('entryUrl', sUrl)
        oGui.addFolder(oGuiElement, params, False, total)
    oGui.setView('episodes')
    oGui.setEndOfDirectory()


def showHosters():
    sUrl = ParameterHandler().getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = "</span><a data-id='([\d]+)' "
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    hosters = []
    if isMatch:
        for post in aResult:
            oRequest = cRequestHandler(URL_MAIN + 'wp-admin/admin-ajax.php')
            oRequest.addParameters('action', 'doo_player_ajax')
            oRequest.addParameters('post', post)
            oRequest.addParameters('nume', '1')
            if 'tvshows' in sUrl:
                oRequest.addParameters('type', 'tv')
            else:
                oRequest.addParameters('type', 'movie')
            oRequest.setRequestType(1)
            sHtmlContent = oRequest.request()
            isMatch, aResult = cParser().parse(sHtmlContent, "src=[^>]([^']+)")
            for sUrl in aResult:
                hoster = {'link': sUrl, 'name': '3434.uls.to'}
                hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    Request = cRequestHandler(sUrl, caching=False)
    Request.addHeaderEntry('Referer', sUrl)
    Request.request()
    return [{'streamUrl': Request.getRealUrl(), 'resolved': False}]


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    oGui.setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_SEARCH % sSearchText, oGui, sSearchText)
