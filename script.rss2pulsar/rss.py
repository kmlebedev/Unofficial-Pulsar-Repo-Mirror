# library to access URL, translation title and filtering
__author__ = 'mancuniancol'
import re 
import xbmcaddon
import xbmc
import xbmcgui
import os


class Settings:
    def __init__(self, movie=True, show=True):
        self.dialog = xbmcgui.Dialog()
        self.log = xbmc.log
        self.settings = xbmcaddon.Addon()
        self.id_addon = self.settings.getAddonInfo('id')  # gets name
        self.icon = self.settings.getAddonInfo('icon')
        self.name_provider = self.settings.getAddonInfo('name')  # gets name
        self.name_provider_clean = re.sub('.COLOR (.*?)]', '', self.name_provider.replace('[/COLOR]', ''))
        self.query = self.settings.getSetting('query').replace('QUERY', '%s')
        self.service = self.settings.getSetting('service')
        self.time_noti = int(self.settings.getSetting('time_noti'))
        self.movie_folder = ''
        self.show_folder = ''
        if movie:
            self.movie_folder = self.settings.getSetting('movie_folder')
            if self.movie_folder == '':
                self.settings.openSettings()
        if show:
            self.show_folder = self.settings.getSetting('show_folder')
            if self.show_folder == '':
                self.settings.openSettings()
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


