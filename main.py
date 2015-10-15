import sys
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import re, os, time
from datetime import date, datetime, timedelta
import urllib, urllib2
from urllib2 import URLError, HTTPError
import json
import calendar
import cookielib

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
NO_SPOILERS = str(settings.getSetting(id="no_spoilers"))
SCORE_COLOR = 'FF00B7EB'
GAMETIME_COLOR = 'FFFFFF66'

#Localisation
local_string = xbmcaddon.Addon(id='plugin.video.nhlgcl').getLocalizedString
ROOTDIR = xbmcaddon.Addon(id='plugin.video.nhlgcl').getAddonInfo('path')
ICON = ROOTDIR+"/icon.png"
FANART = ROOTDIR+"/fanart.jpg"

#User Agents
UA_IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12H143 iphone nhl 5.0925'
UA_IPAD = 'Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12H143 ipad nhl 5.0925'
UA_GCL = 'NHL1415/5.0925 CFNetwork/711.4.6 Darwin/14.0.0'
UA_PS3 = 'PS3Application libhttp/4.5.5-000 (CellOS)'
UA_PS4 = 'PS4Application libhttp/1.000 (PS4) libhttp/3.00 (PlayStation 4)'




def categories():                    
    addDir('Today\'s Games','/live',100,ICON,FANART)
    addDir('Enter Date','/date',200,ICON,FANART)      

def todaysGames(game_day):
    print "GAME DAY = " + str(game_day)        
    day = stringToDate(game_day, "%Y-%m-%d")
    d = day - timedelta(days=1)
    addDir('[B]<< Previous Day[/B]','/live',101,ICON,FANART,d.strftime("%Y-%m-%d"))

    date_display = '[B]'+ colorString(day.strftime("%A, %m/%d/%Y"),GAMETIME_COLOR)+'[/B]'
    addDir(date_display,'/nothing',999,ICON,FANART)
        
    url = 'http://f.nhl.com/livescores/nhl/leagueapp/20142015/scores/'+game_day+'_O1T1.json'
    req = urllib2.Request(url)    
    req.add_header('Connection', 'keep-alive')
    req.add_header('Accept', '*/*')
    req.add_header('User-Agent', UA_IPAD)
    req.add_header('Accept-Language', 'en-us')
    req.add_header('Accept-Encoding', 'gzip, deflate')

    try:    
        response = urllib2.urlopen(req)    
        json_source = json.load(response)                           
        response.close()                
    except HTTPError as e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code          
        sys.exit()

    for game in json_source['games']:
        away = game['gameInformation']['awayTeam']
        home = game['gameInformation']['homeTeam']
        #http://nhl.cdn.neulion.net/u/nhlgc_roku/images/HD/NJD_at_BOS.jpg
        #icon = 'http://nhl.cdn.neulion.net/u/nhlgc_roku/images/HD/'+away['teamAbb']+'_at_'+home['teamAbb']+'.jpg'

        away_city = away['teamCity']
        home_city = home['teamCity']        
        away_score = colorString(str(away['teamScore']),SCORE_COLOR)
        home_score = colorString(str(home['teamScore']),SCORE_COLOR)

        game_time = ''
        if game['gameInformation']['currentGameTime'] != ' ':
            game_time = game['gameInformation']['currentGameTime']
        else:
            game_time = game['gameInformation']['easternGameTime']
            game_time = stringToDate(game_time, "%Y/%m/%d %H:%M:%S")
            print game_time
            game_time = game_time.strftime('%I:%M %p').lstrip('0')

        game_time = colorString(game_time,GAMETIME_COLOR) 
               
        game_id = str(game['id'])

        '''
        "gameLiveVideo": {
        "hasLiveAwayVideo": true,
        "hasLiveBroadcastVideo": false,
        "hasLiveCam1Video": false,
        "hasLiveCam2Video": false,
        "hasLiveFrenchVideo": false,
        "hasLiveHomeVideo": true,
        "hasLivePostgameVideo": false,
        "hasLivePregameVideo": false,
        "hasLiveRogersCam1Video": false,
        "hasLiveRogersCam2Video": false,
        "hasLiveRogersCam3Video": false
        '''
        live_video = game['gameLiveVideo']
        live_feeds = 0
        try:
            if int(live_video['hasLiveHomeVideo']):
                home_feed = str(int(live_video['hasLiveHomeVideo']))
                away_feed = str(int(live_video['hasLiveAwayVideo']))
                french_feed = str(int(live_video['hasLiveFrenchVideo']))
                goalie_cam_1 = str(int(live_video['hasLiveCam1Video']))
                goalie_cam_2 = str(int(live_video['hasLiveCam2Video']))                
                live_feeds = home_feed+away_feed+french_feed+goalie_cam_1+goalie_cam_2
        except:
            pass


        archive_video = game['gameHighlightVideo']
        archive_feeds = 0
        if len(archive_video) > 0:
            home_feed = str(int(archive_video['hasArchiveHomeVideo']))
            away_feed = str(int(archive_video['hasArchiveAwayVideo']))
            french_feed = str(int(archive_video['hasArchiveFrenchVideo']))        
            archive_feeds = home_feed+away_feed+french_feed

        if NO_SPOILERS == 'true':
            name = away_city + ' at ' + home_city
        else:
            name = game_time + ' '+ away_city + ' ' + away_score + ' at ' + home_city + ' ' + home_score

        name = name.encode('utf-8')
        
        title = away_city + ' at ' + home_city
        title = title.encode('utf-8')
        
        addStream(name,'',title,game_id,live_feeds,archive_feeds)

    
    d = day + timedelta(days=1)
    addDir('[B]Next Day >>[/B]','/live',101,ICON,FANART,d.strftime("%Y-%m-%d"))


