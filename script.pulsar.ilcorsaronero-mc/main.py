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
    # try:
        filters.information()  # print filters settings
        data = common.clean_html(data).replace('n/a</td></TR>', "color='#0066CC'>0< ").replace('n/a', " color='#00CC00'>0")
        lname = re.findall('action="http://(.*?)/(.*?)/(.*?)/(.*?)"', data)  # list the name
        name = [item[3].replace('_', ' ') for item in lname]
        size = re.findall("color='#FF6600'>(.*?)<", data)  # list the size
        seeds = re.findall("color='#00CC00'>(.*?)<", data)  # list the seeds
        peers = re.findall("color='#0066CC'>(.*?)<", data)  # list the peers
        print data
        print seeds
        print peers
        cont = 0
        results = []
        for cm, infohash in enumerate(re.findall('value="(.*?)"', data)):
            torrent = 'http://torcache.net/torrent/%s.torrent' % infohash
            name[cm] = size[cm] + ' - ' + name[cm] + ' - ' + settings.name_provider #find name in the torrent
            if filters.verify(name[cm],size[cm]):
                    results.append({"name": name[cm], "uri":  torrent, "info_hash": infohash,
                           "size": common.size_int(size[cm]), "seeds": int(seeds[cm].replace(',', '')),
                           "peers": int(peers[cm].replace(',', '')), "language": "it",
                           "trackers": settings.trackers})  # return le torrent
                    cont+= 1
            else:
                provider.log.warning(filters.reason)
            if cont == settings.max_magnets:  # limit magnets
                break
        provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Pulsar<<<<<<<')
        return results
    # except:
    #     provider.log.error('>>>>>>>ERROR parsing data<<<<<<<')
    #     provider.notify(message='ERROR parsing data', header=None, time=5000, image=settings.icon)


def search(query):
    query = filters.type_filtering(query)  # check type filter and set-up filters.title
    query += ' ' + settings.extra
    if settings.time_noti > 0: provider.notify(message="Searching: " + query.title() + '...', header=None, time=settings.time_noti, image=settings.icon)
    query = provider.quote_plus(query.rstrip())
    url_search = "%s/argh.php?search=%s" % (settings.url,query)
    provider.log.info(url_search)
    if browser.open(url_search):
        results = extract_torrents(browser.content)
    else:
        provider.log.error('>>>>>>>%s<<<<<<<' % browser.status)
        provider.notify(message=browser.status, header=None, time=5000, image=settings.icon)
        results = []
    return results


def search_movie(info):
    query = common.translator(info['imdb_id'],"it")
    query += ' #MOVIE&FILTER'  #to use movie filters
    return search(query)


def search_episode(info):
    info['title'] = common.exception(info['title'])
    if info['absolute_number'] == 0:
        query = info['title'] + ' s%02de%02d'% (info['season'], info['episode'])  # define query
    else:
        query = info['title'] + ' %02d' % info['absolute_number']  # define query anime
    query += ' #TV&FILTER'  #to use TV filters
    return search(query)

# This registers your module for use
provider.register(search, search_movie, search_episode)