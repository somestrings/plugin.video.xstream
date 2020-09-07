# -*- coding: utf-8 -*-
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.gui import cGui
from resources.lib.config import cConfig
from resources.lib import jsunprotect
import re

SITE_IDENTIFIER = 'movie4k_to'
SITE_NAME = 'Movie4k'
SITE_ICON = 'movie4k.png'
SITE_SETTINGS = '<setting default="movie4k.to" enable="!eq(-2,false)" id="movie4k_to-domain" label="30051" type="labelenum" values="movie4k.to|movie4k.lol|movie.to|movie4k.me|movie4k.org|movie4k.pe|movie4k.am" />'

DOMAIN = cConfig().getSetting('movie4k_to-domain')
URL_MAIN = 'https://' + DOMAIN
URL_MOVIES = URL_MAIN + '/index.php'
URL_MOVIES_ALL = URL_MAIN + '/movies-all'
URL_MOVIES_GENRE = URL_MAIN + '/genres-movies.html'
URL_SERIES = URL_MAIN + '/tvshows_featured.php'
URL_SERIES_ALL = URL_MAIN + '/tvshows-all'
URL_SERIES_GENRE = URL_MAIN + '/genres-tvshows.html'
URL_XXX = URL_MAIN + '/xxx-updates.html'
URL_XXX_ALL = URL_MAIN + '/xxx-all'
URL_XXX_GENRE = URL_MAIN + '/genres-xxx.html'
URL_SEARCH = URL_MAIN + '/movies.php?list=search&search=%s'


def load():
    oGui = cGui()
#    __clearProtection()
    __createMainMenuItem(oGui, 'Filme', '', 'showMovieMenu')
    __createMainMenuItem(oGui, 'Serien', '', 'showSeriesMenu')
    if showAdult():
        __createMainMenuItem(oGui, 'XXX', '', 'showXXXMenu')
    __createMainMenuItem(oGui, 'Suche', '', 'showSearch')
    oGui.setEndOfDirectory()


def showMovieMenu():
    oGui = cGui()
    __createMainMenuItem(oGui, 'Kinofilme', URL_MOVIES, 'showFeaturedMovies')
    __createMainMenuItem(oGui, 'Alle Filme', URL_MOVIES_ALL, 'showCharacters')
    __createMainMenuItem(oGui, 'Genre', URL_MOVIES_GENRE, 'showGenre')
    oGui.setEndOfDirectory()


def showSeriesMenu():
    oGui = cGui()
    __createMainMenuItem(oGui, 'Featured', URL_SERIES, 'showFeaturedSeries')
    __createMainMenuItem(oGui, 'Alle Serien', URL_SERIES_ALL, 'showCharacters')
    __createMainMenuItem(oGui, 'Genre', URL_SERIES_GENRE, 'showGenre')
    oGui.setEndOfDirectory()


def showXXXMenu():
    oGui = cGui()
    __createMainMenuItem(oGui, 'Aktuelles', URL_XXX, 'parseMovieSimpleList')
    __createMainMenuItem(oGui, 'Alle XXXFilme', URL_XXX_ALL, 'showCharacters')
    __createMainMenuItem(oGui, 'Genre', URL_XXX_GENRE, 'showGenre')
    oGui.setEndOfDirectory()


def __getHtmlContent(sUrl=False, sSecurityValue=False, ignoreErrors=False):
    params = ParameterHandler()
    # Test if a url is available and set it
    if not sUrl:
        sUrl = params.getValue('siteUrl')
        if not sUrl:
            logger.info('no request url given')

    # Test is a security value is available
    if not sSecurityValue:
        sSecurityValue = params.getValue('securityCookie')
        if not sSecurityValue:
            sSecurityValue = ''
    # preferred language
    sPrefLang = __getPreferredLanguage()
    # adult Cookie
    if showAdult():
        adultCookie = 'xxx2=ok;'
    else:
        adultCookie = ''
    # Make the request
    oRequest = cRequestHandler(sUrl, ignoreErrors=ignoreErrors)
    oRequest.addHeaderEntry('Cookie', sPrefLang + sSecurityValue + adultCookie)
    return oRequest.request()


