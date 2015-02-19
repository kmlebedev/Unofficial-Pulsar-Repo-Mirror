# library to access URL, translation title and filtering
__author__ = 'mancuniancol'
import re 
import xbmcaddon
import xbmc
import xbmcgui
import os
import time

class Settings:
    def __init__(self, movie=True, show=True):
        self.dialog = xbmcgui.Dialog()
        self.log = xbmc.log
        self.settings = xbmcaddon.Addon()
        self.id_addon = self.settings.getAddonInfo('id')  # gets name
        self.icon = self.settings.getAddonInfo('icon')
        self.name_provider = self.settings.getAddonInfo('name')  # gets name
        self.name_provider_clean = re.sub('.COLOR (.*?)]', '', self.name_provider.replace('[/COLOR]', ''))
        self.url_address = self.settings.getSetting('url_address')
        self.service = self.settings.getSetting('service')
        self.time_noti = int(self.settings.getSetting('time_noti'))
        self.movie_folder = ''
        self.show_folder = ''
        if movie:
            self.movie_folder = self.settings.getSetting('movie_folder')
            if self.movie_folder == '':
                self.settings.openSettings()
            self.movie_folder = self.settings.getSetting('movie_folder')
        if show:
            self.show_folder = self.settings.getSetting('show_folder')
            if self.show_folder == '':
                self.settings.openSettings()
            self.show_folder = self.settings.getSetting('show_folder')
        # remove .strm
        self.number_files = int('0%s' % self.settings.getSetting('number_files'))
        self.dialog = xbmcgui.Dialog()

class Browser:
    def __init__(self):
        import cookielib
        self._cookies = None
        self.cookies = cookielib.LWPCookieJar()
        self.content = None
        self.status = ''

    def create_cookies(self, payload):
        import urllib
        self._cookies = urllib.urlencode(payload)

    def open(self,url):
        import urllib2
        result = True
        if self._cookies is not None:
            req = urllib2.Request(url,self._cookies)
            self._cookies = None
        else:
            req = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36')
        req.add_header('Content-Language', 'en')
        req.add_header("Accept-Encoding", "gzip")
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))#open cookie jar
        try:
            response = opener.open(req)  # send cookies and open url
            #borrow from provider.py Steeve
            if response.headers.get("Content-Encoding", "") == "gzip":
                import zlib
                self.content = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(response.read())
            else:
                self.content = response.read()
            response.close()
            self.status = 200
        except urllib2.URLError as e:
            self.status = str(e.reason)
            result = False
        except urllib2.HTTPError as e:
            self.status = e.code
            result = False
        except:
            self.status = 'URL unreachable'
            result = False
        return result

    def login(self, url, payload, word=None):
        result = False
        self.create_cookies(payload)
        if self.open(url):
            result = True
            data = self.content
            if word is not None:
                if word in data:
                    self.status = 'Wrong Username or Password'
                    result = False
        return result


def clear_name(name):
    match = re.search("S[0-9][0-9]E", name, re.I)
    if match is not None:
        name = name[:match.start(0)].rstrip()
    return name


def search_show():
    dialog = xbmcgui.Dialog()
    url_address = xbmcaddon.Addon().getSetting('url_address')
    browser = Browser()
    name = dialog.input('New Anime:')
    url = '%s/lib/search.php?value=%s' % (url_address, name.replace(' ', '+'))
    list_names = {}
    if browser.open(url):
        data = browser.content
        names = [item[:item.rfind('-')].rstrip().replace(' -', '') for item in re.findall('HorribleSubs..(.*?)<', data)]
        for  item in names:
            list_names[item] = 'Yes'
    return list_names.keys()
    del browser
    del dialog


def safe_name(value):
    keys = {'"': ' ', '*': ' ', '/': ' ', ':': ' ', '<': ' ', '>': ' ', '?': ' ', '|': ' ',
            '&#039;': "'"}
    for key in keys.keys():
        value = value.replace(key, keys[key])
    return value


