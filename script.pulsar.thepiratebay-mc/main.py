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
def extract_magnets(data):
    try:
        filters.information()  # print filters settings
        data = common.clean_html(data)
        size = re.findall('Size (.*?)B', data) # list the size
        seedsPeers = re.findall('<td align="right">(.*?)</td>', data)  # list the size
        seeds = seedsPeers[0:][::2]
        peers = seedsPeers[1:][::2]
        cont = 0
        results = []
        for cm, magnet in enumerate(re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)):
            name = re.search('dn=(.*?)&',magnet).group(1) #find name in the magnet
            infohash = re.search(':btih:(.*?)&', magnet).group(1)  # find name in the magnet
            name = size[cm].replace('&nbsp;',' ') + 'B' + ' - ' + unquote_plus(name).replace('.', ' ').title() + ' - ' + settings.name_provider
            if filters.verify(name, size[cm].replace('&nbsp;',' ')):
                    results.append( {"name": name, "uri": magnet, "info_hash": infohash,
                           "size": common.size_int(size[cm].replace('&nbsp;',' ')), "seeds": int(seeds[cm]),
                           "peers": int(peers[cm]), "language": settings.language,
                           "trackers": settings.trackers
                    } ) # return le torrent
                    cont += 1
            else:
                provider.log.warning(filters.reason)
            if cont == settings.max_magnets:  # limit magnets
                break
        provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Pulsar<<<<<<<')
        return results
    except:
        provider.log.error('>>>>>>>ERROR parsing data<<<<<<<')
        provider.notify(message='ERROR parsing data', header=None, time=5000, image=settings.icon)


def search(query):
    global filters
    filters.title = query  # to do filtering by name
    query += ' ' + settings.extra
    if settings.time_noti > 0: provider.notify(message="Searching: " + query.title() + '...', header=None, time=settings.time_noti, image=settings.icon)
    query = query.rstrip().replace(' ', '%20')
    url_search = "%s/search/%s/0/99/200" % (settings.url, query)  # change in each provider
    provider.log.info(url_search)
    if browser.open(url_search):
        results = extract_magnets(browser.content)
    else:
        provider.log.error('>>>>>>>%s<<<<<<<' % browser.status)
        provider.notify(message=browser.status, header=None, time=5000, image=settings.icon)
        results = []
    return results


def search_movie(info):
    filters.use_movie()
    query = (info['title'] + ' ' + str(info['year'])) if settings.language == 'en' else common.translator(info['imdb_id'], settings.language)
    return search(query)


def search_episode(info):
    info['title'] = common.exception(info['title'])
    filters.use_TV()
    if info['absolute_number'] == 0:
        query = info['title'] + ' s%02de%02d'% (info['season'], info['episode'])  # define query
    else:
        query = info['title'] + ' %02d' % info['absolute_number']  # define query anime
    return search(query)

# This registers your module for use
provider.register(search, search_movie, search_episode)