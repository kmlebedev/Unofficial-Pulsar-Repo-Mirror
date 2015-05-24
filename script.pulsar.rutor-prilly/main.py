# -*- coding: utf-8 -*-
from pulsar import provider
import re
import common
settings = common.Settings()
browser = common.Browser()
filters = common.Filtering()

torrent_pattern = re.compile(r'''<tr class=".*"><td>.*</td><td.*><a class="downgif" href="(?P<uri>.+)"><img src=".+" alt="D" /></a><a href="(?P<magnet>.+)"><img src=".+" alt="M" /></a>\s*<a href=".+">(?P<name>.+)?\s</a></td>\s*(<td align="right">.+<img.*></td>)?\s*<td align="right">(?P<size>.+)B</td><td align="center"><span class="green"><img src=".+" alt="S" />.*(?P<seeds>\d+)</span>&nbsp;<img src=".*" alt="L" /><span class="red">.*(?P<leech>\d+)</span></td></tr>''')
tag = re.compile(r'<.*?>')

def extract_torrents(data):
   # try:
        cont = 0
        results = []
        for el in torrent_pattern.finditer(data):
            d = el.groupdict()
            info = common.Magnet(d['magnet'])
            size = d['size'].replace('&nbsp;',' ')
            name = size + 'B' + ' - ' + d['name'] + ' - Rutor'
            provider.log.info('name: ' + name)
            if filters.verify(name.decode('utf-8'), size):
                results.append({"name": name, "uri": d['magnet'], "info_hash": info.hash,
                                     "size": common.size_int(size),
                                     "seeds": int(d['seeds']), "peers": int(d['leech']),
                                     "language": settings.language})  # return le torrent
            cont += 1
            if cont == settings.max_magnets:
                break
        provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Pulsar<<<<<<<')
        return results
   # except:
        provider.log.error('>>>>>>>ERROR parsing data<<<<<<<')
def search(query):
    query += ' ' + settings.extra  # add the extra information
    query = filters.type_filtering(query, '%20')  # check type filter and set-up filters.title
    url_search = "%s/search/0/0/000/4/%s" % (settings.url, query.replace(' ', '%20'))  # change in each provider
    provider.log.info(url_search)
    if browser.open(url_search):
        results = extract_torrents(browser.content)
    else:
        provider.log.error('>>>>>>>%s<<<<<<<' % browser.status)
        provider.notify(message=browser.status, header=None, time=5000, image=settings.icon)
        results = []
    return results

def search_movie(info):
    if settings.language == 'en':  # Title in english
        query = info['title'].encode('utf-8')  # convert from unicode
        if len(info['title']) == len(query):  # it is a english title
            query += ' ' + str(info['year'])  # Title + year
        else:
            query = common.IMDB_title(info['imdb_id'])  # Title + year
    else:  # Title en foreign language
        query = common.translator(info['imdb_id'],settings.language)  # Just title
    return search(query)

def search_episode(info):
    if info['absolute_number'] == 0:
        query = info['title'].encode('utf-8') + ' s%02de%02d' % (info['season'], info['episode'])  # define query
    else:
        query = info['title'].encode('utf-8') + ' %02d' % info['absolute_number']  # define query anime
    return search(query)

# This registers your module for use
provider.register(search, search_movie, search_episode)

del settings
del browser
del filters
