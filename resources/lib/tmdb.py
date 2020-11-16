# -*- coding: utf-8 -*-
import json, re
from requestHandler import cRequestHandler
from resources.lib.config import cConfig
try:
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote_plus


class cTMDB:
    TMDB_GENRES = {12: 'Abenteuer', 14: 'Fantasy', 16: 'Animation', 18: 'Drama', 27: 'Horror', 28: 'Action', 35: 'Komödie', 36: 'Historie', 37: 'Western', 53: 'Thriller', 80: 'Krimi', 99: 'Dokumentarfilm', 878: 'Science Fiction', 9648: 'Mystery', 10402: 'Musik', 10749: 'Liebesfilm', 10751: 'Familie', 10752: 'Kriegsfilm', 10759: 'Action & Adventure', 10762: 'Kids', 10763: 'News', 10764: 'Reality', 10765: 'Sci-Fi & Fantasy', 10766: 'Soap', 10767: 'Talk', 10768: 'War & Politics', 10770: 'TV-Film'}
    URL = 'https://api.themoviedb.org/3/'
    URL_TRAILER = 'plugin://plugin.video.youtube/play/?video_id=%s'

    def __init__(self, api_key='', lang='de'):
        self.api_key = '86dd18b04874d9c94afadde7993d94e3'
        self.lang = lang
        self.poster = 'https://image.tmdb.org/t/p/%s' % cConfig().getSetting('poster_tmdb')
        self.fanart = 'https://image.tmdb.org/t/p/%s' % cConfig().getSetting('backdrop_tmdb')

    def get_idbyname(self, name, year='', mediaType='movie', page=1):
        if year:
            term = quote_plus(name) + '&year=' + year
        else:
            term = quote_plus(name)
        meta = self._call('search/' + str(mediaType), 'query=' + term + '&page=' + str(page))

        if 'errors' not in meta and 'status_code' not in meta:
            if 'total_results' in meta and meta['total_results'] == 0 and year:
                meta = self.search_movie_name(name, '')
            if 'total_results' in meta and meta['total_results'] != 0:
                tmdb_id = meta['results'][0]['id']
                return tmdb_id
        else:
            return False
        return False

    def search_movie_name(self, name, year='', page=1, advanced='false'):
        name = re.sub(" +", " ", name)
        if year:
            term = quote_plus(name) + '&year=' + year
        else:
            term = quote_plus(name)
        meta = self._call('search/movie', 'query=' + term + '&page=' + str(page))
        if 'errors' not in meta and 'status_code' not in meta:
            if 'total_results' in meta and meta['total_results'] == 0 and year:
                meta = self.search_movie_name(name, '')
            if 'total_results' in meta and meta['total_results'] != 0:
                movie = ''
                if meta['total_results'] == 1:
                    movie = meta['results'][0]
                else:
                    for searchMovie in meta['results']:
                        if searchMovie['genre_ids'] and 99 not in searchMovie['genre_ids']:
                            if searchMovie['title'].lower() == name.lower():
                                movie = searchMovie
                                break
                    if not movie:
                        for searchMovie in meta['results']:
                            if searchMovie['genre_ids'] and 99 not in searchMovie['genre_ids']:
                                if year:
                                    if 'release_date' in searchMovie and searchMovie['release_date']:
                                        release_date = searchMovie['release_date']
                                        yy = release_date[:4]
                                        if int(year) - int(yy) > 1:
                                            continue
                                movie = searchMovie
                                break
                    if not movie:
                        movie = meta['results'][0]
                if advanced == 'true':
                    tmdb_id = movie['id']
                    meta = self.search_movie_id(tmdb_id)
                else:
                    meta = movie
        else:
            meta = {}
        return meta

    def search_collection_name(self, name):
        name = re.sub(" +", " ", name)
        term = quote_plus(name)
        meta = self._call('search/collection', 'query=' + term)
        if 'errors' not in meta and 'status_code' not in meta:
            if 'total_results' in meta and meta['total_results'] != 0:
                collection = ''
                if meta['total_results'] == 1:
                    collection = meta['results'][0]
                else:
                    for searchCollec in meta['results']:
                        cleanTitleTMDB = searchCollec['name'].lower()
                        cleanTitleSearch = name.lower()
                        if not cleanTitleSearch.endswith('saga'):
                            cleanTitleSearch += 'saga'
                        if cleanTitleTMDB == cleanTitleSearch:
                            collection = searchCollec
                            break
                        elif (cleanTitleSearch + 'saga') == cleanTitleTMDB:
                            collection = searchCollec
                            break
                    if not collection:
                        for searchCollec in meta['results']:
                            if 'animation' not in searchCollec['name']:
                                collection = searchCollec
                                break
                    if not collection:
                        collection = meta['results'][0]
                meta = collection
                tmdb_id = collection['id']
                meta['tmdb_id'] = tmdb_id
                meta = self.search_collection_id(tmdb_id)
        else:
            meta = {}
        return meta

    def search_tvshow_name(self, name, year='', page=1, genre='', advanced='false'):
        if year:
            term = quote_plus(name) + '&year=' + year
        else:
            term = quote_plus(name)
        meta = self._call('search/tv', 'query=' + term + '&page=' + str(page))
        if 'errors' not in meta and 'status_code' not in meta:
            if 'total_results' in meta and meta['total_results'] == 0 and year:
                meta = self.search_tvshow_name(name, '')
            if 'total_results' in meta and meta['total_results'] != 0:
                movie = ''
                if meta['total_results'] == 1:
                    movie = meta['results'][0]
                else:
                    for searchMovie in meta['results']:
                        if genre == '' or genre in searchMovie['genre_ids']:
                            movieName = searchMovie['name']
                            if movieName.lower() == name.lower():
                                movie = searchMovie
                                break
                    if not movie:
                        for searchMovie in meta['results']:
                            if genre and genre in searchMovie['genre_ids']:
                                if year:
                                    if 'release_date' in searchMovie and searchMovie['release_date']:
                                        release_date = searchMovie['release_date']
                                        yy = release_date[:4]
                                        if int(year) - int(yy) > 1:
                                            continue
                                movie = searchMovie
                                break
                    if not movie:
                        movie = meta['results'][0]
                tmdb_id = movie['id']
                meta = self.search_tvshow_id(tmdb_id)
        else:
            meta = {}
        return meta

    def search_person_name(self, name):
        name = re.sub(" +", " ", name)
        term = quote_plus(name)
        meta = self._call('search/person', 'query=' + term)
        if 'errors' not in meta and 'status_code' not in meta:
            if 'total_results' in meta and meta['total_results'] != 0:
                meta = meta['results'][0]
                person_id = meta['id']
                meta = self.search_person_id(person_id)
        else:
            meta = {}
        return meta

    def search_movie_id(self, movie_id, append_to_response='append_to_response=trailers,credits'):
        result = self._call('movie/' + str(movie_id), append_to_response)
        result['tmdb_id'] = movie_id
        return result

    def search_tvshow_id(self, show_id, append_to_response='append_to_response=external_ids,videos,credits'):
        result = self._call('tv/' + str(show_id), append_to_response)
        result['tmdb_id'] = show_id
        return result

    def search_collection_id(self, collection_id):
        result = self._call('collection/' + str(collection_id))
        result['tmdb_id'] = collection_id
        return result

    def search_person_id(self, person_id):
        result = self._call('person/' + str(person_id))
        result['tmdb_id'] = person_id
        return result

    def search_network_id(self, network_id):
        result = self._call('network/%s/images' % str(network_id))
        if 'status_code' not in result and 'logos' in result:
            network = result['logos'][0]
            vote = -1
            for logo in result['logos']:
                logoVote = float(logo['vote_average'])
                if logoVote > vote:
                    network = logo
                    vote = logoVote
            network['tmdb_id'] = network_id
            network.pop('vote_average')
            return network
        return {}

    def _format(self, meta, name):
        _meta = {}
        _meta['imdb_id'] = ''
        _meta['tmdb_id'] = ''
        _meta['tvdb_id'] = ''
        _meta['title'] = name
        _meta['media_type'] = ''
        _meta['rating'] = 0
        _meta['votes'] = 0
        _meta['duration'] = 0
        _meta['plot'] = ''
        _meta['mpaa'] = ''
        _meta['premiered'] = ''
        _meta['year'] = ''
        _meta['trailer'] = ''
        _meta['tagline'] = ''
        _meta['genre'] = ''
        _meta['studio'] = ''
        _meta['status'] = ''
        _meta['credits'] = ''
        _meta['cast'] = []
        _meta['director'] = ''
        _meta['writer'] = ''
        _meta['poster_path'] = ''
        _meta['cover_url'] = ''
        _meta['backdrop_path'] = ''
        _meta['backdrop_url'] = ''
        _meta['original_title'] = ''
        _meta['original_language'] = ''
        _meta['budget'] = ''
        _meta['revenue'] = ''
        _meta['episode'] = 0

        if 'title' in meta and meta['title']:
            _meta['title'] = meta['title']
        elif 'name' in meta and meta['name']:
            _meta['title'] = meta['name']
        if 'id' in meta:
            _meta['tmdb_id'] = meta['id']
        if 'budget' in meta and meta['budget']:
            _meta['budget'] = meta['budget']
        if 'revenue' in meta and meta['revenue']:
            _meta['revenue'] = meta['revenue']
        if 'original_title' in meta and meta['original_title']:
            _meta['original_title'] = meta['original_title']
        if 'original_language' in meta and meta['original_language']:
            _meta['original_language'] = meta['original_language']
        if 'tmdb_id' in meta:
            _meta['tmdb_id'] = meta['tmdb_id']
        if 'imdb_id' in meta:
            _meta['imdb_id'] = meta['imdb_id']
        elif 'external_ids' in meta:
            _meta['imdb_id'] = meta['external_ids']['imdb_id']
        if 'mpaa' in meta:
            _meta['mpaa'] = meta['mpaa']
        if 'media_type' in meta:
            _meta['media_type'] = meta['media_type']
        if 'release_date' in meta:
            _meta['premiered'] = meta['release_date']
        elif 'first_air_date' in meta:
            _meta['premiered'] = meta['first_air_date']
        elif 'premiered' in meta and meta['premiered']:
            _meta['premiered'] = meta['premiered']
        elif 's_premiered' in meta and meta['s_premiered']:
            _meta['premiered'] = meta['s_premiered']
        elif 'air_date' in meta and meta['air_date']:
            _meta['premiered'] = meta['air_date']
        if 'year' in meta:
            _meta['year'] = meta['year']
        elif 's_year' in meta:
            _meta['year'] = meta['s_year']
        else:
            try:
                if 'premiered' in _meta and _meta['premiered']:
                    _meta['year'] = int(_meta['premiered'][:4])
            except:
                pass
        if 'rating' in meta:
            _meta['rating'] = meta['rating']
        elif 'vote_average' in meta:
            _meta['rating'] = meta['vote_average']
        if 'votes' in meta:
            _meta['votes'] = meta['votes']
        elif 'vote_count' in meta:
            _meta['votes'] = meta['vote_count']
        try:
            duration = 0
            if 'runtime' in meta and meta['runtime']:
                duration = int(meta['runtime'])
            elif 'episode_run_time' in meta and meta['episode_run_time']:
                duration = int(meta['episode_run_time'][0])
            if duration < 300:
                duration *= 60
            _meta['duration'] = duration
        except:
            _meta['duration'] = 0
        if 'overview' in meta and meta['overview']:
            _meta['plot'] = meta['overview']
        elif 'parts' in meta:
            _meta['plot'] = meta['parts'][0]['overview']
        elif 'biography' in meta:
            _meta['plot'] = meta['biography']
        if 'studio' in meta:
            _meta['studio'] = meta['studio']
        elif 'production_companies' in meta:
            _meta['studio'] = ''
            for studio in meta['production_companies']:
                if _meta['studio'] == '':
                    _meta['studio'] += studio['name']
                else:
                    _meta['studio'] += ' / ' + studio['name']
        if 'genre' in meta:
            listeGenre = meta['genre']
            if '{' in listeGenre:
                meta['genres'] = eval(listeGenre)
            else:
                _meta['genre'] = listeGenre
        if 'genres' in meta:
            for genre in meta['genres']:
                if _meta['genre'] == '':
                    _meta['genre'] += genre['name']
                else:
                    _meta['genre'] += ' / ' + genre['name']
        elif 'genre_ids' in meta:
            genres = self.getGenresFromIDs(meta['genre_ids'])
            _meta['genre'] = ''
            for genre in genres:
                if _meta['genre'] == '':
                    _meta['genre'] += genre
                else:
                    _meta['genre'] += ' / ' + genre
            try:
                _meta['genre'] = unicode(_meta['genre'], 'utf-8')
            except:
                pass
        elif 'parts' in meta:
            genres = self.getGenresFromIDs(meta['parts'][0]['genre_ids'])
            _meta['genre'] = ''
            for genre in genres:
                if _meta['genre'] == '':
                    _meta['genre'] += genre
                else:
                    _meta['genre'] += ' / ' + genre
            try:
                _meta['genre'] = unicode(_meta['genre'], 'utf-8')
            except:
                pass
        trailer_id = ''
        if 'trailer' in meta and meta['trailer']:
            _meta['trailer'] = meta['trailer']
        elif 'trailers' in meta:
            try:
                trailers = meta['trailers']['youtube']
                for trailer in trailers:
                    if trailer['type'] == 'Trailer':
                        if 'VF' in trailer['name']:
                            trailer_id = trailer['source']
                            break
                if not trailer_id:
                    trailer_id = meta['trailers']['youtube'][0]['source']
                _meta['trailer'] = self.URL_TRAILER % trailer_id
            except:
                pass
        elif 'videos' in meta and meta['videos']:
            try:
                trailers = meta['videos']
                if len(trailers['results']) > 0:
                    for trailer in trailers['results']:
                        if trailer['type'] == 'Trailer' and trailer['site'] == 'YouTube':
                            trailer_id = trailer['key']
                            if 'de' in trailer['iso_639_1']:
                                trailer_id = trailer['key']
                                break
                    if not trailer_id:
                        trailer_id = meta['videos'][0]['key']
                    _meta['trailer'] = self.URL_TRAILER % trailer_id
            except:
                pass
        if 'backdrop_path' in meta and meta['backdrop_path']:
            _meta['backdrop_path'] = meta['backdrop_path']
            _meta['backdrop_url'] = self.fanart + str(_meta['backdrop_path'])
        elif 'parts' in meta:
            nbFilm = len(meta['parts'])
            _meta['backdrop_path'] = meta['parts'][nbFilm - 1]['backdrop_path']
            _meta['backdrop_url'] = self.fanart + str(_meta['backdrop_path'])
        if 'poster_path' in meta and meta['poster_path']:
            _meta['poster_path'] = meta['poster_path']
            _meta['cover_url'] = self.poster + str(_meta['poster_path'])
        elif 'parts' in meta:
            nbFilm = len(meta['parts'])
            _meta['poster_path'] = meta['parts'][nbFilm - 1]['poster_path']
            _meta['cover_url'] = self.fanart + str(_meta['poster_path'])
        elif 'profile_path' in meta:
            _meta['poster_path'] = meta['profile_path']
            _meta['cover_url'] = self.poster + str(_meta['poster_path'])
        elif 'file_path' in meta:
            _meta['poster_path'] = meta['file_path']
            _meta['cover_url'] = self.poster + str(_meta['poster_path'])
            _meta['backdrop_path'] = _meta['poster_path']
            _meta['backdrop_url'] = self.fanart + str(_meta['backdrop_path'])
        if 's_poster_path' in meta and meta['s_poster_path']:
            _meta['poster_path'] = meta['s_poster_path']
            _meta['cover_url'] = self.poster + str(meta['s_poster_path'])
        if 'tagline' in meta and meta['tagline']:
            _meta['tagline'] = meta['tagline']
        if 'status' in meta:
            _meta['status'] = meta['status']
        if 'writer' in meta and meta['writer']:
            _meta['writer'] = meta['writer']
        if 'director' in meta and meta['director']:
            _meta['director'] = meta['director']
        if 'credits' in meta and meta['credits']:
            strmeta = str(meta['credits'])
            listCredits = eval(strmeta)
            casts = listCredits['cast']
            crews = []
            if len(casts) > 0:
                licast = []
                if 'crew' in listCredits:
                    crews = listCredits['crew']
                if len(crews) > 0:
                    _meta['credits'] = "{'cast': " + str(casts) + ", 'crew': " + str(crews) + "}"
                    for cast in casts:
                        licast.append((cast['name'], cast['character'], self.poster + str(cast['profile_path']), str(cast['id'])))
                    _meta['cast'] = licast
                else:
                    _meta['credits'] = "{'cast': " + str(casts) + '}'
            if len(crews) > 0:
                for crew in crews:
                    if crew['job'] == 'Director':
                        _meta['director'] = crew['name']
                    elif crew['department'] == 'Writing':
                        if _meta['writer'] != '':
                            _meta['writer'] += ' / '
                        _meta['writer'] += '%s (%s)' % (crew['job'], crew['name'])
                    elif crew['department'] == 'Production' and 'Producer' in crew['job']:
                        if _meta['writer'] != '':
                            _meta['writer'] += ' / '
                        _meta['writer'] += '%s (%s)' % (crew['job'], crew['name'])
        return _meta

    def get_meta(self, media_type, name, imdb_id='', tmdb_id='', year='', season='', episode='', advanced='false'):
        name = re.sub(" +", " ", name)
        meta = {}
        if media_type == 'movie':
            if tmdb_id:
                meta = self.search_movie_id(tmdb_id)
            elif name:
                meta = self.search_movie_name(name, year, advanced=advanced)
        elif media_type == 'tvshow':
            if tmdb_id:
                meta = self.search_tvshow_id(tmdb_id)
            elif name:
                meta = self.search_tvshow_name(name, year, advanced=advanced)
        elif media_type == 'anime':
            if tmdb_id:
                meta = self.search_tvshow_id(tmdb_id)
            elif name:
                meta = self.search_tvshow_name(name, year, genre=16)
        elif media_type == 'collection':
            if tmdb_id:
                meta = self.search_collection_id(tmdb_id)
            elif name:
                meta = self.search_collection_name(name)
        elif media_type == 'person':
            if tmdb_id:
                meta = self.search_person_id(tmdb_id)
            elif name:
                meta = self.search_person_name(name)
        elif media_type == 'network':
            if tmdb_id:
                meta = self.search_network_id(tmdb_id)
        if meta and 'id' in meta:
            meta = self._format(meta, name)
        return meta

    def getUrl(self, url, page=1, term=''):
        try:
            if term:
                term = term + '&page=' + str(page)
            else:
                term = 'page=' + str(page)
            result = self._call(url, term)
        except:
            return False
        return result

    def _call(self, action, append_to_response=''):
        url = '%s%s?language=%s&api_key=%s' % (self.URL, action, self.lang, self.api_key)
        if append_to_response:
            url += '&%s' % append_to_response
        if 'person' in url:
            url = url.replace('&page=', '')
        oRequestHandler = cRequestHandler(url, ignoreErrors=True)
        name = oRequestHandler.request()
        data = json.loads(name)
        if 'status_code' in data and data['status_code'] == 34:
            return {}
        return data

    def getGenresFromIDs(self, genresID):
        sGenres = []
        for gid in genresID:
            genre = self.TMDB_GENRES.get(gid)
            if genre:
                sGenres.append(genre)
        return sGenres
