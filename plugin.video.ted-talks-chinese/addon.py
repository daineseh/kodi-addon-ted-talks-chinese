#-*- coding: utf-8 -*-
import sys
import urllib
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import youtube_dl

from clawler import TedParser


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def page_number(url):
    return url.split('=')[-1].split('.')[0]

mode = args.get('mode', None)

if mode is None:
    obj = TedParser()
    for talk in obj.get_talks():
        url = build_url({'mode': 'play', 'folder_name': talk.url})
        li = xbmcgui.ListItem("%s - %s" % (talk.title, talk.speaker))
        li.setArt({'thumb': talk.thumb, 'icon': talk.thumb, 'fanart': talk.thumb})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)

    li = xbmcgui.ListItem('')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=None, listitem=li, isFolder=False)

    url = build_url({'mode': 'page', 'folder_name': obj.next_page})
    li = xbmcgui.ListItem("Next Page (%s)" % page_number(obj.next_page))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'page':
    page_url = args['folder_name'][0]
    obj = TedParser(page_url)

    for talk in obj.get_talks():
        url = build_url({'mode': 'play', 'folder_name': talk.url})
        li = xbmcgui.ListItem("%s - %s" % (talk.title, talk.speaker))
        li.setArt({'thumb': talk.thumb, 'icon': talk.thumb, 'fanart': talk.thumb})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    if obj.next_page:
        li = xbmcgui.ListItem('')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=None, listitem=li, isFolder=False)

        url = build_url({'mode': 'page', 'folder_name': obj.next_page})
        li = xbmcgui.ListItem("Next Page (%s)" % page_number(obj.next_page))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    if obj.last_page:
        url = build_url({'mode': 'page', 'folder_name': obj.last_page})
        li = xbmcgui.ListItem("Last Page (%s)" % page_number(obj.last_page))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'play':
    url = args['folder_name'][0]
    opts = {
        'forceurl': True,
        'quiet': True,
        'simulate': True,
    }

    with youtube_dl.YoutubeDL(opts) as ydl:
        resource_uri = ydl.extract_info(url).get('url')
        if not resource_uri:
            entries = ydl.extract_info(url).get('entries')
            resource_uri = entries[-1].get('url')
    xbmc.Player().play(resource_uri)
