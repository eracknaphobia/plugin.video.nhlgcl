# coding=utf-8

import sys
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import re, os, time
from datetime import date, datetime, timedelta
import calendar
import pytz
import urllib, urllib2


addon_handle = int(sys.argv[1])


#Addon Info
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_PATH = xbmc.translatePath(ADDON.getAddonInfo('path'))
ADDON_PATH_PROFILE = xbmc.translatePath(ADDON.getAddonInfo('profile'))
XBMC_VERSION = float(re.findall(r'\d{2}\.\d{1}', xbmc.getInfoLabel("System.BuildVersion"))[0])
LOCAL_STRING = ADDON.getLocalizedString

#Settings
settings = xbmcaddon.Addon(id='plugin.video.nhlgcl')
USERNAME = str(settings.getSetting(id="username"))
PASSWORD = str(settings.getSetting(id="password"))
ROGERS_SUBSCRIBER = str(settings.getSetting(id="rogers"))
QUALITY = str(settings.getSetting(id="quality"))
NO_SPOILERS = settings.getSetting(id="no_spoilers")
FAV_TEAM = str(settings.getSetting(id="fav_team"))
TEAM_NAMES = settings.getSetting(id="team_names")
TIME_FORMAT = settings.getSetting(id="time_format")

#Colors
SCORE_COLOR = 'FF00B7EB'
GAMETIME_COLOR = 'FFFFFF66'
#FAV_TEAM_COLOR = 'FFFF0000'


#Localization
local_string = xbmcaddon.Addon(id='plugin.video.nhlgcl').getLocalizedString
ROOTDIR = xbmcaddon.Addon(id='plugin.video.nhlgcl').getAddonInfo('path')

#Images
ICON = ROOTDIR+"/icon.png"
FANART = ROOTDIR+"/fanart.jpg"
PREV_ICON = ROOTDIR+"/resources/images/prev.png"
NEXT_ICON = ROOTDIR+"/resources/images/next.png"

#User Agents
UA_GCL = 'NHL1415/5.0925 CFNetwork/711.4.6 Darwin/14.0.0'
UA_IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12H143 iphone nhl 5.0925'
UA_IPAD = 'Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12H143 ipad nhl 5.0925'
UA_NHL = 'NHL/2542 CFNetwork/758.2.8 Darwin/15.0.0'
UA_PC = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'
UA_PS3 = 'PS3Application libhttp/4.7.6-000 (CellOS)'
UA_PS4 = 'PS4Application libhttp/1.000 (PS4) libhttp/3.15 (PlayStation 4)'
    

def find(source,start_str,end_str):    
    start = source.find(start_str)
    end = source.find(end_str,start+len(start_str))

    if start != -1:        
        return source[start+len(start_str):end]
    else:
        return ''


def colorString(string, color):
    return '[COLOR='+color+']'+string+'[/COLOR]'


def stringToDate(string, date_format):
    try:
        date = datetime.strptime(str(string), date_format)
    except TypeError:
        date = datetime(*(time.strptime(str(string), date_format)[0:6]))                

    return date


def easternToLocal(eastern_time):
    utc = pytz.utc
    eastern = pytz.timezone('US/Eastern')    
    eastern_time = eastern.localize(eastern_time)
    # Convert it from Eastern to UTC
    utc_time = eastern_time.astimezone(utc)
    timestamp = calendar.timegm(utc_time.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    # Convert it from UTC to local time
    assert utc_time.resolution >= timedelta(microseconds=1)
    return local_dt.replace(microsecond=utc_time.microsecond)

def UTCToLocal(utc_dt):
    # get integer timestamp to avoid precision lost
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    assert utc_dt.resolution >= timedelta(microseconds=1)
    return local_dt.replace(microsecond=utc_dt.microsecond)


def localToEastern():    
    eastern = pytz.timezone('US/Eastern')    
    local_to_utc = datetime.now(pytz.timezone('UTC'))    
    local_to_eastern = local_to_utc.astimezone(eastern).strftime('%Y-%m-%d')
    return local_to_eastern


def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                    params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                    splitparams={}
                    splitparams=pairsofparams[i].split('=')
                    if (len(splitparams))==2:
                            param[splitparams[0]]=splitparams[1]
                            
    return param



def addStream(name,link_url,title,game_id,epg,icon=None,fanart=None,info=None,video_info=None,audio_info=None):
    ok=True
    u=sys.argv[0]+"?url="+urllib.quote_plus(link_url)+"&mode="+str(104)+"&name="+urllib.quote_plus(name)+"&game_id="+urllib.quote_plus(str(game_id))+"&epg="+urllib.quote_plus(str(epg))
    
    if icon != None:
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=icon) 
    else:
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=ICON) 
    
    if fanart != None:
        liz.setProperty('fanart_image', fanart)
    else:
        liz.setProperty('fanart_image', FANART)

    liz.setProperty("IsPlayable", "true")
    liz.setInfo( type="Video", infoLabels={ "Title": title } )
    if info != None:
        liz.setInfo( type="Video", infoLabels=info)
    if video_info != None:
        liz.addStreamInfo('video', video_info)
    if audio_info != None:
        liz.addStreamInfo('audio', audio_info)

    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    xbmcplugin.setContent(addon_handle, 'episodes')
    
    return ok


