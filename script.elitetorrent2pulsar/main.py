# coding: utf-8
import re
import tools
from urllib import quote_plus

# this read the settings
settings = tools.Settings(show=False)
# define the browser
browser = tools.Browser()
ret =settings.dialog.select('Opcion:', ['Estrenos', 'Peliculas', 'Peliculas HDRip','SALIR'])
if ret == 0:  # Estrenos
    url_search = url_search = '%s/categoria/1/estrenos/modo:listado/pag:' % settings.url_address
if ret == 1:  # Peliculas
    url_search = url_search = '%s/categoria/2/peliculas/modo:listado/pag:' % settings.url_address
if ret == 2:  # Peliculas HDRip
    url_search = url_search = '%s/categoria/13/peliculas-hdrip/modo:listado/pag:' % settings.url_address
if ret!= 3:
    title = []
    magnet = []
    if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...', settings.icon, settings.time_noti)
    for page in range(1, 6):
        settings.log('[%s] %s%d' % (settings.name_provider_clean, url_search, page))
        if browser.open(url_search + str(page)):
            data = browser.content
            for (torrent, name) in re.findall(r'/torrent/(.*?)/(.*?)"', data):
                info = tools.format_title(name)
                title.append(info['title'].replace('-', ' '))
                magnet.append(settings.url_address + '/get-torrent/' + torrent)  # create torrent to send P
        else:
            settings.log('[%s] >>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
            settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
            break
    if len(title) > 0:
        tools.integration(filename=title, magnet=magnet, type_list='MOVIE', folder=settings.movie_folder,
                          name_provider=settings.name_provider)
del settings
del browser