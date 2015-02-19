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
        size = re.findall(r'o</strong> .(.*?). &nbsp',data) # find all sizes
        cont = 0
        for cm, torrent in  enumerate(re.findall(r'/descargar/(.*?)"', data)):
            sname = re.search("_(.*?).html",torrent)
            if sname is None:
                name = torrent
            else:
                name = sname.group(1).replace('-',' ').title()
            torrent = settings.url + '/torrent/' + torrent  # create torrent to send Pulsar
            if filters.verify(name, size[cm] + ' MB'):
                    yield {"name": size[cm] + ' MB - ' + name.title() + ' - ' + settings.name_provider, "uri": torrent}  # return le torrent
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
    query = provider.quote_plus(query)
    url_search = "%s/newtemp/include/ajax/ajax.search.php?search=%s" % (settings.url,query.replace(' ','%20'))  # change in each provider
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
    return []

# This registers your module for use
provider.register(search, search_movie, search_episode)