class Filtering:
    def __init__(self):
        self.settings = xbmcaddon.Addon()
        self.id_addon = self.settings.getAddonInfo('id')  # gets name
        self.name_provider = self.settings.getAddonInfo('name')  # gets name
        self.reason = ''
        self.title = ''
        self.quality_allow = ['*']
        self.quality_deny = []
        self.title = ''
        self.max_size = 10.00  # 10 it is not limit
        self.min_size = 0.00
        #size
        if self.settings.getSetting('movie_min_size') == '':
            self.movie_min_size = 0.0
        else:
            self.movie_min_size = float(self.settings.getSetting('movie_min_size'))
        if self.settings.getSetting('movie_max_size') == '':
            self.movie_max_size = 10.0
        else:
            self.movie_max_size = float(self.settings.getSetting('movie_max_size'))
        if self.settings.getSetting('TV_min_size') == '':
            self.TV_min_size = 0.0
        else:
            self.TV_min_size = float(self.settings.getSetting('TV_min_size'))
        if self.settings.getSetting('TV_max_size') == '':
            self.TV_max_size = 10.0
        else:
            self.TV_max_size = float(self.settings.getSetting('TV_max_size'))

        # movie
        movie_qua1 = self.settings.getSetting('movie_qua1')  # 480p
        movie_qua2 = self.settings.getSetting('movie_qua2')  # HDTV
        movie_qua3 = self.settings.getSetting('movie_qua3')  # 720p
        movie_qua4 = self.settings.getSetting('movie_qua4')  # 1080p
        movie_qua5 = self.settings.getSetting('movie_qua5')  # 3D
        movie_qua6 = self.settings.getSetting('movie_qua6')  # CAM
        movie_qua7 = self.settings.getSetting('movie_qua7')  # TeleSync
        movie_qua8 = self.settings.getSetting('movie_qua8')  # Trailer
        # Accept File
        movie_key_allowed = self.settings.getSetting('movie_key_allowed').replace(', ',',').replace(' ,',',')
        movie_allow = re.split(',',movie_key_allowed)
        if movie_qua1 == 'Accept File': movie_allow.append('480p')
        if movie_qua2 == 'Accept File': movie_allow.append('HDTV')
        if movie_qua3 == 'Accept File': movie_allow.append('720p')
        if movie_qua4 == 'Accept File': movie_allow.append('1080p')
        if movie_qua5 == 'Accept File': movie_allow.append('3D')
        if movie_qua6 == 'Accept File': movie_allow.append('CAM')
        if movie_qua7 == 'Accept File': movie_allow.extend(['TeleSync', ' TS '])
        if movie_qua8 == 'Accept File': movie_allow.append('Trailer')
        #Block File
        movie_key_denied = self.settings.getSetting('movie_key_denied').replace(', ',',').replace(' ,',',')
        movie_deny = re.split(',',movie_key_denied)
        if movie_qua1 == 'Block File': movie_deny.append('480p')
        if movie_qua2 == 'Block File': movie_deny.append('HDTV')
        if movie_qua3 == 'Block File': movie_deny.append('720p')
        if movie_qua4 == 'Block File': movie_deny.append('1080p')
        if movie_qua5 == 'Block File': movie_deny.append('3D')
        if movie_qua6 == 'Block File': movie_deny.append('CAM')
        if movie_qua7 == 'Block File': movie_deny.extend(['TeleSync', '?TS?'])
        if movie_qua8 == 'Block File': movie_deny.append('Trailer')
        if '' in movie_allow: movie_allow.remove('')
        if '' in movie_deny: movie_deny.remove('')
        if len(movie_allow)==0: movie_allow = ['*']
        self.movie_allow = movie_allow
        self.movie_deny = movie_deny
        # TV
        TV_qua1 = self.settings.getSetting('TV_qua1')  # 480p
        TV_qua2 = self.settings.getSetting('TV_qua2')  # HDTV
        TV_qua3 = self.settings.getSetting('TV_qua3')  # 720p
        TV_qua4 = self.settings.getSetting('TV_qua4')  # 1080p
        # Accept File
        TV_key_allowed = self.settings.getSetting('TV_key_allowed').replace(', ',',').replace(' ,',',')
        TV_allow = re.split(',',TV_key_allowed)
        if TV_qua1 == 'Accept File': TV_allow.append('480p')
        if TV_qua2 == 'Accept File': TV_allow.append('HDTV')
        if TV_qua3 == 'Accept File': TV_allow.append('720p')
        if TV_qua4 == 'Accept File': TV_allow.append('1080p')
        # Block File
        TV_key_denied = self.settings.getSetting('TV_key_denied').replace(', ',',').replace(' ,',',')
        TV_deny = re.split(',',TV_key_denied)
        if TV_qua1 == 'Block File': TV_deny.append('480p')
        if TV_qua2 == 'Block File': TV_deny.append('HDTV')
        if TV_qua3 == 'Block File': TV_deny.append('720p')
        if TV_qua4 == 'Block File': TV_deny.append('1080p')
        if '' in TV_allow: TV_allow.remove('')
        if '' in TV_deny: TV_deny.remove('')
        if len(TV_allow)==0: TV_allow = ['*']
        self.TV_allow = TV_allow
        self.TV_deny = TV_deny

    def use_movie(self):
        self.quality_allow = self.movie_allow
        self.quality_deny = self.movie_deny
        self.min_size = self.movie_min_size
        self.max_size = self.movie_max_size

    def use_TV(self):
        self.quality_allow = self.TV_allow
        self.quality_deny = self.TV_deny
        self.min_size = self.TV_min_size
        self.max_size = self.TV_max_size

    def information(self):
        xbmc.log('[%s] Accepted Keywords: %s' % (self.id_addon, str(self.quality_allow)))
        xbmc.log('[%s] Blocked Keywords: %s' % (self.id_addon, str(self.quality_deny)))
        xbmc.log('[%s] min Size: %s' % (self.id_addon, str(self.min_size) + ' GB'))
        xbmc.log('[%s] max Size: %s' % (self.id_addon, (str(self.max_size)  + ' GB') if self.max_size != 10 else 'MAX'))

    #normalize
    def normalize(self, word):
        value = ''
        for a in word:
            if ord(a) < 128:
                value += chr(ord(a))
        value = value.replace('-', ' ').replace('&ntilde;', '')
        return value

    # validate keywords
    def included(self, value, keys, strict=False):
        value = ' ' + self.normalize(value) + ' '
        res = False
        if '*' in keys:
            res = True
        else:
            res1 = []
            for key in keys:
                res2 = []
                for item in re.split('\s', key):
                    item = self.normalize(item)
                    item = item.replace('?', ' ')
                    if strict: item = ' ' + item + ' '  # it makes that strict the comparation
                    if item.upper() in value.upper():
                        res2.append(True)
                    else:
                        res2.append(False)
                res1.append(all(res2))
            res = any(res1)
        return res

    # validate size
    def size_clearance(self, size):
        max_size1 = 100 if self.max_size == 10 else self.max_size
        res = False
        value = float(re.split('\s', size.replace(',', ''))[0])
        value *= 0.001 if 'M' in size else 1
        if self.min_size <= value <= max_size1:
            res = True
        return res

    # verify
    def verify(self, name, size):
        self.reason = name.replace(' - ' + self.name_provider, ' ***Blocked File by')
        if self.included(name, [self.title.replace('.', ' ')], True):
            result = True
            if name != None:
                if not self.included(name, self.quality_allow) or self.included(name, self.quality_deny):
                    self.reason += ", Keyword"
                    result = False
            if size != None:
                if not self.size_clearance(size):
                    result = False
                    self.reason += ", Size"
        else:
            result = False
            self.reason += ", Name"
        self.reason = self.reason.replace('by,', 'by') + '***'
        return result


def normalize(word):
    value = ''
    for a in word:
        if ord(a) < 128:
            value += chr(ord(a))
    value = value.replace('-', ' ').replace('&ntilde;', '')
    return value


def clear_name(name):
    print name
    from HTMLParser import HTMLParser
    name = name.replace('<![CDATA[', '').replace(']]', '')
    name = HTMLParser().unescape(normalize(name))
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
    import unicodedata
    keys = {'"': ' ', '*': ' ', '/': ' ', ':': ' ', '<': ' ', '>': ' ', '?': ' ', '|': ' '}
    for key in keys.keys():
        value = value.replace(key, keys[key])
    if type(value) is unicode:
        normalize = unicodedata.normalize('NFKD', value)
        value = normalize.encode('ascii', 'ignore').replace(':', '')
    value = ' '.join(value.split())
    return value


