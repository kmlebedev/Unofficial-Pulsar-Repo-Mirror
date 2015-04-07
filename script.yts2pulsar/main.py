# coding: utf-8
import re
import tools
import json
from urllib import quote_plus
from time import sleep


# this read the settings
settings = tools.Settings()
# define the browser
browser = tools.Browser()
ret = settings.dialog.select('Option:', ['Manual Search', 'PreFixed List', '-SETTINGS', '-HELP','Exit'])
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
    settings.pages = settings.dialog.numeric(0, 'Number of Pages to download:')
    if settings.pages == '' or settings.pages == 0:
        settings.pages = "1"
    settings.pages = int(settings.pages)
    url_search = "%s/api/v2/list_movies.json?limit=50&quality=%s&sort_by=%s&order_by=desc" % (settings.url_address, qualities[quality], sorts[sort].lower().replace(' ', '_'))
    settings.log('[%s] %s' % (settings.name_provider_clean, url_search))
    title = []
    magnet = []
    for page in range(settings.pages):
        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online, Page %s...' % str(page + 1), settings.icon, settings.time_noti)
        if browser.open(url_search + '&page=' + str(page + 1)):
            data = json.loads(browser.content)
            for movie in data['data']['movies']:
                if movie.has_key('torrents'):
                    for torrent in movie['torrents']:
                        if torrent['quality'] in qualities[quality]:
                            title.append(movie['title_long'])
                            magnet.append('magnet:?xt=urn:btih:%s' % torrent['hash'])
        if page % 5 == 0:
            sleep(1)
    if len(title) > 0:
        tools.integration(filename=title, magnet=magnet, type_list='MOVIE', folder=settings.movie_folder, name_provider=settings.name_provider)
    else:
        settings.log('[%s] >>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
        settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
elif ret == 2:  # Settings
    settings.settings.openSettings()
    settings = tools.Settings()
elif ret == 3:  # Help
        settings.dialog.ok("Help", "Please, check this address to find the user's operation:\n[B]http://goo.gl/0b44BY[/B]")

del settings
del browser