def __getPreferredLanguage():
    sLanguage = cConfig().getSetting('prefLanguage')
    if sLanguage == '0':
        sPrefLang = 'lang=de;onlylanguage=de;'
    elif sLanguage == '1':
        sPrefLang = 'lang=us;onlylanguage=en;'
    else:
        sPrefLang = ''
    return sPrefLang


def showAdult():
    if cConfig().getSetting('showAdult') == 'true':
        return True
    return False


def __clearProtection():
    oRequestHandler = cRequestHandler(URL_MAIN + '/index.php', False)
    oRequestHandler.removeNewLines(False)
    oRequestHandler.removeBreakLines(False)
    sHtmlContent = oRequestHandler.request()
    result = jsunprotect.jsunprotect(sHtmlContent)
    if not result:
        logger.info("Not protected or Deactivator not found")
        return ''
    else:
        logger.info(result)
        oRequestHandler = cRequestHandler(URL_MAIN + '?' + result, False)
        oRequestHandler.addHeaderEntry('Referer', URL_MAIN)
        oRequestHandler.addHeaderEntry('Host', 'www.' + DOMAIN)
        oRequestHandler.request()
        return ''


def showCharacters():
    oGui = cGui()
    params = ParameterHandler()
    baseUrl = params.getValue('sUrl')
    __createCharacters(oGui, '#', baseUrl)
    import string
    for letter in string.uppercase[:26]:
        __createCharacters(oGui, letter, baseUrl)
    oGui.setEndOfDirectory()


def __createCharacters(oGui, sCharacter, sBaseUrl):
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setFunction('parseMovieSimpleList')
    oGuiElement.setTitle(sCharacter)
    if sCharacter == '#':
        sUrl = sBaseUrl + '-1-1.html'
    else:
        sUrl = sBaseUrl + '-' + str(sCharacter) + '-1.html'
    params = ParameterHandler()
    params.setParam('sUrl', sUrl)
    oGui.addFolder(oGuiElement, params)


def showAllSeasons():
    params = ParameterHandler()
    sUrl = params.getValue('sUrl')
    __getAllSeasons(sUrl)


def __getAllSeasons(sUrl):
    oGui = cGui()
    oRequest = cRequestHandler(sUrl)
    sHtmlContent = oRequest.request()
    pattern = '<SELECT name="season".*?>(.*?)</SELECT>'
    aResult = cParser().parse(sHtmlContent, pattern)
    if not aResult[0]:
        return
    pattern = '<OPTION value="(\d+)".*?>([^<]+)</OPTION>'
    aResult = cParser().parse(sHtmlContent, pattern)
    if aResult[0]:
        total = len(aResult[1])
        for aEntry in aResult[1]:
            season = aEntry[0]
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName(SITE_IDENTIFIER)
            oGuiElement.setFunction('showAllEpisodes')
            sTitle = aEntry[1].strip()
            oGuiElement.setTitle(sTitle)
            oGuiElement.setSeason(season)
            oGuiElement.setMediaType('season')
            params = ParameterHandler()
            params.setParam('sUrl', sUrl)
            params.setParam('season', season)
            oGui.addFolder(oGuiElement, params, iTotal=total)
    oGui.setView('seasons')
    oGui.setEndOfDirectory()


