# coding: utf-8
import re
import reader
from urllib import unquote_plus

# this read the settings
settings = reader.Settings()
browser = reader.Browser()
filters = reader.Filtering()


# using function from Steeve to add Provider's name and search torrent
def extract_magnets(data):
    try:
        filters.information()  # print filters settings
        data = reader.clean_html(data)
        size = re.findall('Size (.*?)B', data) # list the size
        seedsPeers = re.findall('<td align="right">(.*?)</td>', data)  # list the size
        seeds = seedsPeers[0:][::2]
        peers = seedsPeers[1:][::2]
        cont = 0
        results = []
        for cm, magnet in enumerate(re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)):
            name = re.search('dn=(.*?)&',magnet).group(1) #find name in the magnet
            infohash = re.search(':btih:(.*?)&', magnet).group(1)  # find name in the magnet
            name = unquote_plus(name).replace('.', ' ').title()
            if filters.verify(name, size[cm].replace('&nbsp;', ' ')):
                    results.append({"name": name, "uri": magnet, "info_hash": infohash,
                           "size": reader.size_int(size[cm].replace('&nbsp;',' ')), "seeds": int(seeds[cm]),
                           "peers": int(peers[cm]), "language": settings.language,
                           "trackers": settings.trackers
                    })  # return le torrent
                    cont += 1
            # this is common for every provider
            else:
                settings.log('[%s]%s' % (settings.name_provider_clean, filters.reason))
            if cont == settings.max_magnets:  # limit magnets
                break
        return results
    except:
        settings.log('[%s]%s' % (settings.name_provider_clean, '>>>>>>>ERROR parsing data<<<<<<<'))
        settings.dialog.notification(settings.name_provider, '>>>>>>>>ERROR parsing data<<<<<<<<', settings.icon, 1000)


def search(query='', type='', silence=False):
    results = []
    if type == 'MOVIE':
        folder = settings.movie_folder
    else:
        folder = settings.show_folder
    # start to search
    for page in range(settings.number_pages):
        url_search = query % (settings.url, page)
        settings.log('[%s]%s' % (settings.name_provider_clean, url_search))
        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Page %s...' % page,
                                                                settings.icon, settings.time_noti)
        if browser.open(url_search):
            results.extend(extract_magnets(browser.content))
        else:
            settings.log('[%s]%s' % (settings.name_provider_clean, '>>>>>>>%s<<<<<<<' % browser.status))
            settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
    if len(results) > 0:
        title = []
        magnet = []
        for item in results:
            info = reader.format_title(item['name'])
            if info['type'] == type:
                title.append(item['name'])
                magnet.append(item['uri'])
        reader.integration(filename=title, magnet=magnet, type_list=type, folder=folder, silence=silence,
                           name_provider=settings.name_provider)


# define the browser
rep = 0

list = ['Movies', 'HD - Movies', 'Movies DVDR', 'Movies 3D', 'TV shows', 'HD - TV shows']
while rep is not len(list):
    rep = settings.dialog.select('Choose an Option:', list + ['Exit'])
    if rep == 0:  # Movies
        query = '%s/browse/201/%s/7'
        search(query, 'MOVIE')
    if rep == 1:  # HD - Movies
        query = '%s/browse/207/%s/7'
        search(query, 'MOVIE')
    if rep == 2:  # Movies DVD
        query = '%s/browse/202/%s/7'
        search(query, 'MOVIE')
    if rep == 3:  # 3D
        query = '%s/browse/209/%s/7'
        search(query, 'MOVIE')
    if rep == 4:  # TV shows
        query = '%s/browse/205/%s/7'
        search(query, 'SHOW')
    if rep == 5:  # HD - TV shows
        query = '%s/browse/208/%s/7'
        search(query, 'SHOW')
del browser
del settings
del filters