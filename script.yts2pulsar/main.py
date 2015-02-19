# coding: utf-8
import re
import tools
import json
from urllib import quote_plus

# this read the settings
settings = tools.Settings(show=False)
# define the browser
browser = tools.Browser()
ret =settings.dialog.select('Option:', ['Manual Search', 'PreFixed List', 'Exit'])
if ret == 0:
    search = settings.dialog.input('Name Movie:')
    if search is not '':
        url_search = '%s/ajax/search?query=%s' % (settings.url_address, quote_plus(search))
        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...', settings.icon, settings.time_noti)
        settings.log('[%s] %s' % (settings.name_provider_clean, url_search))
        if browser.open(url_search):
            data = json.loads(browser.content)
            title = []
            url_search = []
            if 'Success' in data['message']:
                for item in data['data']:
                    title.append(item['title'])
                    url_search.append(item['url'].replace('\\', ''))
            rep = settings.dialog.select('Which Movie:', title + ['CANCEL'])
            if rep < len (title):
                browser.open(url_search[rep])
                data = browser.content
                qualities = re.findall('id="modal-quality-(.*?)"', data)
                magnet = re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)
                ret = settings.dialog.select('Which Quality:', qualities + ['CANCEL'])
                if ret < len(qualities):
                    tools.integration(filename=[title[rep]], magnet=[magnet[ret]], type_list='MOVIE', folder=settings.movie_folder, name_provider=settings.name_provider)
        else:
            settings.log('[%s] >>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
            settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
elif ret == 1:
    qualities = ['720p', '1080p', '3D']
    sorts = ['Year', 'Rating', 'Seeds', 'Downloaded Count', 'Like Count', 'Date Addded']
    quality = settings.dialog.select('Quality:', qualities)
    sort = settings.dialog.select('Sorting by:', sorts)
    number= settings.dialog.numeric(0, 'Number of Movies:', "50")
    url_search = "%s/api/v2/list_movies.json?limit=%s&quality=%s&sort_by=%s&order_by=desc" % (settings.url_address, number, qualities[quality], sorts[sort].lower().replace(' ', '_'))
    settings.log('[%s] %s' % (settings.name_provider_clean, url_search))
    title = []
    magnet = []
    if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...', settings.icon, settings.time_noti)
    if browser.open(url_search):
        data = json.loads(browser.content)
        for movie in data['data']['movies']:
            for torrent in movie['torrents']:
                if torrent['quality'] in qualities[quality]:
                    title.append(movie['title_long'])
                    magnet.append('magnet:?xt=urn:btih:%s' % torrent['hash'])
        tools.integration(filename=title, magnet=magnet, type_list='MOVIE', folder=settings.movie_folder, name_provider=settings.name_provider)
    else:
        settings.log('[%s] >>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
        settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
del settings
del browser