# find the name in different language
def integration(filename=[], magnet=[], title=[], type_list='', folder='', silence=False, message='', name_provider=''):
    from urllib import quote_plus
    if len(title) == 0:
        title = filename
    name_provider_clean = re.sub('.COLOR (.*?)]', '', name_provider.replace('[/COLOR]', ''))
    dialog = xbmcgui.Dialog()
    overwrite = xbmcaddon.Addon().getSetting('overwrite')
    plugin = xbmcaddon.Addon().getSetting('plugin')
    time_noti = int(xbmcaddon.Addon().getSetting('time_noti'))
    total = len(filename)
    if total > 0:
        if not silence:
            answer = dialog.yesno('%s: %s items\nDo you want to integrate this list?' % (name_provider, total), '%s' % filename)
        else:
            answer = True
        if answer:
            pDialog = xbmcgui.DialogProgress()
            if not silence:
                pDialog.create(name_provider, 'Checking for %s\n%s' % (type_list, message))
            else:
                if time_noti > 0: dialog.notification(name_provider, 'Checking for %s\n%s' % (type_list, message), xbmcgui.NOTIFICATION_INFO, time_noti)
            cont = 0
            directory = ''
            for cm, name in enumerate(filename):
                name = safe_name(name)
                title[cm] = safe_name(title[cm])
                if type_list == 'ANIME':
                    pos = name.rfind('- ')
                    name = name[:pos] + '- EP' + name[pos+2:]
                directory = folder + clear_name(title[cm]) + folder[-1]
                if not os.path.exists(directory):
                    try:
                        os.makedirs(directory)
                    except:
                        pass
                if plugin == 'Pulsar':
                    link = 'plugin://plugin.video.pulsar/play?uri=%s' % quote_plus(magnet[cm])
                elif plugin == 'KmediaTorrent':
                    link = 'plugin://plugin.video.kmediatorrent/play/%s' % quote_plus(magnet[cm])
                else:
                    link = 'plugin://plugin.video.xbmctorrent/play/%s' % quote_plus(magnet[cm])
                if not os.path.isfile("%s%s.strm" % (directory, name)) or overwrite == 'true':
                    cont += 1
                    with open("%s%s.strm" % (directory, name), "w") as text_file:  # create .strm
                        text_file.write(link)
                    if not silence: pDialog.update(int(float(cm) / total * 100), 'Creating %s%s.strm...' % (directory, name))
                    if not silence:
                        if pDialog.iscanceled():
                            break
                    if cont % 100 == 0 and time_noti > 0:
                        dialog.notification(name_provider, '%s %s found - Still working...\n%s'
                                            % (cont, type_list, message), xbmcgui.NOTIFICATION_INFO, time_noti)
                    xbmc.log('[%s]%s%s.strm added' % (name_provider_clean, directory.encode('utf-8'), name.encode('utf-8')), xbmc.LOGINFO)
                if not silence:
                    if pDialog.iscanceled():
                        break
            pDialog.close()
            if cont > 0:
                if not xbmc.getCondVisibility('Library.IsScanningVideo'):
                    xbmc.executebuiltin('XBMC.UpdateLibrary(video)')  # update the library with the new information
                xbmc.log('[%s]%s %s added./n%s' % (name_provider_clean, cont, type_list, message))
                if not silence:
                    dialog.ok(name_provider, '%s %s added.\n%s' % (cont, type_list, message))
                else:
                    if time_noti > 0: dialog.notification(name_provider, '%s %s added.\n%s' % (cont, type_list, message), xbmcgui.NOTIFICATION_INFO, time_noti)
            else:
                xbmc.log('[%s] No new %s\n%s' % (name_provider_clean, type_list, message))
                if not silence:
                    dialog.ok(name_provider, 'No new %s\n%s' % (type_list, message))
                else:
                    if time_noti > 0: dialog.notification(name_provider, 'No new %s\n%s' % (type_list, message), xbmcgui.NOTIFICATION_INFO, time_noti)
            del pDialog
    else:
        xbmc.log('[%s] Empty List' % name_provider_clean)
        if not silence: dialog.ok(name_provider, 'Empty List, Try another one, please')
    del dialog
