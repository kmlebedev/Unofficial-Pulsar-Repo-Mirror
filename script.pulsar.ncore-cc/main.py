from pulsar import provider
from urllib import unquote_plus
import xbmcgui
 
import re
import requests

url = provider.ADDON.getSetting('url_address')
icon = provider.ADDON.getAddonInfo('icon')
name_provider = provider.ADDON.getAddonInfo('name') # gets name
language = provider.ADDON.getSetting('language')

xvid_hun = 'xvid_hun' if provider.ADDON.getSetting('xvid_hun') == 'true' else ''
xvid = 'xvid' if provider.ADDON.getSetting('xvid') == 'true' else ''
dvd_hun = 'dvd_hun' if provider.ADDON.getSetting('dvd_hun') == 'true' else ''
dvd = 'dvd' if provider.ADDON.getSetting('dvd') == 'true' else ''
dvd9_hun = 'dvd9_hun' if provider.ADDON.getSetting('dvd9_hun') == 'true' else ''
dvd9 = 'dvd9' if provider.ADDON.getSetting('dvd9') == 'true' else ''
hd_hun = 'hd_hun' if provider.ADDON.getSetting('hd_hun') == 'true' else ''
hd = 'hd' if provider.ADDON.getSetting('hd') == 'true' else ''

xvidser_hun = 'xvidser_hun' if provider.ADDON.getSetting('xvidser_hun') == 'true' else ''
xvidser = 'xvidser' if provider.ADDON.getSetting('xvidser') == 'true' else ''
dvdser_hun = 'dvdser_hun' if provider.ADDON.getSetting('dvdser_hun') == 'true' else ''
dvdser = 'dvdser' if provider.ADDON.getSetting('dvdser') == 'true' else ''
hdser_hun = 'hdser_hun' if provider.ADDON.getSetting('hdser_hun') == 'true' else ''
hdser = 'hdser' if provider.ADDON.getSetting('hdser') == 'true' else ''

movie_min_size = float(provider.ADDON.getSetting('movie_min_size'))
movie_max_size = float(provider.ADDON.getSetting('movie_max_size'))
TV_min_size = float(provider.ADDON.getSetting('TV_min_size'))
TV_max_size = float(provider.ADDON.getSetting('TV_max_size'))
max_magnets = int(provider.ADDON.getSetting('max_magnets'))

username = provider.ADDON.getSetting('username')
password = provider.ADDON.getSetting('password')

stream = provider.ADDON.getSetting('stream') == 'true'
download = provider.ADDON.getSetting('download') == 'true'
requestfolder = provider.ADDON.getSetting('requestfolder')

min_size = 0
max_size = 10
session = requests.Session()


def login():
  result = False
  if username!="" and password!="":
    payload = {'nev': username, 'pass': password, 'ne_leptessen_ki' : True}
    try:
      response = session.post(url + '/login.php', data = payload)
      provider.log.info('Login response: ' + str(response.status_code))
      response = session.get(url + '/profile.php')
      result = True if 'nCore | '+username+' profilja - Profil box' in response.content else False
      if result == False:
        provider.notify(message='Invalid NCore\'s user credentials', header='ERROR!!', time=5000, image=icon)
    except:
        provider.notify(message='Error loading NCore website', header='ERROR!!', time=5000, image=icon)
  else:
    provider.notify(message='Missing NCore\'s user credentials', header='ERROR!!', time=5000, image=icon)
  return result

def request_download(url):
  if requestfolder == '':
    provider.notify(message='Torrent path is not set', header='ERROR!!', time=5000, image=icon)
  else:
    provider.log.info("Opening: " + url)
    response = session.get(url, stream=True)
    if response.ok:
      filename = requestfolder + response.headers['Content-Disposition'].split('filename=')[1].replace('"','')
      provider.log.info("Saving file: " + filename)
      with open(filename, 'wb') as handle:
        for block in response.iter_content(1024):
          if not block:
            break
          handle.write(block)
      xbmcgui.Dialog().ok('nCore downoad', 'Download will be started shortly')
    else:
      provider.notify(message='Error downloading torrent from NCore website', header='ERROR!!', time=5000, image=icon)
      provider.log.error('>>>>>>>ERROR downloading torrent file<<<<<<<')

