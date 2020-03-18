# -*- coding: utf-8 -*-
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib import logger
from resources.lib.handler.ParameterHandler import ParameterHandler

SITE_IDENTIFIER = 'kindertube'
SITE_NAME = 'Kindertube'
SITE_ICON = 'kindertube.png'
URL_MAIN = 'http://www.kindertube.de/'
URL_ALL = URL_MAIN + 'alle-filme-und-serien.html'
URL_02 = URL_MAIN + 'kleinkind-filme-0-2-jahre.html'
URL_KLEINKINDER = URL_MAIN + 'serien-für-kleinkinder.html'
URL_LEHRFILME = URL_MAIN + 'lehrfilme-für-kinder.html'
URL_MUSIK = URL_MAIN + 'musik-für-kinder.html'
URL_SERIEN = URL_MAIN + 'alte-kinderserien.html'

def load():
    logger.info("Load %s" % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_ALL)
    cGui().addFolder(cGuiElement('Alle Filme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_02)
    cGui().addFolder(cGuiElement('0-2 jährigen', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_KLEINKINDER)
    cGui().addFolder(cGuiElement('Kleinkinder', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_LEHRFILME)
    cGui().addFolder(cGuiElement('Lehrfilme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MUSIK)
    cGui().addFolder(cGuiElement('Musik', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_SERIEN)
    cGui().addFolder(cGuiElement('Serien von früher', SITE_IDENTIFIER, 'showEntries'), params)
    cGui().setEndOfDirectory()

def showEntries(entryUrl=False, sGui=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl: entryUrl = params.getValue('sUrl')
    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = '<div[^>]*class="categories[^>]*onlyCategories">.*?<div[^>]*class="panel'
    isMatch, sContainer = cParser().parseSingleResult(sHtmlContent, pattern)

    if isMatch:
        pattern = '<a[^>]*href="([^"]+).*?<img[^>]*src="([^"]+).*?"title">([^<]+)'
        isMatch, aResult = cParser().parse(sContainer, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sUrl, sThumbnail, sName in aResult:
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showEpisodes')
        oGuiElement.setThumbnail(URL_MAIN + sThumbnail)
        oGuiElement.setFanart(URL_MAIN + sThumbnail)
        params.setParam('sEpisodes', sUrl)
        oGui.addFolder(oGuiElement, params, True, total)
    oGui.setEndOfDirectory()

def showEpisodes():
    params = ParameterHandler()
    sEpisodes = params.getValue('sEpisodes')
    sHtmlContent = cRequestHandler(sEpisodes).request()
    pattern = 'data-video="([^"]+).*?<img[^>]*src="([^"]+)".*?</div><span[^>]*class="title">([^<]+)'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)

    if not isMatch:
        if not sGui: cGui().showInfo()
        return

    total = len(aResult)
    for sUrl, sThumbnail, sName in aResult:
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'getHosterUrl')
        isMatch, Episodes = cParser.parseSingleResult(sEpisodes, 'de/([^"]+/)')
        oGuiElement.setThumbnail(URL_MAIN + Episodes + sThumbnail)
        oGuiElement.setFanart(URL_MAIN + Episodes + sThumbnail)
        params.setParam('url', 'https://www.youtube.com/watch?v=' + sUrl)
        cGui().addFolder(oGuiElement, params, False, total)
    cGui().setEndOfDirectory()

def getHosterUrl(sUrl=False):
    if 'youtube' in sUrl:
        import xbmc, xbmcgui
        if not xbmc.getCondVisibility("System.HasAddon(%s)" % "plugin.video.youtube"):
            xbmc.executebuiltin("InstallAddon(%s)" % "plugin.video.youtube")
    return [{'streamUrl': sUrl, 'resolved': False}]
