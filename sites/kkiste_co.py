# -*- coding: utf-8 -*-
from resources.lib import logger
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser

SITE_IDENTIFIER = 'kkiste_co'
SITE_NAME = 'KKiste.co'
SITE_ICON = 'kkiste_co.png'
URL_MAIN = 'https://kkiste.life/'

def load():
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_MAIN)
    cGui().addFolder(cGuiElement('Filme & Serien', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('Value', 'Genres')
    cGui().addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showGenre'), params)
    params.setParam('Value', 'Release Jahre')
    cGui().addFolder(cGuiElement('Release Jahre', SITE_IDENTIFIER, 'showGenre'), params)
    cGui().addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    cGui().setEndOfDirectory()

def showGenre():
    params = ParameterHandler()
    sHtmlContent = cRequestHandler(URL_MAIN).request()
    pattern = '>{0}<.*?</ul>'.format(params.getValue('Value'))
    isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, pattern)

    if isMatch:
        isMatch, aResult = cParser.parse(sHtmlContainer, 'href="([^"]+).*?>([^<]+)')
    if not isMatch:
        cGui().showInfo()
        return

    for sUrl, sName in aResult:
        if sUrl.startswith('/'):
            sUrl = URL_MAIN + sUrl
        params.setParam('sUrl', sUrl)
        cGui().addFolder(cGuiElement(sName, SITE_IDENTIFIER, 'showEntries'), params)
    cGui().setEndOfDirectory()

def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl: entryUrl = params.getValue('sUrl')
    oRequest = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False))
    if sSearchText:
        oRequest.addParameters('do', 'search')
        oRequest.addParameters('subaction', 'search')
        oRequest.addParameters('story', sSearchText)
        oRequest.setRequestType(1)
    sHtmlContent = oRequest.request()
    pattern = 'class="short">.*?href="([^"]+)">([^<]+).*?img src="([^"]+).*?desc">([^<]+).*?Jahr.*?([\d]+).*?s-red">([\d]+)'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)

    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    cf = cRequestHandler.createUrl(entryUrl, oRequest)
    total = len(aResult)
    for sUrl, sName, sThumbnail, sDesc, sYear, sDuration in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        isTvshow = True if 'staffel' in sUrl or 'serie' in sUrl else False
        sThumbnail =  URL_MAIN + sThumbnail + cf
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showEpisodes' if isTvshow else 'showHosters')
        oGuiElement.setYear(sYear)
        oGuiElement.setDescription(sDesc)
        oGuiElement.addItemValue('duration', sDuration)
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setFanart(sThumbnail)
        params.setParam('entryUrl', sUrl)
        params.setParam('sThumbnail', sThumbnail)
        oGui.addFolder(oGuiElement, params, isTvshow, total)
    if not sGui:
        isMatchNextPage, sNextUrl = cParser().parseSingleResult(sHtmlContent, 'next"><a href="([^"]+)')
        if isMatchNextPage:
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('tvshows' if 'staffel' in sUrl else 'movies')
        oGui.setEndOfDirectory()

def showEpisodes():
    params = ParameterHandler()
    sTVShowTitle = params.getValue('TVShowTitle')
    entryUrl = params.getValue('entryUrl')
    sThumbnail = params.getValue('sThumbnail')
    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = '"><a href="#">([^<]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)

    if not isMatch:
        cGui().showInfo()
        return

    total = len(aResult)
    for sName in aResult:
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setTVShowTitle(sTVShowTitle)
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setFanart(sThumbnail)
        oGuiElement.setMediaType('episode')
        params.setParam('entryUrl', entryUrl)
        params.setParam('episode', sName)
        cGui().addFolder(oGuiElement, params, False, total)
    cGui().setView('episodes')
    cGui().setEndOfDirectory()

def showHosters():
    hosters = []
    sUrl = ParameterHandler().getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    if ParameterHandler().exist('episode'):
        episode = ParameterHandler().getValue('episode')
        pattern = '>{0}<.*?</ul></li>'.format(episode)
        isMatch, sHtmlContent = cParser.parseSingleResult(sHtmlContent, pattern)
    isMatch, aResult = cParser().parse(sHtmlContent, 'link="([^"]+)')
    if isMatch:
        for sUrl in aResult:
            if not 'vod' in sUrl and not 'youtube' in sUrl and not 'streamcherry' in sUrl:
                if sUrl.startswith('http'):
                    hoster = {'link': sUrl, 'name': cParser.urlparse(sUrl)}
                else:
                    hoster = {'link': 'https:' + sUrl, 'name': cParser.urlparse(sUrl)}
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
    showEntries(URL_MAIN, oGui, sSearchText)
