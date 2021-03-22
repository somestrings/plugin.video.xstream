# -*- coding: utf-8 -*-
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.gui import cGui
from resources.lib import jsunpacker

SITE_IDENTIFIER = 'pureanime'
SITE_NAME = 'Pureanime'
SITE_ICON = 'pureanime.png'
SITE_SETTINGS = '<setting id="pureanime.user" type="text" label="30083" default="" /><setting id="pureanime.pass" type="text" option="hidden" label="30084" default="" />'
SITE_GLOBAL_SEARCH = False
URL_MAIN = 'https://pure-anime.net/'
URL_MOVIES = URL_MAIN + 'anime-movies/'
URL_SERIES = URL_MAIN + 'anime-serien/'
URL_TRENDING = URL_MAIN + 'trending/'
URL_SEARCH = URL_MAIN + '?s=%s'


def login():
    from resources.lib.config import cConfig
    username = cConfig().getSetting('pureanime.user')
    password = cConfig().getSetting('pureanime.pass')
    if not username == '' and not password == '':
        oRequest = cRequestHandler('https://pure-anime.net/wp-admin/admin-ajax.php', caching=False)
        oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
        oRequest.addHeaderEntry('Referer', URL_MAIN)
        oRequest.addParameters('log', username)
        oRequest.addParameters('pwd', password)
        oRequest.addParameters('rmb', 'forever')
        oRequest.addParameters('red', URL_MAIN)
        oRequest.addParameters('action', 'dooplay_login')
        oRequest.request()


def load():
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    login()
    params.setParam('sUrl', URL_SERIES)
    cGui().addFolder(cGuiElement('Anime Serien', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MOVIES)
    cGui().addFolder(cGuiElement('Anime Movies/OVAs', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_TRENDING)
    cGui().addFolder(cGuiElement('Anime Trends', SITE_IDENTIFIER, 'showEntries'), params)
    cGui().addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    cGui().setEndOfDirectory()


def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl: entryUrl = params.getValue('sUrl')
    oRequest = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False))
    if sSearchText:
        oRequest.addHeaderEntry('Referer', URL_MAIN)
    sHtmlContent = oRequest.request()
    pattern = 'a[^>]title="([^"]+).*?href="([^"]+)'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if not isMatch:
        pattern = 'alt="([^"]+).*? href="([^"]+)"><div class="see">'
        isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if not isMatch:
        pattern = 'result-item.*?alt="([^"]+).*?href="([^"]+)">'
        isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sName, sUrl in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        isTvshow = True if 'serie' in sUrl else False
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons' if isTvshow else 'showHosters')
        params.setParam('entryUrl', sUrl)
        oGui.addFolder(oGuiElement, params, isTvshow, total)
    if not sGui and not sSearchText:
        isMatchNextPage, sNextUrl = cParser().parseSingleResult(sHtmlContent, "<span class=[^>]current.*?href='([^']+)'[^>]class")
        if isMatchNextPage:
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('tvshows' if isTvshow else 'movies')
        oGui.setEndOfDirectory()


def showSeasons():
    params = ParameterHandler()
    entryUrl = params.getValue('entryUrl')
    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = "class='title'>Season[^>]([\d]+)"
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        cGui().showInfo()
        return

    isThumbnail, sThumbnail = cParser.parseSingleResult(sHtmlContent, 'poster.*?src="([^"]+)')
    total = len(aResult)
    for sSeasonNr in aResult:
        oGuiElement = cGuiElement('Staffel ' + sSeasonNr, SITE_IDENTIFIER, 'showEpisodes')
        if isThumbnail:
            oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setMediaType('season')
        oGuiElement.setSeason(sSeasonNr)
        params.setParam('sSeasonNr', int(sSeasonNr))
        cGui().addFolder(oGuiElement, params, True, total)
    cGui().setView('seasons')
    cGui().setEndOfDirectory()