def showAllEpisodes():
    oGui = cGui()
    params = ParameterHandler()
    sUrl = params.getValue('sUrl')
    sSeason = params.getValue('season')
    oRequest = cRequestHandler(sUrl)
    sHtmlContent = oRequest.request()
    pattern = '<FORM name="episodeform' + sSeason + '">(.*?)</FORM>'
    aResult = cParser().parse(sHtmlContent, pattern)
    sHtmlContent = aResult[1][0]
    pattern = '<SELECT name="episode".*?>(.*?)</SELECT>'
    aResult = cParser().parse(sHtmlContent, pattern)
    if not aResult[0]:
        return
    pattern = '<OPTION value="([^"]+)".*?>([^<]+)</OPTION>'
    aResult = cParser().parse(aResult[1][0], pattern)
    if not aResult[0]:
        return
    for aEntry in aResult[1]:
        sUrl = aEntry[0]
        if not sUrl.startswith('http'):
            sUrl = URL_MAIN + '/' + sUrl
        sMovieTitle = aEntry[1].strip()
        episodeNr = aEntry[1].strip().split(' ')[-1]
        oGuiElement = cGuiElement(sMovieTitle, SITE_IDENTIFIER, 'showHostersSeries')
        oGuiElement.setEpisode(episodeNr)
        if sSeason:
            oGuiElement.setSeason(sSeason)
        oGuiElement.setMediaType('episode')
        params.setParam('sUrl', sUrl)
        params.setParam('sMovieTitle', sMovieTitle)
        params.setParam('episode', episodeNr)
        oGui.addFolder(oGuiElement, params, bIsFolder=False, iTotal=len(aResult[1]))
    oGui.setView('episodes')
    oGui.setEndOfDirectory()


def __checkForNextPage(sHtmlContent, iCurrentPage):
    iNextPage = int(iCurrentPage) + 1
    pattern = '<a[^>]*href="([^"]+)">\s*%s\s*</a>' % str(iNextPage)
    isMatch, sNextUrl = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        return sNextUrl
    return False


def showGenre():
    oGui = cGui()
    params = ParameterHandler()
    if params.exist('sUrl'):
        sUrl = params.getValue('sUrl')
        sHtmlContent = cRequestHandler(sUrl).request()
        pattern = '<tr>\s*<td[^>]*id="tdmovies"[^>]*>\s*'
        pattern += '<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>\s*</td>\s*'
        pattern += '(?:<td[^>]*id="tdmovies"[^>]*>(\d+)</td>)?'
        isMatch, aResult = cParser.parse(sHtmlContent, pattern, ignoreCase=True)
        if not isMatch:
            oGui.showInfo()
            return

        for sUrl, sTitle, sCount in aResult:
            sUrl = sUrl.strip()
            if not sUrl.startswith('http'):
                sUrl = URL_MAIN + '/' + sUrl
            sTitle = '%s (%s)' % (sTitle, sCount)
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName(SITE_IDENTIFIER)
            oGuiElement.setFunction('parseMovieSimpleList')
            oGuiElement.setTitle(sTitle)
            params = ParameterHandler()
            params.setParam('sUrl', sUrl)
            oGui.addFolder(oGuiElement, params)
        oGui.setEndOfDirectory()


def parseMovieSimpleList():
    params = ParameterHandler()
    if params.exist('iPage'):
        iPage = params.getValue('iPage')
    else:
        iPage = 1
    if params.exist('sUrl'):
        sUrl = params.getValue('sUrl')
        logger.info(sUrl)
        if sUrl.find('tvshows-season-') != -1:
            pattern = '<TR[^>]*>\s*<TD[^>]*id="tdmovies"[^>]*>\s*<a href="([^"]+)">(.*?)</a>.*?<img[^>]*border=0[^>]*src="/img/([^"]+)"[^>]*>.*?</TR>'
            if params.exist('sLanguageToken'):
                sLanguageToken = params.getValue('sLanguageToken')
                oRequest = cRequestHandler(sUrl)
                sHtmlContent = oRequest.request()
                aResult = cParser().parse(sHtmlContent, pattern)
                if aResult[0]:
                    for aEntry in aResult[1]:
                        sUrl = str(aEntry[0]).strip()
                        if not (sUrl.startswith('http')):
                            sUrl = URL_MAIN + '/' + sUrl
                        if aEntry[2] == sLanguageToken:
                            break
                    oRequest = cRequestHandler(sUrl)
                    sHtmlContent = oRequest.request()
                    aResult = cParser().parse(sHtmlContent, pattern)
                    if aResult[0]:
                        for aEntry in aResult[1]:
                            sUrl = str(aEntry[0]).strip()
                            if not (sUrl.startswith('http')):
                                sUrl = URL_MAIN + '/' + sUrl
                            if aEntry[2] == sLanguageToken:
                                break
            else:
                oRequest = cRequestHandler(sUrl)
                sHtmlContent = oRequest.request()
                aResult = cParser().parse(sHtmlContent, pattern)
                if aResult[0]:
                    sUrl = str(aResult[1][0][0]).strip()
                    if not (sUrl.startswith('http')):
                        sUrl = URL_MAIN + sUrl
                    oRequest = cRequestHandler(sUrl)
                    sHtmlContent = oRequest.request()
                    aResult = cParser().parse(sHtmlContent, pattern)
                    if aResult[0]:
                        sUrl = str(aResult[1][0][0]).strip()
                        if not (sUrl.startswith('http')):
                            sUrl = URL_MAIN + '/' + sUrl
            __getAllSeasons(sUrl)
        else:
            __parseMovieSimpleList(sUrl, iPage, False)


