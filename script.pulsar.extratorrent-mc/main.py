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
if browser.login(settings.url + '/login/', {'login': username, 'password': password, 'action': 'login'}, "Incorrect Login or Password"):  # login
    provider.log.info('Logged In with the username and password')


# using function from Steeve to add Provider's name and search torrent
def extract_torrents(data):
    try:
        filters.information()  # print filters settings
        data = common.clean_html(data)
        value_search = 'total <b style="color: #ff0000;">0</b> torrents found on your search query' in data
        size = re.findall('</span></td><td>(.*?)B</td>', data) # list the size
        cont = 0
        for cm, torrent in  enumerate(re.findall(r'/torrent_download(.*?).torrent', data)):
            name = torrent[len(re.search("/*[0-9]*/",torrent).group()):]
            name = size[cm].replace('&nbsp;',' ') + 'B' + ' - ' + unquote_plus(name) + ' - ' + settings.name_provider #find name in the torrent
            torrent = settings.url + '/download' + torrent + '.torrent' # torrent to send to Pulsar
            if filters.verify(name, size[cm].replace('&nbsp;',' ')) and not value_search:
                yield {"name": name, "uri": torrent}  # return le torrent
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
    if settings.time_noti > 0: provider.notify(message="Searching: " + query.title() + '...', header=None, time=settings.time_noti, image=settings.icon)
    query = provider.quote_plus(query.rstrip())
    url_search = "%s/search/?search=%s&srt=seeds&order=desc" % (settings.url,query)  # change in each provider
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