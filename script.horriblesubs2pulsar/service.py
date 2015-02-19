# coding: utf-8
import re
import tools
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
    path = translatePath('special://temp')
    database = shelve.open(path + 'HorribleSubs2PULSAR.db')
    # this read the settings
    settings = tools.Settings(movie=False)
    # define the browser
    browser = tools.Browser()
    # Begin Service
    if settings.service == 'true':
        rep = 0
        if database.has_key('list'):
            List_shows = database['list']
        else:
            List_shows = []
        List_name = []
        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...', settings.icon, settings.time_noti)
        if len(List_shows) > 0:
            quality = settings.settings.getSetting('quality')
            magnet_list = []
            file_list = []
            title_list = []
            url_search = '%s/lib/latest.php' % settings.url_address
            if browser.open(url_search):
                data = browser.content
                for (magnet, name_file) in zip(re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data), re.findall('HorribleSubs..(.*?)<', data)):
                    for show in List_shows:
                        if show in name_file and quality in name_file:
                            magnet_list.append(magnet)
                            title = name_file[:-4]
                            file_list.append(title)
                            title_list.append(show)
                tools.integration(filename=file_list, magnet=magnet_list, title=title_list, type_list='ANIME', silence=True,
                                        folder=settings.show_folder, name_provider=settings.name_provider)
            else:
                settings.log('[%s]>>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
                settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
        else:
            if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Empty List', settings.icon, settings.time_noti)
        database.close()
    del settings
    del browser


if Addon().getSetting('service') == 'true':
    persistent = Addon().getSetting('persistent')
    name_provider = re.sub('.COLOR (.*?)]', '', Addon().getAddonInfo('name').replace('[/COLOR]', ''))
    every = 28800  # seconds
    previous_time = time()
    log("[%s] Update Service starting..." % name_provider)
    update_service()
    while (not abortRequested) and persistent == 'true':
        if time() >= previous_time + every:  # verification
            previous_time = time()
            update_service()
            log('[%s] Update List at %s' % (name_provider, asctime(localtime(previous_time))))
            log('[%s] Next Update in %s' % (name_provider, strftime("%H:%M:%S", gmtime(every))))
            update_service()
        sleep(500)