def __parseMovieSimpleList(sUrl, iPage, sGui, sHtmlContent=False):
    oGui = sGui if sGui else cGui()
    if not sHtmlContent:
        sHtmlContent = __getHtmlContent(sUrl, ignoreErrors=(oGui is not False))
    pattern = '<TR[^>]*>\s*<TD[^>]*id="tdmovies"[^>]*>\s*<a href="([^"]+)">(.*?)</a>.*?<img[^>]*border=0[^>]*src="/img/([^"]+)"[^>]*>.*?</TR>'
    aResult = cParser().parse(sHtmlContent, pattern)
    pattern = "coverPreview([0-9]+)\"\)\.hover.*?<p id='coverPreview'><img src='(.*?)' alt='Image preview'"
    result = re.finditer(pattern, sHtmlContent, re.DOTALL)
    thumbs = dict()
    for set in result:
        id, thumb = set.groups()
        thumbs.update({id: thumb})
    if aResult[0]:
        total = len(aResult[1])
        for aEntry in aResult[1]:
            newUrl = aEntry[0].strip()
            if not (newUrl.startswith('http')):
                newUrl = URL_MAIN + '/' + newUrl
            sMovieTitle = aEntry[1]
            sMovieTitle = ' '.join(sMovieTitle.split())
            sMovieTitle = ' '.join(sMovieTitle.split())
            sLanguageToken = aEntry[2]
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName(SITE_IDENTIFIER)
            oGuiElement.setTitle(sMovieTitle)
            oGuiElement.setLanguage(__getLanguage(sLanguageToken.replace('.png', '')))
            params = ParameterHandler()
            params.setParam('sMovieTitle', sMovieTitle)
            params.setParam('sUrl', newUrl)
            type, id = getTypeAndID(newUrl)
            if type == 'tvshow':
                if sUrl.find('tvshows-') != -1:
                    params.setParam('sLanguageToken', sLanguageToken)
                    oGuiElement.setMediaType('tvshow')
                    oGuiElement.setFunction('parseMovieSimpleList')
                else:
                    oGuiElement.setFunction('showAllSeasons')
            elif type == 'movie':
                oGuiElement.setMediaType('movie')
                oGuiElement.setFunction('showHosters')
            else:
                params.setParam('sLanguageToken', sLanguageToken)
                oGuiElement.setFunction('parseMovieSimpleList')
            if id in thumbs:
                oGuiElement.setThumbnail(URL_MAIN + thumbs[id])
                oGuiElement.setFanart(URL_MAIN + thumbs[id])
            if type == 'movie':
                oGui.addFolder(oGuiElement, params, bIsFolder=False, iTotal=total)
            else:
                oGui.addFolder(oGuiElement, params, iTotal=total)
    if not sGui:
        sNextUrl = __checkForNextPage(sHtmlContent, iPage)
        if sNextUrl != False:
            if not (sNextUrl.startswith(URL_MAIN)):
                sNextUrl = URL_MAIN + '/' + sNextUrl
            params = ParameterHandler()
            params.setParam('sUrl', sNextUrl)
            params.setParam('iPage', int(iPage) + 1)
            oGui.addNextPage(SITE_IDENTIFIER, 'parseMovieSimpleList', params)
        oGui.setView('movies')
        oGui.setEndOfDirectory()
    return oGui


