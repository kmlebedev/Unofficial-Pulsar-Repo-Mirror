# coding: utf-8
import re
import subscription
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
    settings = subscription.Settings()
    # define the browser
    browser = subscription.Browser()
    watchlist = settings.settings.getSetting('watchlist')
    user = settings.settings.getSetting('user')
    # option
    if watchlist == 'true' and user is not '':  # watchlist
        url_search = "http://www.imdb.com/user/%s/watchlist" % user
        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Please wait...', settings.icon,
                                                                settings.time_noti)
        if browser.open(url_search):
            data = browser.content
            list = re.findall('/list/export.list_id=(.*?)&', data)
            if list != []:
                start = 1
                movie_listing = []
                show_listing = []
                movie_ID = []  # IMDB_ID or thetvdb ID
                TV_ID = []  # IMDB_ID or thetvdb ID
                while True:
                    url_search = "http://www.imdb.com/list/%s/?start=%d&view=detail&sort=listorian:asc" % (
                        list[0], start)
                    if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Please wait...',
                                                                            settings.icon, settings.time_noti)
                    settings.log('[%s] %s' % (settings.name_provider_clean, url_search))
                    if browser.open(url_search):
                        data = browser.content
                        lines = re.findall('<div class="info">(.*?)</div>', data, re.S)
                        if len(lines) > 0:
                            for line in re.findall('<div class="info">(.*?)</div>', data, re.S):
                                if 'This title is no longer available' not in line:  # prevent the error with not info
                                    items = re.search('/title/(.*?)/(.*?)>(.*?)<', line)
                                    year = re.search('<span class="year_type">(.*?)<', line)
                                    if 'TV Series' in year.group(1):
                                        show_listing.append(subscription.clear_name(items.group(3)))  # without year
                                        TV_ID.append(items.group(1))
                                    else:
                                        movie_listing.append(
                                            subscription.clear_name(items.group(3)) + ' ' + year.group(1))
                                        movie_ID.append(items.group(1))
                            start += 100
                        else:
                            break
                    else:
                        settings.log('[%s] %s' % (settings.name_provider_clean, browser.status))
                        settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
                        break
                if len(movie_listing) > 0:
                    subscription.integration(movie_listing, movie_ID, 'MOVIE', settings.movie_folder, silence=True,
                                             name_provider=settings.name_provider)
                if len(show_listing) > 0:
                    subscription.integration(show_listing, [], 'SHOW', settings.show_folder, silence=True,
                                             name_provider=settings.name_provider)
    imdblist = settings.settings.getSetting('imdblist')
    list = settings.settings.getSetting('list')
    # option
    if imdblist == 'true' and list is not '':  # list
        start = 1
        movie_listing = []
        show_listing = []
        movie_ID = []  # IMDB_ID or thetvdb ID
        TV_ID = []  # IMDB_ID or thetvdb ID
        while True:
            url_search = "http://www.imdb.com/list/%s/?start=%d&view=detail&sort=listorian:asc" % (list, start)
            if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Please wait...',
                                                                    settings.icon, settings.time_noti)
            settings.log('[%s] %s' % (settings.name_provider_clean, url_search))
            if browser.open(url_search):
                data = browser.content
                lines = re.findall('<div class="info">(.*?)</div>', data, re.S)
                if len(lines) > 0:
                    for line in re.findall('<div class="info">(.*?)</div>', data, re.S):
                        if 'This title is no longer available' not in line:  # prevent the error with not info
                            items = re.search('/title/(.*?)/(.*?)>(.*?)<', line)
                            year = re.search('<span class="year_type">(.*?)<', line)
                            if 'TV Series' in year.group(1):
                                show_listing.append(subscription.clear_name(items.group(3)))  # without year
                                TV_ID.append(items.group(1))
                            else:
                                movie_listing.append(subscription.clear_name(items.group(3)) + ' ' + year.group(1))
                                movie_ID.append(items.group(1))
                    start += 100
                else:
                    break
            else:
                settings.log('[%s] %s' % (settings.name_provider_clean, browser.status))
                settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
                break
        if len(movie_listing) > 0:
            subscription.integration(movie_listing, movie_ID, 'MOVIE', settings.movie_folder, silence=True,
                                     name_provider=settings.name_provider)
        if len(show_listing) > 0:
            subscription.integration(show_listing, [], 'SHOW', settings.show_folder, silence=True,
                                     name_provider=settings.name_provider)
    del settings
    del browser


if Addon().getSetting('service') == 'true':
    sleep(int(Addon().getSetting('delay_time')))  # get the delay to allow pulsar starts
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
