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
    categories = {'Movies Popular': 'http://trakt.tv/movies/popular',
                  'Movies Trending': 'http://trakt.tv/movies/trending',
                  'TV Popular': 'http://trakt.tv/shows/popular',
                  'TV trending': 'http://trakt.tv/shows/trending',
                  'Watchlist': ''
                  }
    options = categories.keys()
    options.sort()
    rets = []
    movies_popular = settings.settings.getSetting('movies_popular')
    movies_trending = settings.settings.getSetting('movies_trending')
    TV_popular = settings.settings.getSetting('TV_popular')
    TV_trending = settings.settings.getSetting('TV_trending')
    watchlist = settings.settings.getSetting('watchlist')
    user = settings.settings.getSetting('user')
    if movies_popular == 'true':
        rets.append(0)
    if movies_trending == 'true':
        rets.append(1)
    if TV_popular == 'true':
        rets.append(2)
    if TV_trending == 'true':
        rets.append(3)
    if watchlist == 'true' and user is not '':
        rets.append(4)
    # start checking
    for ret in rets:
        if ret == 4:
            categories[options[ret]] = 'http://trakt.tv/users/%s/watchlist' % user.lower()
        url_search = categories[options[ret]]
        settings.log('[%s]%s' % (settings.name_provider_clean, url_search))
        if url_search is not '':
            listing = []
            ID = []  # IMDB_ID or thetvdb ID
            if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...',
                                                                    settings.icon, settings.time_noti)
            if browser.open(url_search):
                data = browser.content
                if options[ret] == 'Movies Popular' or options[ret] == 'Movies Trending':
                    data = data[data.find('/movies/popular'):]
                    items = re.findall('data-type="movie" data-url="/movies/(.*?)"', data)
                    listing = [item[:-4].replace('-', ' ') + ' (' + item[-4:] + ')' for item in items]
                    subscription.integration(listing=listing, ID=ID, type_list='MOVIE', folder=settings.movie_folder,
                                             name_provider=settings.name_provider, silence=True, message=options[ret])
                else:
                    if ret != 4:
                        data = data[data.find('/shows/popular'):]
                    items = re.findall('data-type="show" data-url="/shows/(.*?)"', data)
                    listing = [item.replace('-', ' ') for item in items]
                    subscription.integration(listing=listing, ID=ID, type_list='SHOW', folder=settings.show_folder,
                                             name_provider=settings.name_provider, silence=True, message=options[ret])
            else:
                settings.log('[%s]>>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
                settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
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