def getTypeAndID(url):
    #####################################################################
    # Examples:
    # http://www.movie4k.to/Die-Simpsons-online-serie-656673.html
    # http://www.movie4k.to/Die-Simpsons-Der-Film-online-film-783507.html
    # http://www.movie4k.to/The-Simpsons-watch-tvshow-660732.html
    # http://www.movie4k.to/The-Simpsons-Movie-watch-movie-693640.html
    #####################################################################
    aResult = cParser().parse(url, '([^-]+)-(\d+).html$')
    if aResult[0]:
        match = aResult[1][0]
        type = match[0]
        id = match[1]
        if type in ['serie', 'tvshow', 'tvshows']:
            return 'tvshow', id
        elif type in ['film', 'movie']:
            return 'movie', id
    return '', ''


def showFeaturedMovies():
    params = ParameterHandler()
    if params.exist('sUrl'):
        sUrl = params.getValue('sUrl')
        sHtmlContent = __getHtmlContent(sUrl=sUrl)
        pattern = ('<div style="float:left">\s*<a href="([^"]+)".{0,1}><img src="([^"]+)".*?alt="([^"]+)".*?'
                    '<img src="(.*?)".*?IMDB Rating: <a href="http://www.imdb.de/title/[0-9a-zA-z]+" '
                    'target="_blank">(.*?)</a>.*?smileys/([0-9])\.gif.*?class="info"><STRONG>.*?</STRONG><BR>(.*?)(?:<BR>|</div>).*?id="xline">')
        aResult = cParser().parse(sHtmlContent, pattern)
        if aResult[0]:
            oGui = cGui()
            total = len(aResult[1])
            for aEntry in aResult[1]:
                newUrl = aEntry[0]
                if not (newUrl.startswith('http')):
                    newUrl = URL_MAIN + '/' + newUrl
                if aEntry[1].startswith('/'):
                    sThumbnail = URL_MAIN + aEntry[1]
                else:
                    sThumbnail = + aEntry[1]
                sMovieTitle = aEntry[2].replace('kostenlos', '').replace('&amp;ouml;', 'ö')
                oGuiElement = cGuiElement()
                oGuiElement.setSiteName(SITE_IDENTIFIER)
                oGuiElement.setFunction('showHosters')
                oGuiElement.setMediaType('movie')
                fRating = float(aEntry[4])
                oGuiElement.setDescription(aEntry[6])
                oGuiElement.addItemValue('Rating', fRating)
                oGuiElement.setThumbnail(sThumbnail)
                oGuiElement.setFanart(sThumbnail)
                oGuiElement.setTitle(sMovieTitle)
                oGuiElement.setLanguage(__getLanguage(aEntry[3]))
                oGuiElement._sQuality = aEntry[5]
                params = ParameterHandler()
                params.setParam('sUrl', newUrl)
                params.setParam('sMovieTitle', sMovieTitle)
                oGui.addFolder(oGuiElement, params, bIsFolder=False, iTotal=total)
            oGui.setView('movies')
            oGui.setEndOfDirectory()


