# -*- coding: utf-8 -*-
from resources.lib import logger
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
try:
    from itertools import izip_longest as ziplist
except ImportError:
    from itertools import zip_longest as ziplist

SITE_IDENTIFIER = 'kinoger'
SITE_NAME = 'Kinoger'
SITE_ICON = 'kinoger.png'
URL_MAIN = 'https://kinoger.to'
URL_SERIE = URL_MAIN + '/stream/serie/'


def load():
    logger.info("Load %s" % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_MAIN)
    cGui().addFolder(cGuiElement('Filme & Serien', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_SERIE)
    cGui().addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showGenre'))
    cGui().addFolder(cGuiElement('Serien', SITE_IDENTIFIER, 'showEntries'), params)
    cGui().addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    cGui().setEndOfDirectory()


def showGenre():
    params = ParameterHandler()
    sHtmlContent = cRequestHandler(URL_MAIN).request()
    pattern = '<li[^>]class="links"><a href="([^"]+).*?/>([^<]+)</a>'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
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
        oRequest.addParameters('story', sSearchText)
        oRequest.addParameters('do', 'search')
        oRequest.addParameters('subaction', 'search')
        oRequest.addParameters('x', '0')
        oRequest.addParameters('y', '0')
        oRequest.addParameters('titleonly', '3')
        oRequest.addParameters('submit', 'submit')
    else:
        oRequest.addParameters('dlenewssortby', 'date')
        oRequest.addParameters('dledirection', 'desc')
        oRequest.addParameters('set_new_sort', 'dle_sort_main')
        oRequest.addParameters('set_direction_sort', 'dle_direction_main')
    oRequest.setRequestType(1)
    sHtmlContent = oRequest.request()
    pattern = 'class="title.*?href="([^"]+)">([^<]+).*?src="([^"]+)(.*?)</span>'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sUrl, sName, sThumbnail, sDummy in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        isTvshow = True if 'staffel' in sName.lower() else False
        isYear, sYear = cParser.parse(sName, "(.*?)\\((\\d*)\\)")
        for name, year in sYear:
            sName = name
            sYear = year
            break
        isDesc, sDesc = cParser.parseSingleResult(sDummy, '</b>([^"]+)</div>')
        isDuration, sDuration = cParser.parseSingleResult(sDummy, '[Laufzeit][Spielzeit]:[^>]([\d]+)')
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons' if isTvshow else 'showHosters')
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setFanart(sThumbnail)
        if isYear:
            oGuiElement.setYear(sYear)
        if isDesc:
            oGuiElement.setDescription(sDesc)
        if isDuration:
            oGuiElement.addItemValue('duration', sDuration)
        oGuiElement.setMediaType('tvshow' if isTvshow else 'movie')
        params.setParam('sThumbnail', sThumbnail)
        params.setParam('TVShowTitle', sName)
        params.setParam('entryUrl', sUrl)
        oGui.addFolder(oGuiElement, params, isTvshow, total)
    if not sGui:
        isMatchNextPage, sNextUrl = cParser().parseSingleResult(sHtmlContent, '<a[^>]href="([^"]+)">vorw')
        if isMatchNextPage:
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('tvshows' if 'staffel' in sName.lower() else 'movies')
        oGui.setEndOfDirectory()


def showSeasons():
    params = ParameterHandler()
    entryUrl = params.getValue('entryUrl')
    sThumbnail = params.getValue('sThumbnail')
    sTVShowTitle = params.getValue('TVShowTitle')
    sHtmlContent = cRequestHandler(entryUrl).request()
    L11 = []
    pattern = 'sst.show.*?</script>'
    isMatchsst, sstsContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatchsst:
        sstsContainer = sstsContainer.replace('[', '<').replace(']', '>')
        pattern = "<'([^>]+)"
        isMatchsst, L11 = cParser.parse(sstsContainer, pattern)
        if isMatchsst:
            total = len(L11)
    L22 = []
    pattern = 'ollhd.show.*?</script>'
    isMatchollhd, ollhdsContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatchollhd:
        ollhdsContainer = ollhdsContainer.replace('[', '<').replace(']', '>')
        pattern = "<'([^>]+)"
        isMatchollhd, L22 = cParser.parse(ollhdsContainer, pattern)
        if isMatchollhd:
            total = len(L22)
    L33 = []
    pattern = 'pw.show.*?</script>'
    isMatchpw, pwsContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatchpw:
        pwsContainer = pwsContainer.replace('[', '<').replace(']', '>')
        pattern = "<'([^>]+)"
        isMatchpw, L33 = cParser.parse(pwsContainer, pattern)
        if isMatchpw:
            total = len(L33)
    L44 = []
    pattern = 'go.show.*?</script>'
    isMatchgo, gosContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatchgo:
        gosContainer = gosContainer.replace('[', '<').replace(']', '>')
        pattern = "<'([^>]+)"
        isMatchgo, L44 = cParser.parse(gosContainer, pattern)
        if isMatchgo:
            total = len(L44)

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, '</b>([^"]+)<br><br>')
    for i in range(0, total):
        try:
            params.setParam('L11', L11[i])
        except:
            pass
        try:
            params.setParam('L22', L22[i])
        except:
            pass
        try:
            params.setParam('L33', L33[i])
        except:
            pass
        try:
            params.setParam('L44', L44[i])
        except:
            pass
        i = i + 1
        oGuiElement = cGuiElement("Staffel " + str(i), SITE_IDENTIFIER, 'showEpisodes')
        oGuiElement.setMediaType('season')
        oGuiElement.setTVShowTitle(sTVShowTitle)
        oGuiElement.setSeason(i)
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setFanart(sThumbnail)
        if isDesc:
            oGuiElement.setDescription(sDesc)
        params.setParam('sDesc', sDesc)
        params.setParam('sSeasonNr', i)
        cGui().addFolder(oGuiElement, params, True, total)
        cGui().setView('seasons')
    cGui().setEndOfDirectory()


