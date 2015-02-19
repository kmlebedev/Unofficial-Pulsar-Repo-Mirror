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
if not browser.login(settings.url + '/users/', {'username': username, 'password': password, 'action': 'login'}, "Wrong username or password"):  # login
    provider.notify(message=browser.status, header='ERROR!!', time=5000, image=settings.icon)
    provider.log.error('******** %s ********' % browser.status)


# using function from Steeve to add Provider's name and search torrent
def extract_magnets(data):
    try:
        filters.information()  # print filters settings
        data = common.clean_html(data)
        size = re.findall('class="tac">[0-9.]*[0-9]..B', data)  # list the size
        size = [s.replace('class="tac">','') for s in size]
        cont = 0
        for cm, magnet in enumerate(re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)):
            name = re.search('dn=(.*?)&tr=',magnet).group(1)  # find name in the magnet
            name = size[cm] + ' - ' + unquote_plus(name).replace('.',' ').title() + ' - ' + settings.name_provider
            if filters.verify(name,size[cm]):
                    yield {"name": name, "uri": magnet}  # return le torrent
                    cont+= 1
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
    if settings.time_noti > 0: provider.notify(message="Searching: " + query.title() + '...', header=None, time=settings.time_noti, image=settings.icon)
    query = provider.quote_plus(query.rstrip())
    url_search = "%s/torrents/search:%s/sort:seeders/dir:desc/" % (settings.url,query)
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
        query =  info['title'] + ' s%02de%02d'% (info['season'], info['episode'])  # define query
    else:
        query =  info['title'] + ' %02d' % info['absolute_number']  # define query anime
    return search(query)

# This registers your module for use
provider.register(search, search_movie, search_episode)