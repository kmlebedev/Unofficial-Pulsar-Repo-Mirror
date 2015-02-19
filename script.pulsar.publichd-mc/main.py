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
browser.open(settings.url + '/auth/login')
_token = re.search('_token" type="hidden" value="(.*?)"', browser.content).group(1) # hidden variable required to log in
# open premium account
if not browser.login(settings.url + '/auth/login', {'username': username, 'password': password, '_token': _token}, "Forgot Password"):  # login
    provider.notify(message=browser.status, header='ERROR!!', time=5000, image=settings.icon)
    provider.log.error('******** %s ********' % browser.status)

# using function from Steeve to add Provider's name and search torrent
def extract_magnets(data):
    try:
        filters.information()  # print filters settings
        data = common.clean_html(data)
        rows = re.findall('fa fa-download(.*?)</td>(.*?)</td>(.*?)</td>(.*?)</td>(.*?)</td>(.*?)</td>(.*?)</td>(.*?)</tr>', data, re.S)
        size = [s[2].replace('\n                            <td>', '') for s in rows]
        seeds = [s[5].replace('\n                            <td>', '') for s in rows]
        peers = [s[6].replace('\n                            <td>', '') for s in rows]
        lname = re.findall('torrent-filename">(.*?)>(.*?)<', data, re.S)  # list the name
        cont = 0
        results = []
        for cm, magnet in enumerate(re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)):
            info_magnet = common.Magnet(magnet)
            name = size[cm] + 'B - ' + unquote_plus(lname[cm][1]).replace('.',' ').title() + ' - ' + settings.name_provider
            if filters.verify(name,size[cm]):
                    results.append({"name": name, "uri": magnet, "info_hash": info_magnet.hash, "size": common.size_int(size[cm]),
                           "language": 'en', "trackers": info_magnet.trackers, "seeds": int(seeds[cm]), "peers": int(peers[cm])
                           })  # return le torrent
                    cont+= 1
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
    query = re.sub('s..e...', '', query)
    url_search = "%s/torrents?search=%s&sort=seed" % (settings.url,query)
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
        query = info['title'] + ' s%02de%02d'% (info['season'], info['episode'])  # define query
    else:
        query = info['title'] + ' %02d' % info['absolute_number']  # define query anime
    query += ' #TV&FILTER'  #to use TV filters
    return search(query)

# This registers your module for use
provider.register(search, search_movie, search_episode)