def showEpisodes():
    params = ParameterHandler()
    entryUrl = params.getValue('entryUrl')
    sSeasonNr = params.getValue('sSeasonNr')
    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = "class='title'>Season[^>]%s.*?</li></ul>" % sSeasonNr
    isMatch, sContainer = cParser.parse(sHtmlContent, pattern)
    if isMatch:
        pattern = "numerando'>[^-]*-\s*(\d+)<.*?<a[^>]*href='([^']+)'>([^<]+)"
        isMatch, aResult = cParser.parse(sContainer[0], pattern)
    if not isMatch:
        cGui().showInfo()
        return

    isThumbnail, sThumbnail = cParser.parseSingleResult(sHtmlContent, 'poster.*?src="([^"]+)')
    total = len(aResult)
    for sEpisodeNr, sUrl, sName in aResult:
        oGuiElement = cGuiElement(sEpisodeNr + ' - ' + sName, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setSeason(sSeasonNr)
        oGuiElement.setEpisode(sEpisodeNr)
        if isThumbnail:
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
    isMatch, aResult = cParser().parse(sHtmlContent, "data-type='([^']+).*?post='([^']+).*?nume='([^']+).*?class='title'>([^<]+).*?src='([^']+)")
    if isMatch:
        for sType, sPost, sNume, sName, sLang in aResult:
            oRequest = cRequestHandler('https://pure-anime.net/wp-admin/admin-ajax.php', ignoreErrors=True)
            oRequest.addParameters('action', 'doo_player_ajax')
            oRequest.addParameters('post', sPost)
            oRequest.addParameters('nume', sNume)
            oRequest.addParameters('type', sType)
            sHtmlContent = oRequest.request()
            isMatch, sUrl = cParser.parseSingleResult(sHtmlContent, '(http[^"]+)')
            if isMatch:
                hoster = {'link': sUrl, 'name': sName + Language(sLang)}
                hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def Language(sLang):
    if 'gersub' in sLang:
        return ' (Deutsche Untertitel)'
    elif 'engsub' in sLang:
        return ' (Englische Untertitel)'
    elif 'espsub' in sLang:
        return ' (Spanische Untertitel)'
    elif 'trsub' in sLang:
        return ' (Türkische Untertitel)'
    elif 'de.png' in sLang:
        return ' (Deutsch)'
    elif 'en.png' in sLang:
        return ' (Englische)'
    else:
        return ''


def getHosterUrl(sUrl=False):
    if 'pure' in sUrl:
        sUrl = PureStream(sUrl)
        return [{'streamUrl': sUrl, 'resolved': True}]
    elif 'gproxy.stream' in sUrl:
        sUrl = gproxy_stream(sUrl)
        return [{'streamUrl': sUrl + '|Referer=https://gproxy.stream/', 'resolved': True}]
    else:
        return [{'streamUrl': sUrl, 'resolved': False}]


def PureStream(sUrl):
    from resources.lib import jsunpacker
    html = cRequestHandler(sUrl, caching=False, ignoreErrors=True).request()
    isMatch, sUrl2 = cParser.parse(html, "src:[^>]'([^']+)")
    if not isMatch:
        isMatch, packed = cParser.parseSingleResult(html, 'eval.*0,')
        if isMatch:
            unpack = jsunpacker.unpack(packed)
            isMatch, sUrl2 = cParser.parse(unpack, "file[^>]':[^>]'([^']+)")
    if isMatch:
        return 'https://' + cParser.urlparse(sUrl).lower() + sUrl2[0] + '|Referer=' + sUrl


def decrypt(key, enc_text):
    L = list(range(256))
    f = 0
    t = ''
    for i in range(256):
        f = (f + L[i] + ord(key[i % len(key)])) % 256
        s = L[i]
        L[i] = L[f]
        L[f] = s
    i = 0
    f = 0
    for k in range(len(enc_text)):
        i = (i + 1) % 256
        f = (f + L[i]) % 256
        s = L[i]
        L[i] = L[f]
        L[f] = s
        t += chr(ord(enc_text[k]) ^ L[(L[i] + L[f]) % 256])
    return t


def gproxy_stream(sUrl):
    html = cRequestHandler(sUrl, caching=False, ignoreErrors=True).request()
    Match, packed = cParser.parse(html, '(eval\s*\(function.*?)</script>')
    if Match:
        for p in packed:
            p = jsunpacker.unpack(p)
            Match2, url = cParser.parse(p, 'file":"([^"]+)')
    if Match2:
        return decrypt("\x63\x64\x34", cParser.urlDecode(url[0]))


def showSearch():
    sSearchText = cGui().showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    cGui().setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_SEARCH % cParser().quotePlus(sSearchText), oGui, sSearchText)
