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

# #premium account
# username = provider.ADDON.getSetting('username')  # username
# password = provider.ADDON.getSetting('password')  # passsword
# # open premium account
# if not browser.login(settings.url + '/auth/login', {'username': username, 'password': password, '_token': _token}, "Forgot Password"):  # login
#     provider.notify(message=browser.status, header='ERROR!!', time=5000, image=settings.icon)
#     provider.log.error('******** %s ********' % browser.status)


# using function from Steeve to add Provider's name and search torrent
def extract_torrents(data):
    try:
        filters.information()  # print filters settings
        data = common.clean_html(data)
        cont = 0
        for row in re.findall('<tr class="(.*?)</tr>', data,re.S):  # get each row from table
            if 'Fake file' not in row:
                size = re.search('<span class="icon magnet"></span></a></td><td>(.*?)iB<', row)
                if size is None:
                    size = "0 M"
                else:
                    size = size.group(1)
                print size
                name = size + 'B - ' + re.search('id="results_filename_(.*?)" title="(.*?)"', row).group(2) + ' - ' + settings.name_provider
                magnet = re.search(r'magnet:\?[^\'"\s<>\[\]]+', row).group()
                if filters.verify(name,size):
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
    filters.title = query[query.find('/', 1) + 1:]  # to do filtering by name
    query += ' ' + settings.extra
    if settings.time_noti > 0: provider.notify(message="Searching: " + query.title() + '...', header=None, time=settings.time_noti, image=settings.icon)
    url_search = "%s%s?o=s" % (settings.url,query.rstrip().replace(' ', '_'))
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
    query = (info['title'] + ' ' + str(info['year'])) if settings.language == 'en' else common.translator(
        info['imdb_id'], settings.language)
    query = '/movies/' + query
    return search(query)


def search_episode(info):
    info['title'] = common.exception(info['title'])
    filters.use_TV()
    if info['absolute_number'] == 0:
        query = info['title'] + ' s%02de%02d'% (info['season'], info['episode'])  # define query
    else:
        query = info['title'] + ' %02d' % info['absolute_number']  # define query anime
    query = '/tv/' + query
    return search(query)

# This registers your module for use
provider.register(search, search_movie, search_episode)