def showFeaturedSeries():
    params = ParameterHandler()
    if params.exist('sUrl'):
        sUrl = params.getValue('sUrl')
        oRequest = cRequestHandler(sUrl)
        sHtmlContent = oRequest.request()
        pattern = '<div id="maincontenttvshow">(.*?)<BR><BR>'
        aResult = cParser().parse(sHtmlContent, pattern)
        if aResult[0]:
            pattern = '<div style="float:left"><a href="([^"]+)"><img src="([^"]+)" border=0.*?title="([^"]+)"></a>.*?<img src="/img/(.*?).png"'
            sHtmlContent = aResult[1][0]
            aResult = cParser().parse(sHtmlContent, pattern)
            if aResult[0]:
                oGui = cGui()
                for aEntry in aResult[1]:
                    newUrl = str(aEntry[0]).strip()
                    if not (newUrl.startswith('http')):
                        newUrl = URL_MAIN + '/' + newUrl
                    if aEntry[1].startswith('/'):
                        sThumbnail = URL_MAIN + aEntry[1]
                    else:
                        sThumbnail = aEntry[1]
                    sMovieTitle = aEntry[2].strip().replace('\t', '')
                    oGuiElement = cGuiElement()
                    oGuiElement.setSiteName(SITE_IDENTIFIER)
                    oGuiElement.setFunction('showAllSeasons')
                    oGuiElement.setTitle(sMovieTitle)
                    oGuiElement.setThumbnail(sThumbnail)
                    oGuiElement.setFanart(sThumbnail)
                    oGuiElement.setLanguage(__getLanguage(aEntry[3]))
                    oGuiElement.setMediaType('tvshow')
                    params = ParameterHandler()
                    params.setParam('sUrl', newUrl)
                    oGui.addFolder(oGuiElement, params)
                oGui.setView('tvshows')
                oGui.setEndOfDirectory()


def showHostersSeries():
    params = ParameterHandler()
    if params.exist('sUrl') and params.exist('sMovieTitle'):
        sUrl = params.getValue('sUrl')
        sHtmlContent = cRequestHandler(sUrl).request()
        pattern = '<tr id="tablemoviesindex2".*?<a href="([^"]+)".*? width="16">([^<]+)<'
        aResult = cParser().parse(sHtmlContent.replace('\\', ''), pattern)
        if aResult[0]:
            hosters = []
            previousName = ''
            iMatches = 2
            for aEntry in aResult[1]:
                sHoster = aEntry[1].strip()
                hoster = {'name': sHoster, 'link': URL_MAIN + '/' + aEntry[0]}
                if hoster['name'] == previousName:
                    hoster['displayedName'] = hoster['name'] + ' (' + str(iMatches) + ')'
                    iMatches += 1
                else:
                    previousName = hoster['name']
                    iMatches = 2
                hosters.append(hoster)
            hosters.append('showHoster')
            return hosters


def showHosters():
    params = ParameterHandler()
    if params.exist('sUrl') and params.exist('sMovieTitle'):
        sUrl = params.getValue('sUrl')
        sHtmlContent = cRequestHandler(sUrl).request()
        pattern = '<tr id="tablemoviesindex2">.*?<a href="([^"]+)">([^<]+)<.*?alt="(.*?) .*?width="16">.*?</a>.*?smileys/([1-9]).gif"'
        aResult = cParser().parse(sHtmlContent.replace('\\', ''), pattern)
        hosters = []
        if aResult[0]:
            for aEntry in aResult[1]:
                sHoster = aEntry[2].strip()
                hoster = {'name': sHoster, 'link': URL_MAIN + '/' + aEntry[0],
                          'displayedName': aEntry[1] + ' - ' + sHoster + ' - Quality: ' + aEntry[3],
                          'quality': aEntry[3], 'date': aEntry[1].strip()}
                if sHoster == 'Stream4k':
                    hoster['resolveable'] = True
                hosters.append(hoster)
    pattern = '<SELECT name="hosterlist".*?>(.*?)</SELECT>'
    aResult = cParser().parse(sHtmlContent, pattern)
    if aResult[0]:
        pattern = '<OPTION value="([^"]+)".*?>([^<]+)</OPTION>'
        aResult = cParser().parse(aResult[1][0], pattern)
        if aResult[0]:
            for aEntry in aResult[1]:
                sUrl = aEntry[0]
                if not sUrl.startswith('http'):
                    sUrl = URL_MAIN + '/' + sUrl
                sHosterFull = aEntry[1].strip()
                hoster = {'name': sHosterFull.rsplit(' ', 1)[0], 'link': sUrl, 'displayedName': sHosterFull}
                hosters.append(hoster)

    if len(hosters) > 0:
        hosters.append('showHoster')
        return hosters
    if not aResult[0]:
        pattern = '<a target="_blank" href="([^"]+)'
        isMatch, aResult = cParser.parse(sHtmlContent, pattern)
        if isMatch:
            hosters = []
            for sUrl in aResult:
                hosters.append({'link': sUrl, 'name': sUrl})
            if hosters:
                return [{'streamUrl': sUrl, 'resolved': False}]
    return hosters


