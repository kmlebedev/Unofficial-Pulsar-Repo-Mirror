# coding: utf-8
import re
import tools
import json
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
    settings = tools.Settings()
    # define the browser
    browser = tools.Browser()
    #Begin Service
    if settings.service == 'true':
        options = {'Estrenos': '%s/categoria/1/estrenos/modo:listado/pag:',
                   'Peliculas': '%s/categoria/2/peliculas/modo:listado/pag:',
                   'Peliculas HDRip': '%s/categoria/13/peliculas-hdrip/modo:listado/pag:'}
        ret = int(Addon().getSetting('option'))
        if ret < len(options):
            url_search = options.values()[ret] % settings.url_address
            title = []
            magnet = []
            if settings.pages == 0: settings.pages = 1  # manual pages if the parameter is zero
            for page in range(1, settings.pages + 1):
                if settings.time_noti > 0: settings.dialog.notification(settings.name_provider,
                                                                        'Checking Online page %s...' % page,
                                                                        settings.icon, settings.time_noti)
                settings.log('[%s] %s%d' % (settings.name_provider_clean, url_search, page))
                if browser.open(url_search + str(page)):
                    data = browser.content
                    for (torrent, name) in re.findall(r'/torrent/(.*?)/(.*?)"', data):
                        info = tools.format_title(name)
                        title.append(info['title'].replace('-', ' '))
                        magnet.append(settings.url_address + '/get-torrent/' + torrent)  # create torrent to send P
                    if int(page) % 10 == 0: sleep(3000)  # to avoid too many connections
                else:
                    settings.log('[%s] >>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
                    settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
                    break
            if len(title) > 0:
                tools.integration(filename=title, magnet=magnet, type_list='MOVIE', folder=settings.movie_folder,
                                  name_provider=settings.name_provider, silence=True)
    del settings
    del browser


if Addon().getSetting('service') == 'true':
    persistent = Addon().getSetting('persistent')
    name_provider = re.sub('.COLOR (.*?)]', '', Addon().getAddonInfo('name').replace('[/COLOR]', ''))
    every = 28800  # seconds
    previous_time = time()
    log("[%s]Update Service starting..." % name_provider)
    update_service()
    while (not abortRequested) and persistent == 'true':
        if time() >= previous_time + every:  # verification
            previous_time = time()
            update_service()
            log('[%s] Update List at %s' % (name_provider, asctime(localtime(previous_time))))
            log('[%s] Next Update in %s' % (name_provider, strftime("%H:%M:%S", gmtime(every))))
            update_service()
        sleep(500)
