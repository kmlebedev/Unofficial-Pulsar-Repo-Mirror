# coding: utf-8
import re
import subscription


# this read the settings
settings = subscription.Settings()
# define the browser
browser = subscription.Browser()

categories = {'Movies Popular': 'http://trakt.tv/movies/popular',
              'Movies Trending': 'http://trakt.tv/movies/trending',
              'TV Popular': 'http://trakt.tv/shows/popular',
              'TV trending': 'http://trakt.tv/shows/trending',
              'Watchlist TVSHOW': ''
              }
options = categories.keys()
options.sort()
user = settings.settings.getSetting('user')
ret = settings.dialog.select('Choose a category:', options + ['Exit'])
if ret == 4:  # WatchList
    user = settings.dialog.input('username:', user)
    categories[options[ret]] = 'http://trakt.tv/users/%s/watchlist' % user.lower()
if ret != 5:  # Exit
    url_search = categories[options[ret]]
    settings.log('[%s]%s' % (settings.name_provider_clean, url_search))
    if url_search is not '':
        listing = []
        ID = []  # IMDB_ID or thetvdb ID
        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...', settings.icon, settings.time_noti)
        if browser.open(url_search):
            data = browser.content
            if options[ret] == 'Movies Popular' or options[ret] == 'Movies Trending':
                data = data[data.find('/movies/popular'):]
                items = re.findall('data-type="movie" data-url="/movies/(.*?)"',data)
                listing = [item[:-4].replace('-', ' ') + ' (' + item[-4:] + ')' for item in items]
                subscription.integration(listing=listing, ID=ID, type_list='MOVIE', folder=settings.movie_folder, name_provider=settings.name_provider)
            else:
                if ret != 4:
                    data = data[data.find('/shows/popular'):]
                items = re.findall('data-type="show" data-url="/shows/(.*?)"',data)
                listing = [item.replace('-', ' ') for item in items]
                subscription.integration(listing=listing, ID=ID, type_list='SHOW', folder=settings.show_folder, name_provider=settings.name_provider)
        else:
            settings.log('[%s]>>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
            settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
del settings
del browser