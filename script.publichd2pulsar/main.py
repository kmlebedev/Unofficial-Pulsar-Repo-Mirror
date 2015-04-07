# coding: utf-8
import re
import tools
from urllib import unquote_plus
from xbmcaddon import Addon
from xbmc import sleep


# this read the settings
settings = tools.Settings()
browser = tools.Browser()
filters = tools.Filtering()


# using function from Steeve to add Provider's name and search torrent
def extract_magnets(data):
    try:
        filters.information()  # print filters settings
        data = tools.clean_html(data)
        rows = re.findall('fa fa-download(.*?)</td>(.*?)</td>(.*?)</td>(.*?)</td>(.*?)</td>(.*?)</td>(.*?)</td>(.*?)</tr>', data, re.S)
        size = [s[2].replace('\n                            <td>', '') for s in rows]
        seeds = [s[5].replace('\n                            <td>', '') for s in rows]
        peers = [s[6].replace('\n                            <td>', '') for s in rows]
        lname = re.findall('torrent-filename">(.*?)>(.*?)<', data, re.S)  # list the name
        cont = 0
        results = []
        for cm, magnet in enumerate(re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)):
            info_magnet = tools.Magnet(magnet)
            name = unquote_plus(lname[cm][1]).replace('.',' ').title()
            if filters.verify(name,size[cm]):
                    results.append({"name": name, "uri": magnet, "info_hash": info_magnet.hash, "size": tools.size_int(size[cm]),
                           "language": 'en', "trackers": info_magnet.trackers, "seeds": int(seeds[cm]), "peers": int(peers[cm])
                           })  # return le torrent
                    cont += 1
            else:
                settings.log('[%s]%s' % (settings.name_provider_clean, filters.reason))
            if cont == settings.max_magnets:  # limit magnets
                break
        return results
    except:
        settings.log('[%s]%s' % (settings.name_provider_clean, '>>>>>>>ERROR parsing data<<<<<<<'))
        settings.dialog.notification(settings.name_provider, '>>>>>>>>ERROR parsing data<<<<<<<<', settings.icon, 1000)


def search(query='', type='', silence=False):
    results = []
    if type == 'MOVIE':
        folder = settings.movie_folder
    else:
        folder = settings.show_folder
    # start to search
    settings.pages = settings.dialog.numeric(0, 'Number of pages:')
    if settings.pages == '' or settings.pages == 0:
        settings.pages = "1"
    settings.pages = int(settings.pages)
    for page in range(settings.pages):
        url_search = query % (settings.url_address, page)
        settings.log('[%s]%s' % (settings.name_provider_clean, url_search))
        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Page %s...' % str(page + 1),
                                                                settings.icon, settings.time_noti)
        if browser.open(url_search):
            results.extend(extract_magnets(browser.content))
            if int(page) % 10 == 0: sleep(3000)  # to avoid too many connections
        else:
            settings.log('[%s]%s' % (settings.name_provider_clean, '>>>>>>>%s<<<<<<<' % browser.status))
            settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
    if len(results) > 0:
        title = []
        magnet = []
        for item in results:
            info = tools.format_title(item['name'])
            if info['type'] == type:
                title.append(item['name'])
                magnet.append(item['uri'])
        tools.integration(filename=title, magnet=magnet, type_list=type, folder=folder, silence=silence,
                           name_provider=settings.name_provider, message=type)


#premium account
username = Addon().getSetting('username')  # username
password = Addon().getSetting('password')  # passsword
browser.open(settings.url_address + '/auth/login')
_token = re.search('_token" type="hidden" value="(.*?)"', browser.content).group(1) # hidden variable required to log in
# open premium account
if not browser.login(settings.url_address + '/auth/login', {'username': username, 'password': password, '_token': _token}, "Forgot Password"):  # login
    settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 5000)
    settings.log('[%s]%s' % (settings.name_provider_clean, '>>>>>>>%s<<<<<<<' % browser.status))
# start the selection
type = ['', 'MOVIE', 'SHOW', 'MOVIE']
category = settings.dialog.select('Category:', ['Movies', 'TV Shows', 'XXX', '-SETTINGS', '-HELP', 'CANCEL']) + 1  # select the category
if category < 4:
    quality = settings.dialog.select('Quality:', ['ALL', '720p', '1080p', '3D', 'UHD'])
    riptype = settings.dialog.select('Rip Type:', ['ALL', 'BDRip', 'BLU-RAY', 'BLU-RAY REMUX', 'BRRip', 'DVD', 'DVDRip', 'HDRip', 'HDTV', 'VODRip', 'WEB-DL', 'WEBRip'])
    query = '%s/torrents?category=' + str(category) + '&quality=' + str(quality) + '&rip_type=' + str(riptype) + '&page=%s'
    search(query, type[category])
if category == 4:  # Settings
    settings.settings.openSettings()
    settings = tools.Settings()
if category == 5:  # Help
        settings.dialog.ok("Help", "Please, check this address to find the user's operation:\n[B]http://goo.gl/0b44BY[/B]")


# delete
del browser
del settings
del filters