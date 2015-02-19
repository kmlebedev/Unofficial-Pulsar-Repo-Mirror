from pulsar import provider
import re
import common

# this read the settings
settings = common.Settings()
# create the filters
filters = common.Filtering()

values3 = {'ALL': 0, 'HDTV': 1, '480p': 1, 'DVD': 1, '720p': 2, '1080p': 3, '3D': 3, "1440p": 4, "2K": 5, "4K": 5}  # code_resolution steeve


def extract_magnets_json(data):
    results = []
    if not ("No movies found" in data):
        filters.information()
        items = provider.parse_json(data)
        for movie in items['MovieList']:
            resASCII =movie['Quality'].encode('utf-8')
            name = movie['Size'] + ' - ' + movie['MovieTitle'] + ' - ' + resASCII + ' - ' + settings.name_provider
            filters.title = name
            if filters.verify(name ,movie['Size']):
                results.append({'name': name, 'uri': movie['TorrentMagnetUrl'], 'info_hash': movie['TorrentHash'],
                                'resolution': values3[resASCII], 'Size': int(movie['SizeByte'])})
            else:
                provider.log.warning(filters.reason)
    return results


def search(query):
    return []


def search_movie(info):
    filters.use_movie()
    if settings.time_noti > 0: provider.notify(message='Searching: ' + info['title'].title() + '...', header=None,
                                               time=settings.time_noti, image=settings.icon)
    url_search = "%s/listimdb.json?imdb_id=%s" % (settings.url, info['imdb_id'])
    provider.log.info(url_search)
    response = provider.GET(url_search)
    return extract_magnets_json(response.data)


def search_episode(info):
    # just movies site
    return []

# This registers your module for use
provider.register(search, search_movie, search_episode)