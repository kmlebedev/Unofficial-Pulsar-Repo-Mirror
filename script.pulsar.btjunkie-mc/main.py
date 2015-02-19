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


#premium account
username = provider.ADDON.getSetting('username')  # username
password = provider.ADDON.getSetting('password')  # passsword
# open premium account
if username != '':
    if browser.login(settings.url, {'username': username, 'pass': password, 'action': 'login'},
                     "Invalid username/password!"):  # login
        provider.log.info('Logged In with the username and password')

# using function from Steeve to add Provider's name and search torrent
def extract_torrents(data):
    try:
        filters.information()  # print filters settings
        data = common.clean_html(data).replace('<td data-href="magnet:?', '')
        lname = re.findall('<td data-href="/torrent/(.*?)/(.*?)"', data)  # list the size
        size = re.findall('<td class="size_td">(.*?)</td>', data)  # list the size
        seeds = re.findall('<td class="seed_td">(.*?)</td>', data)  # list the seeds
        peers = re.findall('<td class="leech_td">(.*?)</td>', data)  # list the seeds
        cont = 0
        results = []
        for cm, magnet in enumerate(re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)):
            info_magnet = common.Magnet(magnet)
            name = size[cm] + ' - ' + lname[cm][1].replace('-', ' ') + ' - ' + settings.name_provider #find name in the torrent
            if filters.verify(name,size[cm]):
                results.append({"name": name, "uri": magnet, "info_hash": info_magnet.hash,
                                "size": common.size_int(size[cm]), "seeds": int(seeds[cm]), "peers": int(peers[cm]),
                                "language": settings.language,
                                "trackers": info_magnet.trackers + settings.trackers})  # return le torrent
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
    query = provider.quote(query.rstrip())
    url_search = "%s/all/type-all/by-seed/desc/page1/%s" % (settings.url,query)
    provider.log.info(url_search)
    if browser.open(url_search):
        results = extract_torrents(browser.content)
    else:
        provider.log.error('>>>>>>>%s<<<<<<<' % browser.status)
        provider.notify(message=browser.status, header=None, time=5000, image=settings.icon)
        results = []
    return results


def search_movie(info):
    query = (info['title'] + ' ' + str(info['year'])) if settings.language == 'en' else common.translator(info['imdb_id'],settings.language)
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