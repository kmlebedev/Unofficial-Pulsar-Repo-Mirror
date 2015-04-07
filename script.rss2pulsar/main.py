# coding: utf-8
import re
import tools
import shelve
import xbmc
from urllib import quote_plus
from xbmc import translatePath


# this read the settings
settings = tools.Settings()
browser = tools.Browser()
# define the browser
list_url_search = []
path = xbmc.translatePath('special://temp')
Dict_RSS = {}
try:
    with open(path + 'RSS2PULSAR.txt', 'r') as fp:
        for line in fp:
            listedline = line.strip().split('::')  # split around the :: sign
            if len(listedline) > 1:  # we have the : sign in there
                Dict_RSS[listedline[0]] = listedline[1]
except:
    database = shelve.open(path + 'RSS2PULSAR.db')
    if database.has_key('dict'):
        Dict_RSS = database['dict']
rep = 0
while rep < 7:
    rep = settings.dialog.select('Choose an Option:', ['Add a New RSS', 'Easy RSS creation', 'Modify Saved RSS', 'Remove a RSS', 'View Saved RSS list', 'Manual Search', 'Read RSS list and create .strm Files', '-SETTINGS', '-HELP', 'Exit'])
    if rep == 0:  # Add a New RSS
        selection = settings.dialog.input('URL RSS:')
        name = ''
        while name is '':
            name = settings.dialog.input('Name to this RSS:').title()
        Dict_RSS[name] = selection
    if rep == 1:  # Easy RSS creation
        search = settings.dialog.input('Search query:')
        if search != '':
            type = settings.dialog.select('Type:', ['General', 'Movie', 'TV'])
            if type == 0:  # General
                selection = settings.query.replace('QUERY', quote_plus(search))
            elif type ==1:  # Movie
                selection = settings.querymovie.replace('QUERY', quote_plus(search))
            else:  # TV Show
                print settings.querytv
                selection = settings.querytv.replace('QUERY', quote_plus(search))
            name = ''
            while name is '':
                name = settings.dialog.input('Name to this RSS:').title()
            Dict_RSS[name] = selection
    if rep == 2:  # Modify RSS list
        List = [name + ": " + RSS for (name, RSS) in zip(Dict_RSS.keys(), Dict_RSS.values())]
        list_rep = settings.dialog.select('Shows', List + ['CANCEL'])
        if list_rep < len(List):
            name = Dict_RSS.keys()[list_rep]
            Dict_RSS[name]= settings.dialog.input('URL RSS:', Dict_RSS[name])
    if rep == 3 and len(Dict_RSS.keys()) > 0:  # Remove a RSS
        List = [name + ": " + RSS for (name, RSS) in zip(Dict_RSS.keys(), Dict_RSS.values())]
        list_rep = settings.dialog.select('Choose RSS to Remove', List + ['CANCEL'])
        if list_rep < len (List):
            if settings.dialog.yesno('', 'Do you want Remove %s?' % List[list_rep]):
                del Dict_RSS[Dict_RSS.keys()[list_rep]]
    if rep == 4:  # View Saved RSS list
        List = [name + ": " + RSS for (name, RSS) in zip(Dict_RSS.keys(), Dict_RSS.values())]
        settings.dialog.select('Shows', List)
    if rep == 5:  # Manual Search
        search = settings.dialog.input('Search query:')
        if search != '':
            url_search = settings.query % quote_plus(search)
            if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...',
                                                                    settings.icon, settings.time_noti)
            # Begin reading
            magnet_search = []
            title_search = []
            if settings.time_noti > 0: settings.dialog.notification(settings.name_provider,
                                                                    'Checking %s...' % url_search, settings.icon,
                                                                    settings.time_noti)
            acum = 0
            if browser.open(url_search):
                items = re.findall('<item>(.*?)</item>', browser.content, re.S)
                for item in items:
                    s_title = re.findall('title>(.*?)</title>', item)
                    s_link = re.findall(r'magnet:\?[^\'"\s<>\[\]]+', item)
                    if len(s_link) == 0:
                        s_link = re.findall(
                            r'http??[a-zA-Z0-9\.\/\?\:@\-_=#\[\]\s]+[.]torren[a-zA-Z0-9\.\/\?\:@\-_=#\[\]]+', item)
                    if len(s_link) == 0:
                        s_link = re.findall('<link>(.*?)</link>', item, re.S)
                    if len(s_link) != 0:
                        if len(s_title) > 0:
                            if s_title[0] != '':
                                title_search.append(s_title[0])
                                magnet_search.append(s_link[0])
                                acum += 1
                if acum == 0:
                    if settings.time_noti > 0: settings.dialog.notification(settings.name_provider,
                                                                            'No Movies nor Shows!!', settings.icon,
                                                                            settings.time_noti)
                else:
                    list_rep = settings.dialog.select('Choose File', title_search + ['CANCEL'])
                    if list_rep < len(title_search):
                        rep = 6  # exit
                        xbmc.executebuiltin("PlayMedia(plugin://plugin.video.pulsar/play?uri=%s)" % quote_plus(magnet_search[list_rep]))
            else:
                settings.log('[%s]>>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
                settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
    if rep == 6:
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
                        s_title = re.findall('title>(.*?)</title>', item)
                        s_link = re.findall(r'magnet:\?[^\'"\s<>\[\]]+', item)
                        if len(s_link) == 0:
                            s_link = re.findall(r'http??[a-zA-Z0-9\.\/\?\:@\-_=#\[\]\s]+[.]torren[a-zA-Z0-9\.\/\?\:@\-_=#\[\]]+', item)
                        if len(s_link) == 0:
                            s_link = re.findall('<link>(.*?)</link>', item, re.S)
                        if len(s_link) != 0:
                            if len(s_title) > 0:
                                if s_title[0] != '':
                                    info = tools.format_title(s_title[0])
                                    if 'MOVIE' in info['type']:
                                        title_movie.append(s_title[0])
                                        magnet_movie.append(s_link[0])
                                        acum += 1
                                    if 'SHOW' in info['type']:
                                        title_show.append(s_title[0])
                                        magnet_show.append(s_link[0])
                                        acum += 1
                    if acum == 0:
                        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider,'No Movies nor Shows!!', settings.icon, settings.time_noti)
                    if len(title_movie) > 0:
                        tools.integration(filename=title_movie, magnet=magnet_movie, type_list='MOVIE', folder=settings.movie_folder, silence=True, name_provider=settings.name_provider)
                    if len(title_show) > 0:
                        tools.integration(filename=title_show, magnet=magnet_show, type_list='EPISODES', folder=settings.show_folder, silence=True, name_provider=settings.name_provider)
                else:
                    settings.log('[%s]>>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
                    settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
    if rep == 7:  # Settings
        settings.settings.openSettings()
        settings = tools.Settings()
    if rep == 8:  # Help
            settings.dialog.ok("Help", "Please, check this address to find the user's operation:\n[B]http://goo.gl/0b44BY[/B]")
# save the dictionary
with open(path + 'RSS2PULSAR.txt', 'w') as fp:
    for p in Dict_RSS.items():
        fp.write("%s::%s\n" % p)
del browser
del settings