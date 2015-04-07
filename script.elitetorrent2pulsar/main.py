# coding: utf-8
import re
import tools
from xbmc import sleep


# this read the settings
settings = tools.Settings()
# define the browser
browser = tools.Browser()
options = {'Estrenos': '%s/categoria/1/estrenos/modo:listado/pag:',
           'Peliculas': '%s/categoria/2/peliculas/modo:listado/pag:',
           'Peliculas HDRip': '%s/categoria/13/peliculas-hdrip/modo:listado/pag:',
           'Series':'%s/categoria/4/series/modo:listado/pag:',
           'Series VOSE': '%s/categoria/16/series-vose/modo:listado/pag:' }
list_options = options.keys()
list_options.sort()
ret =settings.dialog.select('Opcion:', list_options + ['-CONFIGURACIÓN', '-AYUDA', 'SALIR'])
if ret < len (options):
    url_search = options[list_options[ret]] % settings.url_address
    title = []
    magnet = []
    if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...', settings.icon, settings.time_noti)
    settings.pages = settings.dialog.numeric(0, 'Number of pages:')
    if settings.pages == '' or settings.pages == 0:
        settings.pages = "1"
    settings.pages = int(settings.pages)
    for page in range(1, settings.pages + 1):
        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Page %s...' %
            page, settings.icon, settings.time_noti)
        settings.log('[%s] %s%d' % (settings.name_provider_clean, url_search, page))
        if browser.open(url_search + str(page)):
            data = browser.content
            for (torrent, name) in re.findall(r'/torrent/(.*?)/(.*?)"', data):
                title.append(name.replace('-', ' '))
                magnet.append(settings.url_address + '/get-torrent/' + torrent)  # create torrent to send P
            if int(page) % 10 == 0: sleep(3000)  # to avoid too many connections
        else:
            settings.log('[%s] >>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
            settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
            break
    if len(title) > 0 and 'Series' not in list_options[ret]:
        tools.integration(filename=title, magnet=magnet, type_list='MOVIE', folder=settings.movie_folder,
                          name_provider=settings.name_provider)
    if len(title) > 0 and 'Series' in list_options[ret]:
        tools.integration(filename=title, magnet=magnet, type_list='SHOW', folder=settings.show_folder,
                          name_provider=settings.name_provider)
if ret == len(options):  # Settings
    settings.settings.openSettings()
    settings = tools.Settings()
if ret == len(options) + 1:  # Help
        settings.dialog.ok("Help", "Please, check this address to find the user's operation:\n[B]http://goo.gl/0b44BY[/B]")
del settings
del browser