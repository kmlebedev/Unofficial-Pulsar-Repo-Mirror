# coding: utf-8
from pulsar import provider
from urllib import unquote_plus
import re
import common

# this read the settings
settings = common.Settings()
# define the browser
browser = common.Browser()
# create the filters
filters = common.Filtering()


# using function from Steeve to add Provider's name and search torrent
def extract_torrents(data):
    try:
        filters.information()  # print filters settings
        data = common.clean_html(data)
        cont = 0
        for cm, (torrent, name) in  enumerate(re.findall(r'/torrent/(.*?)/(.*?)"', data)):
            torrent = settings.url + '/get-torrent/' + torrent  # create torrent to send Pulsar
            if filters.verify(name, None):
                    yield {"name": name.title() + ' - ' + settings.name_provider, "uri": torrent}  # return le torrent
                    cont += 1
            else:
                provider.log.warning(filters.reason)
            if cont == settings.max_magnets:  # limit magnets
                break
        provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Pulsar<<<<<<<')
    except:
        provider.log.error('>>>>>>>ERROR parsing data<<<<<<<')
        provider.notify(message='ERROR parsing data', header=None, time=5000, image=settings.icon)


def search(query):
    global filters
    filters.title = query  # to do filtering by name
    query += ' ' + settings.extra
    if settings.time_noti > 0: provider.notify(message="Searching: " + query.encode('utf-8','ignore').title() + '...', header=None, time=settings.time_noti, image=settings.icon)
    query = provider.quote_plus(query.rstrip())
    url_search = "%s/busqueda/%s/modo:listado/orden:valoracion" % (settings.url,query)
    provider.log.info(url_search)
    if browser.open(url_search):
        results = extract_torrents(browser.content)
    else:
        provider.log.error('>>>>>>>%s<<<<<<<' % browser.status)
        provider.notify(message=browser.status, header=None, time=5000, image=settings.icon)
        results = []
    return results


def search_movie(info):
    filters.use_movie()
    query = common.translator(info['imdb_id'], 'es') #define query in spanish
    return search(query)


def search_episode(info):
    filters.use_TV()
    if info['absolute_number'] == 0:
        query =  info['title'] + ' s%02de%02d'% (info['season'], info['episode'])  # define query
    else:
        query =  info['title'] + ' %02d' % info['absolute_number']  # define query anime
    return search(query)

# This registers your module for use
provider.register(search, search_movie, search_episode)