def extract_torrents(data, cookies):
  torrentboxs = re.findall('<div class="box_torrent">(.*?)<div class="box_feltolto2">', data, re.DOTALL)
  cont = 0
  provider.log.info("Stream: " + str(stream))
  provider.log.info("Download: " + str(download))
  torrents = []
  if download:
    list = []
    urls = []
  for cm, torrentbox in enumerate(torrentboxs):
    try:
      id = re.findall('konyvjelzo\(\'(.*?)\'\)', torrentbox)[0]
      name = re.findall('<a href="torrents.php(.*?)</a>', torrentbox)[0]
      name = re.findall('title="(.*?)"', name)[0]
      size = re.findall('<div class="box_meret2">(.*?)</div>', torrentbox)[0]
      bytes = int(size.replace(' B', '')) if ' B' in size else int(float(size.replace(' KB', ''))*1024) if ' KB' in size else int(float(size.replace(' MB', ''))*1024*1024) if ' MB' in size else int(float(size.replace(' GB', ''))*1024*1024*1024) if ' GB' in size else 0
      peers = re.findall('&peers=1#peers">(.*?)</a>', torrentbox)
      icon = re.findall('ico/ico_(.*?).gif', torrentbox)[0]
      language = 'hu' if 'hun' in icon else 'en'
      if stream:
        # 'ALL': 0, 'HDTV': 1,'480p': 1,'DVD': 1,'720p': 2 ,'1080p': 3, '3D': 3, "1440p": 4 ,"2K": 5,"4K": 5} #code_resolution steeve
        resolution = 4 if '1440p' in name else 3 if '1080p' in name else 2 if '720p' in name else 1 if 'dvd' in icon else 0
        torrent = {
          "language": language,
          "name": size.replace(' ', '') + ' - ' + name, 
          "peers": int(peers[1]), 
          "resolution": resolution, 
          "seeds": int(peers[0]), 
          "size": bytes, 
          "uri": 'https://ncore.cc/torrents.php?action=download&id=' + id + '|Cookie=' + cookies 
        }
        provider.log.info(torrent)
      if download:
        item = '(' + peers[0] + '|' + peers[1] + ') ' + size.replace(' ', '') + ' [' + language + '] ' + name
        provider.log.info(item)
      min_size = TV_min_size if 'ser' in icon else movie_min_size
      max_size = TV_max_size if 'ser' in icon else movie_max_size
      max_size = 1000 if max_size == 10 else max_size
      bytes /= 1024*1024*1024
      if min_size <= bytes and bytes <= max_size:
        if stream:
          torrents.append(torrent)
        if download:
          list.append(item)
          urls.append('https://ncore.cc/torrents.php?action=download&id=' + id)
        cont+= 1
        if cont == max_magnets: #limit torrents
          break
      else:
        provider.log.info('Skipping torrent because of size limitations')
    except:
      provider.log.error('>>>>>>>ERROR parsing data<<<<<<<')
  provider.log.info('>>>>>>' + str(cont) + ' torrents are found<<<<<<<')
  if download:
    if cont > 0:
      id = xbmcgui.Dialog().select('Download movie', list)
      if id == -1:
        provider.log.info('Download was canceled')
      else:
        request_download(urls[id])
  return torrents

def search(query):
  if login() == True:
    provider.notify(message='Searching: ' + query + '...', header=None, time=1500, image=icon)
    provider.log.info('Searching for ' + query)
    url_search = "%s/torrents.php?miszerint=seeders&hogyan=DESC" % (url)
    payload = {'mire': query, 'miben': 'name', 'tipus': 'kivalasztottak_kozott', 'kivalasztott_tipus': xvid_hun + ',' + xvid + ',' + dvd_hun + ',' + dvd + ',' + dvd9_hun + ',' + dvd9 + ',' + hd_hun + ',' + hd + ',' + xvidser_hun + ',' + xvidser + ',' + dvdser_hun + ',' + dvdser + ',' + hdser_hun + ',' + hdser }
    provider.log.info('mire:' + query + ', miben: name, tipus: kivalasztottak_kozott, kivalasztott_tipus:' + xvid_hun + ',' + xvid + ',' + dvd_hun + ',' + dvd + ',' + dvd9_hun + ',' + dvd9 + ',' + hd_hun + ',' + hd + ',' + xvidser_hun + ',' + xvidser + ',' + dvdser_hun + ',' + dvdser + ',' + hdser_hun + ',' + hdser)
    response = session.post(url_search, data = payload)
    if response.status_code != 200:
      provider.notify(message='Error loading search page (' + str(response.status_code) + ')', header='ERROR!!', time=5000, image=icon)
      provider.log.error('Error loading search page (' + str(response.status_code) + ')')
      return []
    else:
      return extract_torrents(response.content, 'PHPSESSID=' + session.cookies['PHPSESSID'] + ';')
  else:
    return []


def search_movie(info):
  global min_size, max_size, xvidser_hun, xvidser, dvdser_hun, dvdser, hdser_hun, hdser
  min_size = movie_min_size
  max_size = movie_max_size
  xvidser_hun = ''
  xvidser = ''
  dvdser_hun = ''
  dvdser = ''
  hdser_hun = ''
  hdser = ''
  query = info['title'] + ' ' + str(info['year']) #define query
  return search(query)

def search_episode(info):
  global min_size, max_size, xvid_hun, xvid, dvd_hun, dvd, dvd9_hun, dvd9, hd_hun, hd
  min_size = TV_min_size
  max_size = TV_max_size
  xvid_hun = ''
  xvid = ''
  dvd_hun = ''
  dvd = ''
  dvd9_hun = ''
  dvd9 = ''
  hd_hun = ''
  hd = ''
  query = info['title'].replace(' s ','s ') + ' S%02dE%02d '% (info['season'],info['episode'])  #define query
  return search(query)

provider.register(search, search_movie, search_episode)
