#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys,urllib
import xbmcaddon,xbmcplugin,xbmcgui

Config = xbmcaddon.Addon()
dialog = xbmcgui.Dialog()



kb = xbmc.Keyboard('','Ingrese su Magnet Link',False)
kb.doModal()

if (kb.isConfirmed()):
    url = kb.getText()
else:
    sys.exit()
    
if str(url).startswith("magnet"):
    pass
elif url == "":
    dialog.ok('ERROR', 'Debe ingresar un Magnet Link.')
else:
    dialog.ok('ERROR', 'No es un Magnet Link válido.')

    
if str(url).startswith("magnet:"):
    url = urllib.quote_plus(url.encode("utf-8"))
else:
    pass


if Config.getSetting("engine") == '0':
    magnet = "plugin://plugin.video.xbmctorrent/play/" + str(url)
    print "THIS" + str(magnet)
else:
    magnet = "plugin://plugin.video.pulsar/play?uri=" + str(url)


xbmctpath = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.xbmctorrent'))
pulsarpath = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.pulsar'))

if os.path.isdir(xbmctpath) == True and os.path.isdir(pulsarpath) == True:
    pass
elif os.path.isdir(xbmctpath) == False and os.path.isdir(pulsarpath) == False:
    dialog.ok('ERROR', '                                  Para utilizar este add-on,', '             necesita tener instalado XBMCtorrent o Pulsar.')
    sys.exit()
elif os.path.isdir(xbmctpath) == True and os.path.isdir(pulsarpath) == False:
    Config.setSetting("engine", "0")
    magnet = "plugin://plugin.video.xbmctorrent/play/" + str(url)
elif os.path.isdir(xbmctpath) == False and os.path.isdir(pulsarpath) == True:
    Config.setSetting("engine", "1")
    magnet = "plugin://plugin.video.pulsar/play?uri=" + str(url)


xbmc.Player().play(magnet)

sys.exit()

