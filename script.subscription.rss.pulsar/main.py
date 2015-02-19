# coding: utf-8
import re
import subscription
import shelve
import xbmc
from urllib import quote_plus
from urllib import unquote_plus

# this read the settings
settings = subscription.Settings()
browser = subscription.Browser()

# define the browser
list_url_search = []
path = xbmc.translatePath('special://temp')
database = shelve.open(path + 'SUBSCRIPTION-PULSAR-RSS.db')
rep = 0
Dict_RSS = {}
if database.has_key('dict'):
    Dict_RSS = database['dict']
while rep is not 5:
    rep = settings.dialog.select('Choose an Option:',
                                 ['Add a New RSS', 'Remove a RSS', 'Modify Saved RSS', 'View Saved RSS list',
                                  'Read RSS list and create .strm Files', 'Exit'])
    if rep == 0:  # Add a New RSS
        selection = settings.dialog.input('URL RSS:')
        name = ''
        while name is '':
            name = settings.dialog.input('Name to this RSS:').title()
        Dict_RSS[name] = selection
        database['dict'] = Dict_RSS
        database.sync()
    if rep == 1 and len(Dict_RSS.keys()) > 0:  # Remove a RSS
        List = [name + ": " + RSS for (name, RSS) in zip(Dict_RSS.keys(), Dict_RSS.values())]
        list_rep = settings.dialog.select('Choose RSS to Remove', List + ['CANCEL'])
        if list_rep < len (List):
            if settings.dialog.yesno('', 'Do you want Remove %s?' % List[list_rep]):
                del Dict_RSS[Dict_RSS.keys()[list_rep]]
                database['dict'] = Dict_RSS
                database.sync()
    if rep == 2:  # Modify RSS list
        List = [name + ": " + RSS for (name, RSS) in zip(Dict_RSS.keys(), Dict_RSS.values())]
        list_rep = settings.dialog.select('Shows', List + ['CANCEL'])
        if list_rep < len(List):
            name = Dict_RSS.keys()[list_rep]
            Dict_RSS[name] = settings.dialog.input('URL RSS:', Dict_RSS[name])
            database['dict'] = Dict_RSS
            database.sync()
    if rep == 3:  # View Saved RSS list
        List = [name + ": " + RSS for (name, RSS) in zip(Dict_RSS.keys(), Dict_RSS.values())]
        settings.dialog.select('Shows', List)
    if rep == 4:
        list_url_search = Dict_RSS.values()
        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...', settings.icon, settings.time_noti)
        # Begin reading
        for url_search in list_url_search:
            if url_search is not '':
                title_movie = []
                title_show = []
                if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking %s...' % url_search, settings.icon, settings.time_noti)
                acum = 0
                settings.log('[%s]%s' % (settings.name_provider_clean, url_search))
                if browser.open(url_search):
                    items = re.findall('<item>(.*?)</item>', browser.content, re.S)
                    for item in items:
                        s_title = re.findall('title>(.*?)<', item)
                        if s_title[0] != '':
                            info = subscription.format_title(s_title[0])
                            if 'MOVIE' in info['type']:
                                title_movie.append(info['title'])
                                acum += 1
                            if 'SHOW' in info['type']:
                                title_show.append(info['clean_title'])
                                acum += 1
                    if acum == 0:
                        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'No Movies nor Shows!!', settings.icon, settings.time_noti)
                    if len(title_movie) > 0:
                        subscription.integration(listing=title_movie, ID=[], type_list='MOVIE', folder=settings.movie_folder, name_provider=settings.name_provider)
                    if len(title_show) > 0:
                        subscription.integration(listing=title_show, ID=[], type_list='SHOW', folder=settings.show_folder, name_provider=settings.name_provider)
                else:
                    settings.log('[%s]>>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
                    settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
database.close()
del browser
del settings