def format_title(value=''):
    import re
    value = safe_name(value.lower())
    value = value.replace('.', ' ').replace(')', '').replace('(', '')
    formats = ['s[0-9]+e[0-9]+', 's[0-9]+ e[0-9]+', '[0-9]+x[0-9]+', '[0-9][0-9][0-9][0-9] [0-9][0-9] [0-9][0-9]',
               'season [0-9]+', 'season[0-9]+', 's[0-9][0-9]']
    for format in formats:
        sshow = re.search(format, value) # format shows
        if sshow is not None:
            break
    if sshow is None:
        # it is a movie
        value += ' 0000'
        syear = re.search('[0-9][0-9][0-9][0-9]', value)
        year = syear.group(0)
        pos = value.find(year)
        if pos >0:
            title = value[:value.find(year)].strip()
            rest =  value[value.find(year) + 4:].strip().replace(' 0000', '')
        else:
            title = value.replace(' 0000', '')
            rest = ''
        title = title.replace('[', '').replace(']', '').strip()
        clean_title = title
        if year not in '0000':
            title += ' (' + year + ')'
        title = title.title().replace('Of', 'of')
        folder = title
        return {'title': title, 'folder': folder, 'rest': rest, 'type': 'MOVIE', 'clean_title': clean_title, 'year': year}
    else:
        # it is a show
        episode = sshow.group(0)
        title = value[:value.find(episode)].strip()
        rest =  value[value.find(episode) + len(episode):].strip()
        title = title.replace('[', '').replace(']', '').strip()
        if 'x' in episode:
            episode = 's' + episode.replace('x', 'e')
        episode = episode.replace(' ', '')  # remove spaces in the episode format
        folder = title.title().replace('Of', 'of')
        clean_title = folder
        title = folder + ' ' + episode.upper()
        year = 0000
        return {'title': title, 'folder': folder, 'rest': rest, 'type': 'SHOW', 'clean_title': clean_title, 'year': year}


# find the name in different language
def integration(filename=[], magnet=[], title=[], type_list='', folder='', silence=False, message='', name_provider=''):
    from urllib import quote_plus
    if len(title) == 0:
        title = filename
    filters = Filtering() # start filtering
    if type_list == 'MOVIE':
        filters.use_movie()
    else:
        filters.use_TV() # TV SHOWS and Anime
    name_provider_clean = re.sub('.COLOR (.*?)]', '', name_provider.replace('[/COLOR]', ''))
    dialog = xbmcgui.Dialog()
    overwrite = xbmcaddon.Addon().getSetting('overwrite')
    duplicated = xbmcaddon.Addon().getSetting('duplicated')
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
                info = format_title(title[cm])
                check = False
                details_title = ''
                if len(info['rest']) >0: # check for quality filtering
                    filters.title = info['title'] + ' ' + info['rest']
                    if filters.verify(filters.title, None): # just check the quality no more
                        check = True
                        if duplicated == 'true':
                            details_title = ' ' + info['rest']
                else:
                    check = True
                if check:  # the file has passed the filtering
                    name = info['title'] + details_title
                    title[cm] = info['title']
                    if type_list == 'ANIME':
                        pos = name.rfind('- ')
                        name = name[:pos] + '- EP' + name[pos+2:]
                    if len(info['folder']) > 100:  # to limit the length of directory name
                        info['folder'] = info['folder'][:100]
                    directory = folder + info['folder'] + folder[-1]
                    if not os.path.exists(directory):
                        try:
                            os.makedirs(directory)
                        except:
                            pass
                    uri_string = quote_plus(clear_name(magnet[cm]))
                    if plugin == 'Pulsar':
                        link = 'plugin://plugin.video.pulsar/play?uri=%s' % uri_string
                    elif plugin == 'KmediaTorrent':
                        link = 'plugin://plugin.video.kmediatorrent/play/%s' % uri_string
                    else:
                        link = 'plugin://plugin.video.xbmctorrent/play/%s' % uri_string
                    if not os.path.isfile("%s%s.strm" % (directory, name)) or overwrite == 'true':
                        cont += 1
                        if len(name) > 100:
                            name = name[:99]
                        with open("%s%s.strm" % (directory, name), "w") as text_file:  # create .strm
                            text_file.write(link)
                        if not silence: pDialog.update(int(float(cm) / total * 100), 'Creating %s%s.strm...' % (directory, name))
                        if not silence:
                            if pDialog.iscanceled():
                                break
                        if cont % 100 == 0 and time_noti >0:
                            dialog.notification(name_provider, '%s %s found - Still working...\n%s'
                                                % (cont, type_list, message), xbmcgui.NOTIFICATION_INFO, time_noti)
                        xbmc.log('[%s]%s%s.strm added' % (name_provider_clean, directory, name))
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
    del filters