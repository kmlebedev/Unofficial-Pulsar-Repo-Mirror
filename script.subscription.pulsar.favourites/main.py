# coding: utf-8
import subscription
import xml.etree.ElementTree as ET
import re
import time
import xbmc
import json
import os

# this read the settings of add on
settings = subscription.Settings()
path = xbmc.translatePath('special://userdata')
if os.path.exists("%sfavourites.xml" % path):
    tree = ET.parse("%sfavourites.xml" % path)
    root = tree.getroot()

    # check movies
    listing = []
    ID = []
    for child in root:
        data = child.text
        if 'plugin://plugin.video.pulsar/movie/' in data:
            listing.append(child.attrib['name'])
            ID.append(re.search('plugin://plugin.video.pulsar/movie/(.*?)/', data).group(1))
    if len(listing) > 0:
        subscription.integration(listing, ID,'MOVIE', settings.movie_folder, True, name_provider=settings.name_provider, message='Single Movie List')

    # check movies sections
    cont = 0
    listing = []
    ID = []
    browser = subscription.Browser()
    for child in root:
        data = child.text.replace('"plugin://plugin.video.pulsar/movies/"', '')  # remove movies root
        if 'plugin://plugin.video.pulsar/movies/' in data:
            section = re.search('plugin://plugin.video.pulsar/movies/(.*?)"', data).group(1)
            # get the list of movies
            time.sleep(0.002)
            browser.open('http://localhost:65251/movies/%s' % section)
            data = json.loads(browser.content)
            for item in data['items']:
                if 'title' in item['info'] and item['info'].has_key('code'):
                    listing.append(item['info']['title'].encode('ascii', 'ignore') + ' (' + str(item['info']['year']) + ')')
                    ID.append(item['info']['code'])
                cont += 1
                if cont >= settings.number_files:  # limitation of number
                    break
    del browser
    if len(listing) > 0:
        subscription.integration(listing, ID,'MOVIE', settings.movie_folder, True, name_provider=settings.name_provider, message='Pulsar Movies Section')

    # check tv shows
    listing = []
    ID = []
    for child in root:
        data = child.text
        name = child.attrib['name']
        if 'plugin://plugin.video.pulsar/show/' in data and 'Season ' not in name:
            listing.append(name)
            ID.append(re.search('plugin://plugin.video.pulsar/show/(.*?)/', data).group(1))
    if len(listing) > 0:
        subscription.integration(listing, ID,'SHOW', settings.show_folder, True, name_provider=settings.name_provider, message='Single TV Shows List')
else:
    if time_noti > 0: settings.dialog.notification(settings.name_provider, 'Not Favourites!', settings.icon, settings.time_noti)

	
#other addons
#xbmc.executebuiltin('XBMC.Runaddon(script.subscription.pulsar.trakt)')
	
#clear memory
del settings