def showHoster(sUrl=False):
    params = ParameterHandler()
    if not sUrl:
        sUrl = params.getValue('url')
    sMovieTitle = params.getValue('sMovieTitle')
    # type,id = getTypeAndID(sUrl)
    sHtmlContent = cRequestHandler(sUrl).request()

    # if type == 'Film' or type=='Serie':
    pattern = '<a href="(movie.php\?id=(\d+)&part=(\d+))">'
    aResult = cParser().parse(sHtmlContent, pattern)
    results = []
    if aResult[0]:  # multipart stream
        for aEntry in aResult[1]:
            result = parseHosterDirect(sHtmlContent)  # , sHoster.lower(), sMovieTitle)
            result['title'] = sMovieTitle + ' Part ' + aEntry[2]
            results.append(result)
        return results
    else:
        result = parseHosterDirect(sHtmlContent)  # , sHoster.lower(), sMovieTitle)
        if type(result) is list:
            results.extend(result)
        else:
            results.append(result)
        return results


def __getMovieTitle(sHtmlContent):
    pattern = '<title>(.*?) online anschauen.*?</title>'
    aResult = cParser().parse(sHtmlContent, pattern)

    if aResult[0]:
        return str(aResult[1][0]).strip()
    else:
        aResult = cParser().parse(sHtmlContent, 'Watch (.*?) online.*?</title>')
        if aResult[0]:
            return str(aResult[1][0]).strip()
    return False


def parseHosterDirect(sHtmlContent):
    # Link oder Iframe suchen der den Hosternamen enthält
    pattern = 'id="maincontent5".*?(?:target="_blank" href|iframe[^<]+src|value)="([^"]+)".*?id="underplayer">'
    aResult = cParser().parse(sHtmlContent, pattern)
    if aResult[0]:
        sStreamUrl = aResult[1][0]

        # Stream4k
        if 'http' not in sStreamUrl:
            oRequest = cRequestHandler(URL_MAIN + '/' + sStreamUrl)
            oRequest.removeBreakLines(False)
            oRequest.removeNewLines(False)
            sHtml = oRequest.request()

            isMatch, aResult = cParser.parse(sHtml, '(eval\(function.*?)</script>')

            if isMatch:
                from resources.lib import jsunpacker
                import json

                unpacked = jsunpacker.unpack(aResult[0])
                isMatch, sJson = cParser.parseSingleResult(unpacked, '(\[{".*?}\])')

                if isMatch:
                    results = []
                    for entry in json.loads(sJson):
                        if 'file' not in entry or 'label' not in entry: continue
                        result = dict()
                        result['streamUrl'] = entry['file']
                        result['title'] = entry['label'].encode('utf-8')
                        result['resolved'] = True
                        results.append(result)
                    return results
        else:
            result = {'streamUrl': sStreamUrl, 'resolved': False}
            return result
    return False


def __getLanguage(sString):
    if 'us_ger_small' in sString:
        return 'de'
    return 'en'


def __createMainMenuItem(oGui, sTitle, sUrl, sFunction):
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setFunction(sFunction)
    oGuiElement.setTitle(sTitle)
    params = ParameterHandler()
    if sUrl != '':
        params.setParam('sUrl', sUrl)
    oGui.addFolder(oGuiElement, params)


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    oGui.setEndOfDirectory()


def _search(oGui, sSearchText):
    if not sSearchText: return
    __parseMovieSimpleList(URL_SEARCH % cParser().quotePlus(sSearchText), 1, oGui)
