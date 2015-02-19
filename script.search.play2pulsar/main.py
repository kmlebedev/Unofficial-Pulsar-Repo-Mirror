# coding: utf-8
import re
from urllib import quote
from urllib import quote_plus
from urllib import unquote_plus
import commontools
from xbmcgui import Dialog
from xbmc import executebuiltin

# this read the settings
settings = commontools.Settings()
# define the browser
browser = commontools.Browser()
# create the filters
filters = commontools.Filtering()


# using function from Steeve to add Provider's name and search torrent
def torrentz(query):
    query = quote_plus(query.rstrip())
    url_search = settings.torrentz % query
    print(url_search)
    if browser.open(url_search):
        data = browser.content
        try:
            filters.information()  # print filters settings
            data = commontools.clean_html(data)
            data = data[data.find('peers'):].replace('<b>', '').replace('</b>', '').replace('class="pe">Pending',
                                                                                            'class="s">0 MB')  # short the result
            size = re.findall('class="s">(.*?)</span>', data)  # list the size
            seeds = re.findall('class="u">(.*?)</span>', data)  # list the seeds
            peers = re.findall('class="d">(.*?)</span>', data)  # list the seeds
            cont = 0
            results = []
            for cm, (infohash, name) in enumerate(re.findall('<dl><dt><a href="/(.*?)">(.*?)<', data)):
                torrent = 'magnet:?xt=urn:btih:%s' % infohash
                name = ' - ' + size[cm] + ' - ' + name.replace('-', ' ').title()
                if filters.verify(name, size[cm]):
                    results.append({"name": name, "uri": torrent, "info_hash": infohash,
                                    "size": commontools.size_int(size[cm]), "seeds": int(seeds[cm].replace(',', '')),
                                    "peers": int(peers[cm].replace(',', '')), "language": settings.language,
                                    "trackers": settings.trackers})  # return le torrent
                    cont += 1
                else:
                    print(filters.reason)
                if cont == settings.max_magnets:  # limit magnets
                    break
            print('>>>>>>' + str(cont) + ' torrents sent to Pulsar<<<<<<<')
            return results
        except:
            print('>>>>>>>ERROR parsing data<<<<<<<')
            settings.dialog.notification(settings.name_provider, '>>>>>>>>ERROR parsing data<<<<<<<<', settings.icon, 1000)
    else:
        print('>>>>>>>%s<<<<<<<' % browser.status)
        settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)


def kickass(query):
    query = quote(query.rstrip())
    url_search = settings.kickass % query
    print(url_search)
    if browser.open(url_search):
        data = browser.content
        try:
            filters.information()  # print filters settings
            data = commontools.clean_html(data)
            size = re.findall('class="nobr center">(.*?)B', data)  # list the size
            seeds = re.findall('green center">(.*?)<', data)  # list the seeds
            peers = re.findall('red lasttd center">(.*?)<', data)  # list the peers
            cont = 0
            results = []
            for cm, magnet in enumerate(re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)):
                info_magnet = commontools.Magnet(magnet)
                size[cm] = size[cm].replace('<span>', '')
                name = ' - ' + size[cm] + 'B' + ' - ' + info_magnet.name
                if filters.verify(name, size[cm]):
                    results.append({"name": name, "uri": magnet, "info_hash": info_magnet.hash,
                            "size": commontools.size_int(size[cm]), "seeds": int(seeds[cm]), "peers": int(peers[cm]),
                            "language": settings.language, "trackers": info_magnet.trackers + settings.trackers})  # return le torrent
                    cont += 1
                else:
                    print(filters.reason)
                if cont == settings.max_magnets:  # limit magnets
                    break
            print('>>>>>>' + str(cont) + ' torrents sent to Pulsar<<<<<<<')
            return results
        except:
            print('>>>>>>>ERROR parsing data<<<<<<<')
            settings.dialog.notification(settings.name_provider, '>>>>>>>>ERROR parsing data<<<<<<<<', settings.icon,
                                         1000)
    else:
        print('>>>>>>>%s<<<<<<<' % browser.status)
        settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)


