# -*- coding: utf-8 -*-
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.gui import cGui

SITE_IDENTIFIER = 'hd-streams_to'
SITE_NAME = 'HD-Streams.to'
SITE_ICON = 'hd-streams_to.png'
URL_MAIN = 'https://hd-streams.to/de/'
URL_FILME = URL_MAIN + 'movies/'
URL_SERIE = URL_MAIN + 'tvshows/'
URL_SEARCH = URL_MAIN + '?s=%s'


def load():
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_FILME)
    cGui().addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_SERIE)
    cGui().addFolder(cGuiElement('Serien', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sCont', 'Genres')
    cGui().addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showValue'), params)
    params.setParam('sCont', 'Jahr')
    cGui().addFolder(cGuiElement('Jahr', SITE_IDENTIFIER, 'showValue'), params)
    cGui().addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    cGui().setEndOfDirectory()


def showValue():
    params = ParameterHandler()
    sHtmlContent = cRequestHandler(URL_MAIN).request()
    isMatch, sContainer = cParser.parse(sHtmlContent, '">%s<.*?</ul>' % params.getValue('sCont'))
    if isMatch:
        pattern = '<a[^>]*href="([^"]+)".*?>([^"]+)</a>'
        isMatch, aResult = cParser.parse(sContainer[0], pattern)
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
    pattern = '<article id="post-\d.*?src="([^"]+).*?href="([^"]+)">([^<]+).*?span>([\d]+).*?texto">([^<]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        pattern = '<article>.*?<img src="([^"]+).*?href="([^"]+)">([^<]+)(.*?)contenido">([^"]+)</div>'
        isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sThumbnail, sUrl, sName, sDummy, sDesc in aResult:
        isYear, sYear = cParser.parseSingleResult(sDummy, '(\d{4})')
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        isTvshow = True if 'tvshow' in sUrl else False
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons' if isTvshow else 'showHosters')
        oGuiElement.setMediaType('tvshow' if isTvshow else 'movie')
        oGuiElement.setThumbnail(sThumbnail)
        if isYear:
            oGuiElement.setYear(sYear)
        oGuiElement.setDescription(sDesc)
        params.setParam('entryUrl', sUrl)
        params.setParam('sName', sName)
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
    params = ParameterHandler()
    entryUrl = params.getValue('entryUrl')
    sThumbnail = params.getValue('sThumbnail')
    sTVShowTitle = params.getValue('sName')
    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = "<span[^>]class='title'>.*?([\d]+)"
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        cGui().showInfo()
        return

    isDesc, sDesc = cParser.parse(sHtmlContent, 'class="wp-content">([^"]+)<div')
    total = len(aResult)
    for sSeasonNr in aResult:
        oGuiElement = cGuiElement('Staffel ' + sSeasonNr, SITE_IDENTIFIER, 'showEpisodes')
        oGuiElement.setMediaType('season')
        oGuiElement.setSeason(sSeasonNr)
        oGuiElement.setTVShowTitle(sTVShowTitle)
        oGuiElement.setThumbnail(sThumbnail)
        if isDesc:
            oGuiElement.setDescription(sDesc[0])
        params.setParam('sSeasonNr', int(sSeasonNr))
        cGui().addFolder(oGuiElement, params, True, total)
    cGui().setView('seasons')
    cGui().setEndOfDirectory()


def showEpisodes():
    params = ParameterHandler()
    sThumbnail = params.getValue('sThumbnail')
    entryUrl = params.getValue('entryUrl')
    sSeasonNr = params.getValue('sSeasonNr')
    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = "title'>Season[^>]%s[^<]<i>.*?[^<]<i>.*?></li></ul>" % sSeasonNr
    isMatch, sContainer = cParser.parse(sHtmlContent, pattern)
    if isMatch:
        pattern = "numerando'>[^-]*-\s*(\d+)<.*?<a[^>]*href='([^']+)'>([^<]+)"
        isMatch, aResult = cParser.parse(sContainer[0], pattern)
    if not isMatch:
        cGui().showInfo()
        return

    isDesc, sDesc = cParser.parse(sHtmlContent, 'class="wp-content">([^"]+)<div')
    total = len(aResult)
    for sEpisodeNr, sUrl, sName in aResult:
        oGuiElement = cGuiElement(sEpisodeNr + ' - ' + sName, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setSeason(sSeasonNr)
        oGuiElement.setEpisode(sEpisodeNr)
        oGuiElement.setThumbnail(sThumbnail)
        if isDesc:
            oGuiElement.setDescription(sDesc[0])
        oGuiElement.setMediaType('episode')
        params.setParam('entryUrl', sUrl)
        cGui().addFolder(oGuiElement, params, False, total)
    cGui().setView('episodes')
    cGui().setEndOfDirectory()


def showHosters():
    hosters = []
    sUrl = ParameterHandler().getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    isMatch, aResult = cParser().parse(sHtmlContent, "</span><a data-id='([\d]+)'")
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
            sHtmlContent = oRequest.request()
            isMatch, aResult = cParser().parse(sHtmlContent, "src=[^>]([^']+)")
            for sUrl in aResult:
                Request = cRequestHandler(sUrl, caching=False)
                Request.addHeaderEntry('Referer', sUrl)
                Request.request()
                sUrl = Request.getRealUrl()
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
    showEntries(URL_SEARCH % cParser().quotePlus(sSearchText), oGui, sSearchText)