def addLink(name,url,title,iconimage,info=None,video_info=None,audio_info=None):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)    
    liz.setProperty("IsPlayable", "true")
    liz.setInfo( type="Video", infoLabels={ "Title": title } )
    liz.setProperty('fanart_image', FANART)
    if iconimage != None:
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage) 
    else:
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=ICON) 

    if info != None:
        liz.setInfo( type="Video", infoLabels=info)
    if video_info != None:
        liz.addStreamInfo('video', video_info)
    if audio_info != None:
        liz.addStreamInfo('audio', audio_info)

    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    xbmcplugin.setContent(addon_handle, 'episodes')
    return ok




def addDir(name,url,mode,iconimage,fanart=None,game_day=None):       
    ok=True
    
    if game_day == None:
        #Set day to today if none given
        #game_day = time.strftime("%Y-%m-%d")
        game_day = localToEastern()
        #game_day = '2016-01-27'

    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&icon="+urllib.quote_plus(iconimage)+"&game_day="+urllib.quote_plus(game_day)

    if iconimage != None:
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage) 
    else:
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=ICON) 

    liz.setInfo( type="Video", infoLabels={ "Title": name } )

    if fanart != None:
        liz.setProperty('fanart_image', fanart)
    else:
        liz.setProperty('fanart_image', FANART)


    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)    
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    return ok


def scoreUpdates():
    #s = ScoreThread()
    t = threading.Thread(target = scoringUpdates)
    t.start() 

def getFavTeamColor():
    #Hex code taken from http://teamcolors.arc90.com/    
    team_colors = {"Anaheim":"FF91764B",
                "Arizona":"FF841F27",
                "Boston":"FFFFC422",
                "Buffalo":"FF002E62",
                "Calgary":"FFE03A3E",
                "Carolina":"FFE03A3E",
                "Chicago":"FFE3263A",
                "Colorado":"FF8B2942",
                "Columbus":"FF00285C",
                "Dallas":"FF006A4E",
                "Detroit":"FFEC1F26",
                "Edmonton":"FF003777",
                "Florida":"FFC8213F",
                "Los Angeles":"FFAFB7BA",
                "Minnesota":"FF025736",
                "Montréal":"FFBF2F38",
                "Nashville":"FFFDBB2F",
                "New Jersey":"FFE03A3E",
                "New York Islanders":"FF00529B",
                "New York Rangers":"FF0161AB",
                "Philadelphia":"FFF47940",
                "Pittsburgh":"FFD1BD80",
                "Ottawa":"FFE4173E",
                "San Jose":"FF05535D",
                "St. Louis":"FF0546A0",
                "Tampa Bay":"FF013E7D",
                "Toronto":"FF003777",
                "Vancouver":"FF07346F",
                "Washington":"FFCF132B",
                "Winnipeg":"FF002E62"}
    
    # Default to red
    #fav_team_color = "FFFF0000"                
    #try:
    print FAV_TEAM
    fav_team_color = team_colors[FAV_TEAM]
    print fav_team_color
    #except:
    #pass

    return  fav_team_color

def getAudioVideoInfo():
    #SD (800 kbps)|SD (1600 kbps)|HD (3000 kbps)|HD (5000 kbps)
    if QUALITY == 'SD (800 kbps)':        
        video_info = { 'codec': 'h264', 'width' : 512, 'height' : 288, 'aspect' : 1.78 }        
    elif QUALITY == 'SD (1200 kbps)':
        video_info = { 'codec': 'h264', 'width' : 640, 'height' : 360, 'aspect' : 1.78 }        
    elif QUALITY == 'HD (2500 kbps)' or QUALITY == 'HD (3500 kbps)' or QUALITY == 'HD (5000 kbps)':
        video_info = { 'codec': 'h264', 'width' : 1280, 'height' : 720, 'aspect' : 1.78 }        

    audio_info = { 'codec': 'aac', 'language': 'en', 'channels': 2 }
    return audio_info, video_info

