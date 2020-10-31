# -*- coding: utf-8 -*-
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.gui import cGui

SITE_IDENTIFIER = 'streamkiste'
SITE_NAME = 'StreamKiste'
SITE_ICON = 'streamkiste.png'

URL_MAIN = 'https://streamkiste.life/'
URL_AJAX = URL_MAIN + '?c=movie&m=filter2&page={0}&order_by={1}&language=Deutsch&genre={2}'
URL_SEARCH = URL_MAIN + '?c=movie&m=filter2&page=1&position=0&order_by=&keyword=%s'


def load():
    oGui = cGui()
    logger.info("Load %s" % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_AJAX)
    oGui.addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showFilme'), params)
    oGui.addFolder(cGuiElement('Serien', SITE_IDENTIFIER, 'showSerien'), params)
    oGui.addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'), params)
    oGui.setEndOfDirectory()


def showFilme():
    params = ParameterHandler()
    params.setParam('Page', '1')
    params.setParam('order', 'releases')
    cGui().addFolder(cGuiElement('Hinzugefügt', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('order', 'updates')
    cGui().addFolder(cGuiElement('Updates', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('order', 'rating')
    cGui().addFolder(cGuiElement('TOP IMDb', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('order', 'name')
    cGui().addFolder(cGuiElement('A-Z', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('order', 'releases')
    cGui().addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showGenre'), params)
    cGui().setEndOfDirectory()


def showSerien():
    params = ParameterHandler()
    params.setParam('Page', '1')
    params.setParam('order', 'tvshows')
    cGui().addFolder(cGuiElement('Hinzugefügt', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('order', 'u-tvshows')
    cGui().addFolder(cGuiElement('Updates', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('order', 'r-tvshows')
    cGui().addFolder(cGuiElement('TOP IMDb', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('order', 'name-tvshows')
    cGui().addFolder(cGuiElement('A-Z', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('order', 'tvshows')
    cGui().addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showGenre'), params)
    cGui().setEndOfDirectory()


def showGenre():
    params = ParameterHandler()
    sHtmlContent = cRequestHandler(URL_MAIN + 'movies/').request()
    isMatch, aResult = cParser.parse(sHtmlContent, 'genre=([^&]+)')
    if not isMatch:
        cGui().showInfo()
        return

    for sID in aResult:
        params.setParam('Genre', sID)
        cGui().addFolder(cGuiElement(sID, SITE_IDENTIFIER, 'showEntries'), params)
    cGui().setEndOfDirectory()


def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    order = params.getValue('order')
    Page = params.getValue('Page')
    if params.exist('Genre'):
        genre = params.getValue('Genre')
    else:
        genre = ''
    if not entryUrl:
        entryUrl = params.getValue('sUrl')
        entryUrl = entryUrl.format(Page, order, genre)
    oRequest = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False))
    oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
    oRequest.addHeaderEntry('Referer', URL_MAIN)
    sHtmlContent = oRequest.request()
    pattern = 'class="clip">.*?src="([^"]+).*?href="([^"]+)(.*?)f_title[^>]>([^<]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sThumbnail, sUrl, sDummy, sName in aResult:
        isYear, sYear = cParser.parseSingleResult(sDummy, "f_year'>(\d{4})")
        isDesc, sDesc = cParser.parseSingleResult(sDummy, 'Description">([^<]+)')
        isRating, sRating = cParser.parseSingleResult(sDummy, 'fa-star">.*?(\d+.\d+)<')
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        isTvshow = True if 'staffel' in sName.lower() or 'season' in sName.lower() else False
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons' if isTvshow else 'showHosters')
        oGuiElement.setThumbnail('https:' + sThumbnail)
        if isYear:
            oGuiElement.setYear(sYear)
        if isDesc:
            oGuiElement.setDescription(sDesc)
        if isRating:
            oGuiElement.addItemValue('rating', float(sRating.replace(',', '.')))
        oGuiElement.setMediaType('tvshow' if isTvshow else 'movie')
        params.setParam('entryUrl', sUrl)
        params.setParam('sThumbnail', 'https:' + sThumbnail)
        oGui.addFolder(oGuiElement, params, isTvshow, total)
    if not sGui and not sSearchText:
        params.setParam('Page', (int(Page) + 1))
        params.setParam('sUrl', URL_AJAX)
        oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('tvshows' if 'staffel' in sName.lower() or 'season' in sName.lower() else 'movies')
        oGui.setEndOfDirectory()


def showSeasons():
    params = ParameterHandler()
    sUrl = params.getValue('entryUrl')
    sThumbnail = params.getValue('sThumbnail')
    sHtmlContent = cRequestHandler(sUrl).request()
    isMatch, aResult = cParser().parse(sHtmlContent, 'class="seasons.*?title=".*?(\d+)"')
    if not isMatch:
        cGui().showInfo()
        return

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, 'e><meta content="([^"]+)')
    isFanart, sFanart = cParser.parseSingleResult(sHtmlContent, 'url=([^&]+)')
    total = len(aResult)
    for sSeasonNr in aResult[::-1]:
        oGuiElement = cGuiElement('Staffel ' + sSeasonNr, SITE_IDENTIFIER, 'showEpisodes')
        oGuiElement.setMediaType('season')
        oGuiElement.setSeason(sSeasonNr)
        oGuiElement.setThumbnail(sThumbnail)
        if isFanart:
            oGuiElement.setFanart('https:' + sFanart)
            params.setParam('sFanart', 'https:' + sFanart)
        if isDesc:
            oGuiElement.setDescription(sDesc)
        params.setParam('season', sSeasonNr)
        
        cGui().addFolder(oGuiElement, params, True, total)
    cGui().setView('seasons')
    cGui().setEndOfDirectory()


def showEpisodes():
    params = ParameterHandler()
    sUrl = params.getValue('entryUrl')
    sThumbnail = params.getValue('sThumbnail')
    sFanart = params.getValue('sFanart')
    sSeason = params.getValue('season')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = "Staffel:[^>]%s.*?section-header" % sSeason
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = "href='([^']+).*?>#(\d+)<"
        isMatch, aResult = cParser.parse(sContainer, pattern)
    if not isMatch:
        cGui().showInfo()
        return

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, 'e><meta content="([^"]+)')
    total = len(aResult)
    for sUrl, sName in aResult[::-1]:
        oGuiElement = cGuiElement('Folge ' + str(sName), SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setFanart(sFanart)
        oGuiElement.setSeason(sSeason)
        oGuiElement.setEpisode(sName)
        oGuiElement.setMediaType('episode')
        params.setParam('entryUrl', sUrl)
        if isDesc:
            oGuiElement.setDescription(sDesc)
        cGui().addFolder(oGuiElement, params, False, total)
    cGui().setView('episodes')
    cGui().setEndOfDirectory()


def showHosters():
    hosters = []
    sUrl = ParameterHandler().getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = "href='([^']+)'[^>]target.*?<mark>([^<]+)</mark></span>[^>]*<span"
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if isMatch:
        for sUrl, sLang in sorted(aResult):
            if sUrl.startswith('//'):
                sUrl = 'https:' + sUrl
            if 'streamcrypt' in sUrl:
                oRequest = cRequestHandler(sUrl, caching=False)
                oRequest.request()
                sUrl = oRequest.getRealUrl()
            if 'imdb' in sUrl or 'youtube' in sUrl:
                continue
            hoster = {'link': sUrl, 'name': cParser.urlparse(sUrl) + ' ' + sLang}
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
