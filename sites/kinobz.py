# -*- coding: utf-8 -*-
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.gui import cGui

SITE_IDENTIFIER = 'kinobz'
SITE_NAME = 'Kino BZ'
SITE_ICON = 'kinobz.png'
URL_MAIN = 'https://kino.bz/'
URL_KINO = URL_MAIN + 'genre/kinofilme/'
URL_FILME = URL_MAIN + 'movies/'
URL_TOP = URL_MAIN + 'imdb/'
URL_SEARCH = URL_MAIN + '?s=%s'
SITE_GLOBAL_SEARCH = False


def load():
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_KINO)
    cGui().addFolder(cGuiElement('Kinofilme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_FILME)
    cGui().addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_TOP)
    cGui().addFolder(cGuiElement('Top Filme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN)
    cGui().addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showGenre'), params)
    cGui().addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    cGui().setEndOfDirectory()


def showGenre():
    params = ParameterHandler()
    entryUrl = params.getValue('sUrl')
    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = 'Kategorie.*?></li></ul>'
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

    pattern = '<h1>Filme</h1>.*?"></script></body>'
    isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    pattern = '''class=[^>](:?result-item|item movies|top-imdb-item).*?src=[^>]([^"']+).*?href=[^>]([^"']+)[^>]>([^<]+)'''
    if isMatch:
        isMatch, aResult = cParser().parse(sHtmlContainer, pattern)
    else:
        isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sDummy, sThumbnail, sUrl, sName in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setThumbnail(sThumbnail.replace('https', 'http'))
        oGuiElement.setMediaType('movie')
        params.setParam('entryUrl', sUrl)
        params.setParam('sThumbnail', sThumbnail)
        oGui.addFolder(oGuiElement, params, False, total)
    if not sGui:
        isMatchNextPage, sNextUrl = cParser().parseSingleResult(sHtmlContent, '''class="current">\d+<.*?href=[^>]([^"']+)''')
        if isMatchNextPage:
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('movies')
        oGui.setEndOfDirectory()


def showHosters():
    hosters = []
    sUrl = ParameterHandler().getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    isMatch, aResult = cParser().parse(sHtmlContent, "data-type='([^']+).*?post='([^']+).*?nume='([^']+).*?class='title'>([^<]+).*?src='([^']+)")
    if isMatch:
        for sType, sPost, sNume, sName, sLang in aResult:
            oRequest = cRequestHandler(URL_MAIN + 'wp-admin/admin-ajax.php', ignoreErrors=True)
            oRequest.addParameters('action', 'doo_player_ajax')
            oRequest.addParameters('post', sPost)
            oRequest.addParameters('nume', sNume)
            oRequest.addParameters('type', sType)
            sHtmlContent = oRequest.request()
            isMatch, sUrl = cParser.parseSingleResult(sHtmlContent, '(http[^"]+)')
            if isMatch:
                hoster = {'link': sUrl, 'name': cParser.urlparse(sUrl) + ' - ' + sName + Language(sLang)}
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


def Language(sLang):
    if 'de.png' in sLang:
        return ' (Deutsch) '
    elif 'en.png' in sLang:
        return ' (Englische) '
    else:
        return ' '
