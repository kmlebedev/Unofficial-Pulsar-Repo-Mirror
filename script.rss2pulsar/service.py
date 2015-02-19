# coding: utf-8
import re
import rss
import shelve
from xbmc import translatePath
from time import time
from time import asctime
from time import localtime
from time import strftime
from time import gmtime
from xbmc import log
from xbmc import sleep
from xbmc import abortRequested
from xbmcaddon import Addon


def update_service():
    # this read the settings
    settings = rss.Settings()
    # define the browser
    browser = rss.Browser()
    #Begin Service
    if settings.service == 'true':
        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...', settings.icon, settings.time_noti)
        list_url_search = []
        path = translatePath('special://temp')
        database = shelve.open(path + 'RSS2PULSAR.db')
        rep = 0
        Dict_RSS = {}
        if database.has_key('dict'):
            Dict_RSS = database['dict']
        database.close()
        list_url_search = Dict_RSS.values()
        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...', settings.icon, settings.time_noti)
        # Begin reading
        for url_search in list_url_search:
            if url_search is not '':
                magnet_movie = []
                title_movie = []
                magnet_show = []
                title_show = []
                if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking %s...' % url_search, settings.icon, settings.time_noti)
                acum = 0
                if browser.open(url_search):
                    items = re.findall('<item>(.*?)</item>', browser.content, re.S)
                    for item in items:
                        s_title = re.findall('title>(.*?)<', item)
                        s_link = re.findall(r'magnet:\?[^\'"\s<>\[\]]+', item)
                        if len(s_link) == 0:
                            s_link = re.findall(r'http://(.*?)[.]torrent', item)
                        if len(s_link) != 0:
                            if 'magnet' not in s_link[0]:
                                s_link[0] = 'http://' + s_link[0].replace('&amp;', '&') + '.torrent'
                            if len(s_title) > 0:
                                if s_title[0] != '':
                                    info = rss.format_title(s_title[0])
                                    if 'MOVIE' in info['type']:
                                        title_movie.append(s_title[0])
                                        magnet_movie.append(s_link[0])
                                        acum += 1
                                    if 'SHOW' in info['type']:
                                        title_show.append(s_title[0])
                                        magnet_show.append(s_link[0])
                                        acum += 1
                    if acum == 0:
                        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'No Movies nor Shows!!', settings.icon, settings.time_noti)
                    if len(title_movie) > 0:
                        rss.integration(filename=title_movie, magnet=magnet_movie, type_list='MOVIE',
                                        folder=settings.movie_folder, silence=True, name_provider=settings.name_provider)
                    if len(title_show) > 0:
                        rss.integration(filename=title_show, magnet=magnet_show, type_list='EPISODES',
                                        folder=settings.show_folder, silence=True, name_provider=settings.name_provider)
                else:
                    settings.log('[%s]>>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
                    settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
    del settings
    del browser


if Addon().getSetting('service') == 'true':
    persistent = Addon().getSetting('persistent')
    name_provider = re.sub('.COLOR (.*?)]', '', Addon().getAddonInfo('name').replace('[/COLOR]', ''))
    every = 28800  # seconds
    previous_time = time()
    log("[%s] Persistent Update Service starting..." % name_provider)
    update_service()
    while (not abortRequested) and persistent == 'true':
        if time() >= previous_time + every:  # verification
            previous_time = time()
            update_service()
            log('[%s] Update List at %s' % (name_provider, asctime(localtime(previous_time))))
            log('[%s] Next Update in %s' % (name_provider, strftime("%H:%M:%S", gmtime(every))))
            update_service()
        sleep(500)