def publishPoint(game_id,ft,gs):    
    #---------------------
    # ft key
    #---------------------
    # 1 = Broadcast
    # 2 = Home
    # 4 = Away
    # 8 = French
    # 16 = NBC
    # 64 = Goalie Cam 1
    # 128 = Goalie Cam 2
    # 256 = Rogers Cam 1
    # 512 = Rogers Cam 1
    # 1024 = Rogers Cam 1
    # 2048 = PreGame Press Conference
    # 4096 = PostGame Press Conference
    #---------------------

    #---------------------
    # gs key
    #---------------------
    # live 
    # dvr    
    #---------------------

    #token = epoch time (in milliseconds) + "." + token???

    cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp')) 
    try:
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
    except:
        pass
       
    url = 'http://gamecenter.nhl.com/nhlgc/servlets/publishpoint'        
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))    
    opener.addheaders = [ ("Accept", "application/x-www-form-urlencoded"),
                        ("Accept-Encoding", "gzip, deflate"),
                        ("Accept-Language", "en-us"),
                        ("Content-Type", "application/x-www-form-urlencoded"),                        
                        ("Connection", "keep-alive"),
                        ("User-Agent", UA_PS4)]

    #8da5fde&id=2015020014&nt=1&type=game&gs=dvr&ft=2
    
    game_data = urllib.urlencode({'id' : game_id,
                                   'nt' : '1',  
                                   'type' : 'game',                                   
                                   'gs' : gs,
                                   'ft' : ft    
                                   })

    try:
        response = opener.open(url, game_data)
    except HTTPError as e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code       
        
        #Error 401 for invalid cookies
        if e.code == 401:
            #Remove cookies file and attempt to login and try again
            cj.clear()
            login()
            try:
                cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp')) 
                cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
                opener.addheaders = [ ("Accept", "application/x-www-form-urlencoded"),
                        ("Accept-Encoding", "gzip, deflate"),
                        ("Accept-Language", "en-us"),
                        ("Content-Type", "application/x-www-form-urlencoded"),                        
                        ("Connection", "keep-alive"),
                        ("User-Agent", UA_PS3)]
                response = opener.open(url, game_data)
                stream_data = response.read()
                response.close()

                stream_url = find(stream_data,'![CDATA[',']]')
                print stream_url
                return stream_url
            except:       
                #alert user that credentials may not be correct         
                msg = "Please make sure that your username and password are correct."
                dialog = xbmcgui.Dialog() 
                ok = dialog.ok('Invalid Login', msg)
                
        elif e.code == 403:
            #Error 403 for blacked out games
            msg = "This game was broadcast on television in your area and is not available to view at this time. Please check back after 48 hours."
            dialog = xbmcgui.Dialog() 
            ok = dialog.ok('Game Blacked Out', msg)            

    except URLError as e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
        sys.exit()
    else:
        #everything's fine 
        stream_data = response.read()
        response.close()

        stream_url = find(stream_data,'![CDATA[',']]')
        print stream_url
        return stream_url
    


