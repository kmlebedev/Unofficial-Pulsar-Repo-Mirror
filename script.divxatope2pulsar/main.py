# coding: utf-8
import re
import tools
from xbmc import sleep


# this read the settings
settings = tools.Settings()
# define the browser
browser = tools.Browser()
options = {'Estrenos de Cine': '%s/categoria/estrenos/pg/',
           'Peliculas en Alta Definicion': '%s/categoria/peliculas-hd/pg/',
           'Peliculas en 3D': '%s/categoria/peliculas-3d/pg/',
           'Peliculas en Castellano': '%s/categoria/peliculas-castellano/pg/',
           'Peliculas Latino': '%s/categoria/peliculas-latino/pg/'}
ret =settings.dialog.select('Opción:', options.keys() + ['-CONFIGURACIÓN', '-AYUDA', 'SALIR'])
if ret < len(options):
    url_search = options.values()[ret] % settings.url_address
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
            sname = re.findall('<li style="width:136px;height:263px;margin:0px 15px 0px 0px;">(.*?)title="(.*?)"', data,
                               re.S)
            torrent = re.findall(r'/descargar/(.*?)"', data)
            for cm, temp in enumerate(sname):
                name = sname[cm][1].replace('Descargar', '').replace('torrent gratis', '')
                info = tools.format_title(name.title())
                title.append(info['title'])
                magnet.append(settings.url_address + '/torrent/' + torrent[cm])  # create torrent to send P
            if int(page) % 10 == 0: sleep(3000)  # to avoid too many connections
        else:
            settings.log('[%s] >>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
            settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
            break
    if len(title) > 0:
        tools.integration(filename=title, magnet=magnet, type_list='MOVIE', folder=settings.movie_folder,
                          name_provider=settings.name_provider)
if ret == len(options):
    settings.settings.openSettings()
    settings = tools.Settings()
if ret == len(options) + 1:
        settings.dialog.ok("Help", "Please, check this address to find the user's operation:\n[B]http://goo.gl/0b44BY[/B]")
del settings
del browser