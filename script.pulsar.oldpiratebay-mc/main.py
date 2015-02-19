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
        title = []
        lmagnet = []
        size = []
        seeds = []
        peers = []
        for row in re.findall('<tr(.*?)>(.*?)</tr>', data, re.S): # get each row in the table
            columns = re.findall('<td(.*?)>(.*?)</td>', row[1], re.S)  # get each column for the row
            if len(columns) > 0:
                size.append(columns[3][1])
                seeds.append(columns[4][1])
                peers.append(columns[5][1])
                aref = re.findall('<a(.*?)href="(.*?)"(.*?)>(.*?)<', columns[1][1]) # get the aref
                title.append(aref[0][3])
                lmagnet.append(aref[2][1])
        cont = 0
        results = []
        for cm, magnet in enumerate(lmagnet):
            info_magnet = common.Magnet(magnet)
            name =size[cm] + ' - ' + title[cm] + ' - ' + settings.name_provider
            if filters.verify(name, size[cm]):
                    results.append({"name": name, "uri": magnet, "info_hash": info_magnet.hash,
                           "size": common.size_int(size[cm]), "seeds": int(seeds[cm]), "peers": int(peers[cm]),
                           "language": settings.language, "trackers": info_magnet.trackers + settings.trackers})  #
                           # return le torrent
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
    query = filters.type_filtering(query)  # check type filter and set-up filters.title
    query += ' ' + settings.extra
    if settings.time_noti > 0: provider.notify(message="Searching: " + query.title() + '...', header=None, time=settings.time_noti, image=settings.icon)
    query = provider.quote_plus(query.rstrip())
    url_search = "%s/search.php?q=%s&Torrent_sort=seeders.desc" % (settings.url, query)  # change in each provider
    provider.log.info(url_search)
    if browser.open(url_search):
        results = extract_magnets(browser.content)
    else:
        provider.log.error('>>>>>>>%s<<<<<<<' % browser.status)
        provider.notify(message=browser.status, header=None, time=5000, image=settings.icon)
        results = []
    return results


def search_movie(info):
    query = (info['title'] + ' ' + str(info['year'])) if settings.language == 'en' else common.translator(info['imdb_id'], settings.language)
    query += ' #MOVIE&FILTER'  #to use movie filters
    return search(query)


def search_episode(info):
    info['title'] = common.exception(info['title'])
    if info['absolute_number'] == 0:
        query =  info['title'] + ' s%02de%02d'% (info['season'], info['episode'])  # define query
    else:
        query =  info['title'] + ' %02d' % info['absolute_number']  # define query anime
    query += ' #TV&FILTER'  #to use TV filters
    return search(query)

# This registers your module for use
provider.register(search, search_movie, search_episode)