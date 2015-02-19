# coding: utf-8
import re
import tools
import shelve
import xbmc

path = xbmc.translatePath('special://temp')
database = shelve.open(path + 'HorribleSubs2PULSAR.db')
# this read the settings
settings = tools.Settings(movie=False)
# define the browser
browser = tools.Browser()
rep = 0
if database.has_key('list'):
    List_shows = database['list']
else:
    List_shows = []
List_name = []
while rep is not 4:
    rep = settings.dialog.select('Choose an Option:', ['Add a New Anime', 'Remove a Anime', 'View The List', 'Sync .strm Files', 'Exit'])
    if rep == 0:
        list_name = tools.search_anime()
        if len(list_name) > 0:
            selection = settings.dialog.select('Select One Show:', list_name + ['CANCEL']) # check the name
            if  selection < len (list_name):
                name = list_name[selection]
                if name not in List_shows:
                    List_shows.append(name)
                    List_shows.sort()
                if settings.dialog.yesno(settings.name_provider, 'Do you want to add ALL the episodes available for %s' % name):
                    url_search = '%s/lib/search.php?value=%s' % (settings.url_address, name.replace(' ', '+')) # search for the show
                    print url_search
                    browser.open(url_search)
                    quality = settings.settings.getSetting('quality')
                    magnet_list = []
                    file_list = []
                    title_list = []
                    data = browser.content
                    if data is not None:
                        for (magnet, name_file) in zip(re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data), re.findall('HorribleSubs..(.*?)<', data)):
                            if quality in name_file:
                                magnet_list.append(magnet)
                                title = name_file[:-4]
                                file_list.append(title)
                                title_list.append(name)
                        tools.integration(filename=file_list, magnet=magnet_list, title=title_list, type_list='ANIME',
                                        folder=settings.show_folder, name_provider=settings.name_provider)
    if rep == 1 and len(List_shows) > 0:
        list_rep = settings.dialog.select('Choose Show to Remove', List_shows + ['CANCEL'])
        if list_rep < len(List_shows):
            if settings.dialog.yesno('', 'Do you want Remove %s?' % List_shows[list_rep]):
                del List_shows[list_rep]
    if rep == 2:
        settings.dialog.select('Shows', List_shows)
    if rep == 3:
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
                tools.integration(filename=file_list, magnet=magnet_list, title=title_list, type_list='ANIME', folder=settings.show_folder, name_provider=settings.name_provider)
            else:
                settings.log('[%s]>>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
                settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
        else:
            if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Empty List', settings.icon, settings.time_noti)
database['list'] = List_shows
database.sync()
database.close()
del settings
del browser
