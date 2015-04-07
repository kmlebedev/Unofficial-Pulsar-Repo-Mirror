from pulsar import provider

icon = provider.ADDON.getAddonInfo('icon')

def search(query):
	url_search = "http://getstrike.net/api/torrents/search/?q=%s" % (query)
	provider.log.info(url_search)
	response = provider.GET(url_search)
	results=[]
	if str(response.data) != '':
		items = provider.parse_json(response.data)
		nbrTorrents = items[0]['results']
		for torrent in range(0, nbrTorrents):
			hash = items[1][torrent]['torrent_hash']
			name = items[1][torrent]['torrent_title']
			link = items[1][torrent]['download_link']
			magnet = 'magnet:?xt=urn:btih:%s' % (hash)
			results.append({'name': name, 'uri': magnet, 'info_hash': hash})
	return results
		
def search_episode(info):
	title = info['title'].encode('utf-8') + ' S%02dE%02d' % (info['season'],info['episode'])
	provider.notify(message='Searching: ' + title +'...', header=None, time=1500, image=icon)
	return search(title)

def search_movie(info):
	title = info['title'].encode('utf-8') + ' %s' % (info['year'])
	provider.notify(message='Searching: ' + title +'...', header=None, time=1500, image=icon)
	return search(title)

#This registers your module for use
provider.register(search, search_movie, search_episode)