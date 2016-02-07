import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import urllib, urllib2
import cookielib
import os


ADDON = xbmcaddon.Addon(id='plugin.video.nhlgcl')
ADDON_PATH_PROFILE = xbmc.translatePath(ADDON.getAddonInfo('profile'))
UA_PC = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'
ROOTDIR = xbmcaddon.Addon(id='plugin.video.nhlgcl').getAddonInfo('path')

#Images
ICON = ROOTDIR+"/icon.png"

#Delete sessionKey
try:
    fname = os.path.join(ADDON_PATH_PROFILE, 'sessionKey.txt')
    os.remove(fname)
except:
    pass

cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))   
try:  
    cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
except:
    pass

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))                
url = 'https://account.nhl.com/ui/rest/logout'

req = urllib2.Request(url, data='',
      headers={"Accept": "*/*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "en-US,en;q=0.8",
                "Content-Type": "application/x-www-form-urlencoded",                            
                "Origin": "https://account.nhl.com/ui/SignOut?lang=en",
                "Connection": "close",
                "User-Agent": UA_PC})

response = opener.open(req)              
user_data = response.read()
response.close()

#clear session cookies since they're no longer valid
cj.clear()
cj.save(ignore_discard=True);

dialog = xbmcgui.Dialog() 
title = "NHL TV" 
dialog.notification(title, 'Logout successfully completed', ICON, 5000, False) 



