# coding: utf-8
import re
import tools
import shelve
import xbmc

path = xbmc.translatePath('special://temp')
database = shelve.open(path + 'EZTV2PULSAR.db')
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
    rep = settings.dialog.select('Choose an Option:', ['Add a New Show', 'Remove a Show', 'View The List', 'Sync .strm Files', 'Exit'])
    if rep == 0:
        if len(List_name) == 0:
            if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...', settings.icon, settings.time_noti)
            url_search = settings.url_address
            if browser.open(url_search): # create the list of shows
                data = browser.content
                data = data[data.find('</option>'):]
                results = re.findall('<option value="(.*?)">(.*?)</option>', data)
                List_name = [result[1] for result in results]  # list of shows
                List_name_id = [result[0] for result in results]  # list of IDs
        name = settings.dialog.input('New Show:')
        if name == '':
            option_list = List_name
            option_ID = List_name_id
        else:
            option_list =[]
            option_ID = []
            for (itemID, item) in zip(List_name_id, List_name):
                if name.lower() in item.lower():
                    option_list.append(item)
                    option_ID.append(itemID)
            if len(option_list) == 0:
                option_list = List_name
                option_ID = List_name_id
        selection = settings.dialog.select('New Show', option_list + ['CANCEL'])
        if selection < len(option_list):
            name = option_list[selection]
            pos = name.find(',')  # CHANGE TITLE
            if pos > 0:
                name = name[pos + 1:].lstrip() + ' ' + name[:pos] # change Simpsons, The = The Simpsons
            name = name.replace(')', '').replace('(', '') # change (2015) = 2015
            name = name.replace("'",'') # replace Grey's = Greys
            if name not in List_shows:
                List_shows.append(name)
                List_shows.sort()
            ID = option_ID[selection]
            if settings.dialog.yesno(settings.name_provider, 'Do you want to add ALL the episodes available for %s' % name):
                url_search = settings.url_address # search for the show
                payload = {'SearchString1': '', 'SearchString': ID , 'search': 'Search'}
                if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...', settings.icon, settings.time_noti)
                browser.login(url_search, payload, name)
                quality = settings.settings.getSetting('quality').lower()
                magnet_list = []
                file_list = []
                title_list = []
                data = browser.content
                for magnet in re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data):
                    name_file = magnet.lower()
                    if quality == 'hdtv' and ('720p' in name_file or '1080p' in name_file):
                        name_file = name_file.replace('hdtv', '')
                    if quality in name_file:
                        magnet_list.append(magnet)
                        title = re.search('&dn=(.*?)&', magnet).group(1)
                        file_list.append(title)
                        title_list.append(name)
                tools.integration(filename=file_list, magnet=magnet_list, title=title_list, type_list='EPISODES', folder=settings.show_folder, name_provider=settings.name_provider)
    if rep == 1 and len(List_shows) > 0:
        list_rep = settings.dialog.select('Choose Show to Remove', List_shows + ['CANCEL'])
        if list_rep < len(List_shows):
            if settings.dialog.yesno(settings.name_provider, 'Do you want Remove %s?' % List_shows[list_rep]):
                del List_shows[list_rep]
    if rep == 2:
        settings.dialog.select('Shows', List_shows)
    if rep == 3:
        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...', settings.icon, settings.time_noti)
        if len(List_shows) > 0:
            quality = settings.settings.getSetting('quality').lower()
            number = int(settings.settings.getSetting('number'))
            magnet_list = []
            file_list = []
            title_list = []
            for page in range(number + 1):
                if page == 0:
                    url_search = settings.url_address
                else:
                    url_search = '%s/page_%s' % (settings.url_address, str(page))
                if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Still working...', settings.icon, settings.time_noti)
                if browser.open(url_search):
                    data = browser.content
                    for magnet in re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data):
                        for show in List_shows:
                            name_file = magnet.lower()
                            if quality == 'hdtv' and ('720p' in name_file or '1080p' in name_file):
                                name_file = name_file.replace('hdtv', '')
                            if show.replace(' ', '.').lower() in name_file and quality in name_file:
                                magnet_list.append(magnet)
                                file_list.append(re.search('&dn=(.*?)&', magnet).group(1))
                                title_list.append(show)
                else:
                    settings.log('[%s]>>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
                    settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
            tools.integration(filename=file_list, magnet=magnet_list, title=title_list, type_list='EPISODES', folder=settings.show_folder, name_provider=settings.name_provider)
        else:
            if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Empty List', settings.icon, settings.time_noti)
database['list'] = List_shows
database.sync()
database.close()
del settings
del browser