def showEpisodes():
    params = ParameterHandler()
    sSeasonNr = params.getValue('sSeasonNr')
    sThumbnail = params.getValue('sThumbnail')
    sTVShowTitle = params.getValue('TVShowTitle')
    sDesc = params.getValue('sDesc')
    L11 = []
    if params.exist('L11'):
        L11 = params.getValue('L11')
        pattern = "(http[^']+)"
        isMatch1, L11 = cParser.parse(L11, pattern)
        if isMatch1:
            L11 = L11
    L22 = []
    if params.exist('L22'):
        L22 = params.getValue('L22')
        pattern = "(http[^']+)"
        isMatch2, L22 = cParser.parse(L22, pattern)
        if isMatch2:
            L22 = L22
    L33 = []
    if params.exist('L33'):
        L33 = params.getValue('L33')
        pattern = "(http[^']+)"
        isMatch3, L33 = cParser.parse(L33, pattern)
        if isMatch3:
            L33 = L33
    L44 = []
    if params.exist('L44'):
        L44 = params.getValue('L44')
        pattern = "(http[^']+)"
        isMatch4, L44 = cParser.parse(L44, pattern)
        if isMatch4:
            L44 = L44
    liste = ziplist(L11, L22, L33, L44)
    i = 0
    for sUrl in liste:
        i = i + 1
        oGuiElement = cGuiElement('Episode ' + str(i), SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setTVShowTitle(sTVShowTitle)
        oGuiElement.setSeason(sSeasonNr)
        oGuiElement.setEpisode(i)
        if sDesc:
            oGuiElement.setDescription(sDesc)
        if sThumbnail:
            oGuiElement.setThumbnail(sThumbnail)
            oGuiElement.setFanart(sThumbnail)
        params.setParam('sLinks', sUrl)
        cGui().addFolder(oGuiElement, params, False)
    cGui().setView('episodes')
    cGui().setEndOfDirectory()


def showHosters():
    hosters = []
    params = ParameterHandler()
    if params.exist('sLinks'):
        sUrl = params.getValue('sLinks')
        pattern = "(http[^']+)"
        isMatch, aResult = cParser().parse(sUrl, pattern)
    else:
        sUrl = params.getValue('entryUrl')
        sHtmlContent = cRequestHandler(sUrl).request()
        pattern = "show[^>]\\d,[^>][^>]'([^']+)"
        isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if isMatch:
        for sUrl in aResult:
            if 'protonvideo' in sUrl:
                oRequest = cRequestHandler(sUrl)
                oRequest.addHeaderEntry('Referer', URL_MAIN)
                sHtmlContent = oRequest.request()
                pattern = '(\d+p)[^>](http[^ ]+)'
                isMatch, aResult = cParser.parse(sHtmlContent, pattern)
                for sQualy, sUrl in aResult:
                    hoster = {'link': sUrl, 'name': sQualy + ' ProtonVideo'}
                    hosters.append(hoster)
            if 'sst' in sUrl:
                oRequest = cRequestHandler(sUrl)
                oRequest.addHeaderEntry('Referer', sUrl)
                sHtmlContent = oRequest.request()
                pattern = 'file:"(.*?)"'
                isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
                pattern = '(http[^",]+)'
                isMatch, aResult = cParser().parse(sContainer[0], pattern)
                for sUrl in aResult:
                    hoster = {'link': sUrl, 'name': Qualy(sUrl) + ' Fsst.Online'}
                    hosters.append(hoster)
            if 'kinoger.re' in sUrl:
                oRequest = cRequestHandler(sUrl.replace('/v/', '/api/source/'))
                oRequest.addHeaderEntry('Referer', sUrl)
                oRequest.addParameters('r', 'https://kinoger.com/')
                oRequest.addParameters('d', 'kinoger.re')
                sHtmlContent = oRequest.request()
                pattern = 'file":"([^"]+)","label":"([^"]+)'
                isMatch, aResult = cParser.parse(sHtmlContent, pattern)
                for sUrl, sQualy in aResult:
                    hoster = {'link': sUrl, 'name': sQualy + ' Kinoger.re'}
                hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    if 'sst' in sUrl:
        return [{'streamUrl': sUrl, 'resolved': True}]
    else:
        return [{'streamUrl': sUrl + '|Referer=' + sUrl + '&Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0', 'resolved': True}]


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    oGui.setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_MAIN, oGui, sSearchText)


def Qualy(sUrl):
    if '360p' in sUrl:
        return '360p'
    elif '480p' in sUrl:
        return '480p'
    elif '720p' in sUrl:
        return '720p'
    else:
        return '1080p'
