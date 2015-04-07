#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import xbmcaddon,xbmcplugin,xbmcgui
import shutil


Config = xbmcaddon.Addon()

dialog = xbmcgui.Dialog()

addondir = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.xbmctorrentmod/'))
addonsdir = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.xbmctorrent/'))

moddirsc = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.xbmctorrentmod/mods/'))
moddirxt = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.xbmctorrent/resources/site-packages/xbmctorrent/scrapers/mods/'))

indexmod = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.xbmctorrent/resources/site-packages/xbmctorrent/scrapers/mods/', 'index_mod.py'))
index_xt = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.xbmctorrent/resources/site-packages/xbmctorrent/', 'index.py'))
index_bk = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.xbmctorrent/resources/site-packages/xbmctorrent/scrapers/mods/', 'index.py'))

if os.path.isdir(addonsdir) == True and Config.getSetting("state") != "done":
    try:
        shutil.copytree(moddirsc, moddirxt)
    except:
        pass

    shutil.copy(indexmod, index_xt)
    Config.setSetting("state","done")
    dialog.ok("DONE", "Now you have modified scrapers!")
elif os.path.isdir(addonsdir) == True and Config.getSetting("state") == "done":
    shutil.copy(index_bk, index_xt)
    Config.setSetting("state","")
    dialog.ok("DONE", "REVERTED.")
else:
    dialog.ok("ERROR", "Looks like you have not XBMCtorrent.")
    sys.exit()
    