def login():    
    #Check if username and password are provided
    global USERNAME
    if USERNAME == '':        
        dialog = xbmcgui.Dialog()
        USERNAME = dialog.input('Please enter your username', type=xbmcgui.INPUT_ALPHANUM)        
        settings.setSetting(id='username', value=USERNAME)

    global PASSWORD
    if PASSWORD == '':        
        dialog = xbmcgui.Dialog()
        PASSWORD = dialog.input('Please enter your password', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
        settings.setSetting(id='password', value=PASSWORD)

    if USERNAME != '' and PASSWORD != '':
        cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))    
        url = 'https://gamecenter.nhl.com/nhlgc/secure/login'        
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))    
        opener.addheaders = [ ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                            ("Accept-Encoding", "gzip, deflate"),
                            ("Accept-Language", "en-us"),
                            ("Content-Type", "application/x-www-form-urlencoded; charset=utf-8"),
                            ("Proxy-Connection", "keep-alive"),
                            ("Connection", "close"),
                            ("User-Agent", UA_IPAD)]

        
        login_data = {'username' : USERNAME,
                       'password' : PASSWORD                   
                       #'deviceid' : '########-DAF3-43DE-B7B8-############',
                       #'devicename' : 'iPhone',
                       #'devicetype' : '7'    
                       }
        if ROGERS_SUBSCRIBER == 'true':
            login_data['rogers'] = 'true'
        
        login_data = urllib.urlencode(login_data)                                   
        response = opener.open(url, login_data)
        #json_source = json.load(response)    
        user_data = response.read()
        response.close()
        token = find(user_data,'token><![CDATA[',']]')

        #Save token to file for         
        #fname = os.path.join(ADDON_PATH_PROFILE, 'token')               
        #device_file = open(fname,'w')   
        #device_file.write(token)
        #device_file.close()

        cj.save(ignore_discard=True); 

def checkLogin():
    expired_cookies = True
    try:
        cj = cookielib.LWPCookieJar()
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
        at_least_one_expired = False
        for cookie in cj:                
            #if cookie.name == 'gcsub':
            print cookie.name
            print cookie.expires
            print cookie.is_expired()
            if cookie.is_expired():
                at_least_one_expired = True
                break

        if not at_least_one_expired:
            expired_cookies = False
            
    except:
        pass
    
    if expired_cookies:
        login()

