# coding: utf-8
import re
import tools
import shelve
from xbmc import translatePath
from xbmc import sleep


def change_title(name=''):
    pos = name.find(',')  # CHANGE TITLE
    if pos > 0:
        name = name[pos + 1:].lstrip() + ' ' + name[:pos]  # change Simpsons, The = The Simpsons
    name = name.replace(')', '').replace('(', '')  # change (2015) = 2015
    return name.replace("'", '')  # replace Grey's = Greys


# main
path = translatePath('special://temp')
#get the list
try:
    with open(path + 'EZTV2PULSAR.txt', "r") as text_file:  # create .strm
        List_shows = [line.strip() for line in text_file]
        text_file.close()
except:
    #convert from the old version
    database = shelve.open(path + 'EZTV2PULSAR.db')
    List_shows = []
    if database.has_key('list'):
       List_shows = database['list']
    else:
       List_shows = []

# this read the settings
settings = tools.Settings()
# define the browser
browser = tools.Browser()

rep = 0
List_name = []
List_name_id = []
while rep is not 7:
    rep = settings.dialog.select('Choose an Option:', ['Add a New Show', 'Remove a Show', 'View The List', 'ReBuild All Episodes', 'Sync .strm Files', '-SETTINGS', '-HELP', 'Exit'])
    if rep == 0:  # Add new Show
        if len(List_name) == 0:
            if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...', settings.icon, settings.time_noti)
            url_search = settings.url_address
            settings.log('[%s]%s' % (settings.name_provider_clean, settings.url_address))
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
            name = change_title(option_list[selection])
            if name not in List_shows:
                List_shows.append(name)
                List_shows.sort()
            ID = option_ID[selection]
            if settings.dialog.yesno(settings.name_provider, 'Do you want to add episodes available for %s' % name):
                url_search = settings.url_address # search for the show
                payload = {'SearchString1': '', 'SearchString': ID , 'search': 'Search'}
                if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online for %s...' % name, settings.icon, settings.time_noti)
                settings.log('[%s]%s' % (settings.name_provider_clean, settings.url_address))
                browser.login(url_search, payload, name)
                quality_options = ['HDTV:720p:1080p', '1080p:720p:HDTV', '720p:1080p', '1080p:720p', 'HDTV:720p', '720p:HDTV', 'HDTV', '720p', '1080p']
                quality_ret = settings.dialog.select('Quality:', quality_options)
                quality_keys = quality_options[quality_ret].lower().split(":")
                magnet_list = []
                file_list = []
                title_list = []
                data = browser.content
                seasons = list(set(re.findall('S[0-9]+E', data.upper()))) + ['ALL']
                seasons.sort()
                season = settings.dialog.select('Season:', seasons)
                print seasons[season]
                magnets = re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)
                for quality in quality_keys:
                    for magnet in magnets:
                        name_file = magnet.lower() + ' hdtv'  # take any file as hdtv by default
                        if seasons[season].lower() in name_file or seasons[season] == 'ALL':  # check for the right season to add
                            if quality == 'hdtv' and ('720p' in name_file or '1080p' in name_file):
                                name_file = name_file.replace('hdtv', '')
                            if quality in name_file:
                                magnet_list.append(magnet)
                                title = magnet[magnet.find('&dn=') + 4:] + '&' # find the start of the name
                                title = title[:title.find('&')]
                                file_list.append(title)
                                title_list.append(name)
                tools.integration(filename=file_list, magnet=magnet_list, title=title_list, type_list='EPISODES', folder=settings.show_folder, name_provider=settings.name_provider)
    if rep == 1 and len(List_shows) > 0:  # Remove Show
        list_rep = settings.dialog.select('Choose Show to Remove', List_shows + ['CANCEL'])
        if list_rep < len(List_shows):
            if settings.dialog.yesno(settings.name_provider, 'Do you want Remove %s?' % List_shows[list_rep]):
                del List_shows[list_rep]
    if rep == 2:  # View Show
        settings.dialog.select('Shows', List_shows)
    if rep == 3:  # Rebuild Strm files
        if settings.dialog.yesno("EZTV2PULSAR","Do you want to rebuild the all the episodes?"):
            quality_options = ['HDTV:720p:1080p', '1080p:720p:HDTV', '720p:1080p', '1080p:720p', 'HDTV:720p', '720p:HDTV', 'HDTV',
                               '720p', '1080p']
            quality_ret = settings.dialog.select('Quality:', quality_options)
            quality_keys = quality_options[quality_ret].lower().split(":")
            number = int(settings.settings.getSetting('number'))
            if len(List_name) == 0:
                if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...',
                                                                        settings.icon, settings.time_noti)
                url_search = settings.url_address
                settings.log('[%s]%s' % (settings.name_provider_clean, settings.url_address))
                if browser.open(url_search):  # create the list of shows
                    data = browser.content
                    data = data[data.find('</option>'):]
                    results = re.findall('<option value="(.*?)">(.*?)</option>', data)
                    List_name = [change_title(result[1]) for result in results]  # list of shows
                    List_name_id = [result[0] for result in results]  # list of IDs
            magnet_list = []
            file_list = []
            title_list = []
            ID = dict(zip(List_name, List_name_id))
            for show in List_shows:
                if settings.time_noti > 0: settings.dialog.notification(settings.name_provider,
                                            'Checking Online for %s...' % show, settings.icon, settings.time_noti)
                url_search = settings.url_address  # search for the show
                payload = {'SearchString1': '', 'SearchString': ID[show], 'search': 'Search'}
                if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...',
                                                                        settings.icon, settings.time_noti)
                settings.log('[%s]%s-%s' % (settings.name_provider_clean, settings.url_address, show))
                browser.login(url_search, payload, show)
                data = browser.content
                magnets = re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)
                for quality in quality_keys:
                    for magnet in magnets:
                        name_file = magnet.lower() + ' hdtv'  # take any file as hdtv by default
                        if quality == 'hdtv' and ('720p' in name_file or '1080p' in name_file):
                            name_file = name_file.replace('hdtv', '')
                        if quality in name_file:
                            magnet_list.append(magnet)
                            title = magnet[magnet.find('&dn=') + 4:] + '&'  # find the start of the name
                            title = title[:title.find('&')]
                            file_list.append(title)
                            title_list.append(show)
            tools.integration(filename=file_list, magnet=magnet_list, title=title_list, type_list='EPISODES',
                              folder=settings.show_folder, name_provider=settings.name_provider)
    if rep == 4:  # Update strm
        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...', settings.icon, settings.time_noti)
        if len(List_shows) > 0:
            quality_options = ['HDTV:720p:1080p', '1080p:720p:HDTV', '720p:1080p', '1080p:720p', 'HDTV:720p', '720p:HDTV', 'HDTV', '720p', '1080p']
            quality_ret = settings.dialog.select('Quality:', quality_options)
            quality_keys = quality_options[quality_ret].lower().split(":")
            number = int(settings.settings.getSetting('number'))
            magnet_list = []
            file_list = []
            title_list = []
            if number == 0:  # manual pages if the parameter is zero
                number = settings.dialog.numeric(0, 'Number of pages:')
                if number == '' or number == 0:
                    number = "1"
                number = int(number)
            for page in range(number + 1):
                if page == 0:
                    url_search = settings.url_address
                else:
                    url_search = '%s/page_%s' % (settings.url_address, str(page))
                if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Still working...', settings.icon, settings.time_noti)
                if browser.open(url_search):
                    data = browser.content
                    for quality in quality_keys:
                        for magnet in re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data):
                            for show in List_shows:
                                name_file = magnet.lower()
                                if quality == 'hdtv' and ('720p' in name_file or '1080p' in name_file):
                                    name_file = name_file.replace('hdtv', '')
                                if show.replace(' ', '.').lower() in name_file and quality in name_file:
                                    magnet_list.append(magnet)
                                    file_list.append(re.search('&dn=(.*?)&', magnet).group(1))
                                    title_list.append(show)
                        if int(page) % 10 == 0: sleep(3000)  # to avoid too many connections
                else:
                    settings.log('[%s]>>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
                    settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
            tools.integration(filename=file_list, magnet=magnet_list, title=title_list, type_list='EPISODES', folder=settings.show_folder, name_provider=settings.name_provider)
        else:
            if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Empty List', settings.icon, settings.time_noti)
    if rep == 5:  # settings
        settings.settings.openSettings()
        settings = tools.Settings()
    if rep == 6:  # help
            settings.dialog.ok("Help", "Please, check this address to find the user's operation:\n[B]http://goo.gl/0b44BY[/B]")
#save the list
with open(path + 'EZTV2PULSAR.txt', "w") as text_file:  # create .strm
    text_file.writelines(list("%s\n" % item for item in List_shows))
    text_file.close()
del settings
del browser