def thepiratebay(query):
    query = query.rstrip().replace(' ', '%20')
    url_search = settings.thepiratebay % query
    print(url_search)
    if browser.open(url_search):
        data = browser.content
        try:
            filters.information()  # print filters settings
            data = commontools.clean_html(data)
            size = re.findall('Size (.*?)B', data) # list the size
            seedsPeers = re.findall('<td align="right">(.*?)</td>', data)  # list the size
            seeds = seedsPeers[0:][::2]
            peers = seedsPeers[1:][::2]
            cont = 0
            results = []
            for cm, magnet in enumerate(re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)):
                name = re.search('dn=(.*?)&',magnet).group(1) #find name in the magnet
                infohash = re.search(':btih:(.*?)&', magnet).group(1)  # find name in the magnet
                name = ' - ' + size[cm].replace('&nbsp;',' ') + 'B' + ' - ' + unquote_plus(name).replace('.', ' ').title()
                if filters.verify(name, size[cm].replace('&nbsp;',' ')):
                        results.append( {"name": name, "uri": magnet, "info_hash": infohash,
                               "size": commontools.size_int(size[cm].replace('&nbsp;',' ')), "seeds": int(seeds[cm]),
                               "peers": int(peers[cm]), "language": settings.language,
                               "trackers": settings.trackers
                        } ) # return le torrent
                        cont += 1
                else:
                    print(filters.reason)
                if cont == settings.max_magnets:  # limit magnets
                    break
            print('>>>>>>' + str(cont) + ' torrents sent to Pulsar<<<<<<<')
            return results
        except:
            print('>>>>>>>ERROR parsing data<<<<<<<')
            settings.dialog.notification(settings.name_provider, '>>>>>>>>ERROR parsing data<<<<<<<<', settings.icon, 1000)
    else:
        print('>>>>>>>%s<<<<<<<' % browser.status)
        settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)


def btjunkie(query):
    query = query.rstrip().replace(' ', '%20')
    url_search = settings.btjunkie % query
    print(url_search)
    if browser.open(url_search):
        data = browser.content
        try:
            filters.information()  # print filters settings
            data = commontools.clean_html(data).replace('<td data-href="magnet:?', '')
            lname = re.findall('<td data-href="/torrent/(.*?)/(.*?)"', data)  # list the size
            size = re.findall('<td class="size_td">(.*?)</td>', data)  # list the size
            seeds = re.findall('<td class="seed_td">(.*?)</td>', data)  # list the seeds
            peers = re.findall('<td class="leech_td">(.*?)</td>', data)  # list the seeds
            cont = 0
            results = []
            for cm, magnet in enumerate(re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)):
                info_magnet = commontools.Magnet(magnet)
                name = ' - ' + size[cm] + ' - ' + lname[cm][1].replace('-', ' ')   # find name in the torrent
                if filters.verify(name, size[cm]):
                    results.append({"name": name, "uri": magnet, "info_hash": info_magnet.hash,
                                    "size": commontools.size_int(size[cm]), "seeds": int(seeds[cm]), "peers": int(peers[cm]),
                                    "language": settings.language,
                                    "trackers": info_magnet.trackers + settings.trackers})  # return le torrent
                    cont += 1
                else:
                    print(filters.reason)
                if cont == settings.max_magnets:  # limit magnets
                    break
            print('>>>>>>' + str(cont) + ' torrents sent to Pulsar<<<<<<<')
            return results
        except:
            print('>>>>>>>ERROR parsing data<<<<<<<')
            settings.dialog.notification(settings.name_provider, '>>>>>>>>ERROR parsing data<<<<<<<<', settings.icon, 1000)
    else:
        print('>>>>>>>%s<<<<<<<' % browser.status)
        settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)


dialog = Dialog()
query = dialog.input('Query:')
type = dialog.select('Type:', ['All', 'Movies', 'TV Shows'])
if type == 1:
    filters.use_movie()
if type == 2:
    filters.use_TV()
selection = dialog.select('Engine:', ['Torrentz', 'The Pirate Bay', 'Btjunkie', 'Kickass', 'CANCEL'])
if query != '':
    results = []
    if selection == 0:
        results = torrentz(query)
    elif selection ==1:
        results = thepiratebay(query)
    elif selection ==2:
        results = btjunkie(query)
    elif selection ==3:
        results = kickass(query)
    # check if we get results
    if results == [] or results is None:
        dialog.ok('Search2Pulsar', 'No results')
    else:
        list = [result['name'] for result in results]
        seeds = ['S:%s ' % result['seeds'] for result in results]
        peers = ['P:%s ' % result['peers'] for result in results]
        magnet = [result['uri'] for result in results]
        lists = [ item1 + item2 + item3 for (item1, item2, item3) in zip(seeds, peers, list)]
        list_rep = dialog.select('Choose File', lists + ['CANCEL'])
        if list_rep < len(list):
            executebuiltin("PlayMedia(plugin://plugin.video.pulsar/play?uri=%s)" % quote_plus(magnet[list_rep]))

del dialog
del settings
del browser
del filters