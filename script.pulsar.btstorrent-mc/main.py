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
        data = data[data.find('FILENAME'):data.find('twitter')]
        size = re.findall('class="tsize">(.*?)<', data)
        cont = 0
        for cm, ntorrent in enumerate(re.findall('-tf(.*?).html">(.*?)<', data)):
            name = size[cm] + ' - ' + ntorrent[1] + ' - ' + settings.name_provider
            torrent = '%s/torrentdownload.php?id=%s' % (settings.url, ntorrent[0])
            if filters.verify(name, size[cm]):
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
    url_search = "%s/results.php?q=%s" % (settings.url,query)  # change in each provider
    provider.log.info(url_search)
    if browser.open(url_search):
        results = extract_magnets(browser.content)
    else:
        provider.log.error('>>>>>>>%s<<<<<<<' % browser.status)
        provider.notify(message=browser.status, header=None, time=5000, image=settings.icon)
        results = []
    return results


def search_movie(info):
    return []


def search_episode(info):
    info['title'] = common.exception(info['title'])
    filters.use_TV()
    query = common.clean(info['title']) + ' %02d' % info['absolute_number']  # define query
    results = []
    if info['absolute_number'] != 0:
        results = search(query)
    return results

# This registers your module for use
provider.register(search, search_movie, search_episode)