def streamSelect(live_feeds,archive_feeds):
    print live_feeds
    print archive_feeds
    stream_title = []
    ft = []
    
    if int(live_feeds) > 1:
        gs = 'live'
        if live_feeds[0] == "1":
            stream_title.append('Home')
            ft.append('2')
        if live_feeds[1] == "1":
            stream_title.append('Away')
            ft.append('4')
        if live_feeds[2] == "1":
            stream_title.append('French')
            ft.append('8')  
        #if live_feeds[3] == "1":
        stream_title.append('Goalie Cam 1')
        ft.append('64')
        #if live_feeds[4] == "1":
        stream_title.append('Goalie Cam 2')
        ft.append('128')
    elif int(archive_feeds) > 1:
        gs = 'dvr'
        if archive_feeds[0] == "1":
            stream_title.append('Home')
            ft.append('2')
        if archive_feeds[1] == "1":
            stream_title.append('Away')
            ft.append('4')
        if archive_feeds[2] == "1":
            stream_title.append('French')
            ft.append('8')
    else:
        msg = "No playable streams found."
        dialog = xbmcgui.Dialog() 
        ok = dialog.ok('Streams Not Found', msg)
        sys.exit()

  
    dialog = xbmcgui.Dialog() 
    n = dialog.select('Choose Stream', stream_title)    
    if n > -1:
        #Even though cookies haven't expired some calls won't run unless the cookies are fairly new???
        #Login checking is now done at the publishpoint. If error 401 is received a login is submitted and the stream url is requested again
        #checkLogin()
        stream_url = publishPoint(game_id,ft[n],gs)

        if stream_url != None:
            print "STREAM URL: "+stream_url
            #SD (800 kbps)|SD (1600 kbps)|HD (3000 kbps)|HD (5000 kbps)        
            bndwth = find(QUALITY,'(',' kbps)')

            #Don't replace quality for goalie cams or if 5000 kbps is selected
            #The best quality will be selected by default (1600 kbps for goalie cams | 4500 kbps for French feeds)
            if ft[n] != '64' and ft[n] != '128' and bndwth != '5000':
                stream_url = stream_url.replace('_hd_ced.m3u8', '_hd_'+bndwth+'_ced.m3u8')    

            #Add user-agent to stream
            stream_url = stream_url + '|User-Agent='+UA_GCL

            listitem = xbmcgui.ListItem(path=stream_url)
            xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
        else:
            sys.exit()
    else:
        sys.exit()


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



def addStream(name,link_url,title,game_id,live_feeds,archive_feeds,icon=None,fanart=None,info=None):
    ok=True
    u=sys.argv[0]+"?url="+urllib.quote_plus(link_url)+"&mode="+str(104)+"&name="+urllib.quote_plus(name)+"&game_id="+urllib.quote_plus(str(game_id))+"&live_feeds="+urllib.quote_plus(str(live_feeds))+"&archive_feeds="+urllib.quote_plus(str(archive_feeds))
    
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
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    xbmcplugin.setContent(addon_handle, 'episodes')
    
    return ok

def addLink(name,url,title,iconimage,fanart=None):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)    
    liz.setProperty("IsPlayable", "true")
    liz.setInfo( type="Video", infoLabels={ "Title": title } )
    if iconimage != None:
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage) 
    else:
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=ICON) 

    if fanart != None:
        liz.setProperty('fanart_image', fanart)
    else:
        liz.setProperty('fanart_image', FANART)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok


def addDir(name,url,mode,iconimage,fanart=None,game_day=None):       
    ok=True
    
    if game_day == None:
        #Set day to today in none given
        game_day = time.strftime("%Y-%m-%d")

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

params=get_params()
url=None
name=None
mode=None
game_day=None
game_id=None
live_feeds=None
archive_feeds=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass
try:
    game_day=urllib.unquote_plus(params["game_day"])
except:
    pass
try:
    game_id=urllib.unquote_plus(params["game_id"])
except:
    pass
try:
    live_feeds=urllib.unquote_plus(params["live_feeds"])
except:
    pass
try:
    archive_feeds=urllib.unquote_plus(params["archive_feeds"])
except:
    pass

print "Mode: "+str(mode)
#print "URL: "+str(url)
print "Name: "+str(name)



if mode==None or url==None:        
    categories()  
elif mode == 100:
    todaysGames(game_day)    
elif mode == 101:
    #Used to overwrite current Today's Game list
    todaysGames(game_day)    
elif mode == 104:
    streamSelect(live_feeds,archive_feeds)
elif mode == 200:
    search_txt = ''
    dialog = xbmcgui.Dialog()
    game_day = dialog.input('Enter date (yyyy-mm-dd)', type=xbmcgui.INPUT_ALPHANUM)
    print game_day
    mat=re.match('(\d{4})-(\d{2})-(\d{2})$', game_day)
    if mat is not None:    
        todaysGames(game_day)
    else:
        msg = "The date entered is not in the format required."
        dialog = xbmcgui.Dialog() 
        ok = dialog.ok('Invalid Date', msg)
        sys.exit()
elif mode == 999:
    sys.exit()


if mode == 100:
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
elif mode == 101:
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False, updateListing=True)
else:
    xbmcplugin.endOfDirectory(addon_handle)
    