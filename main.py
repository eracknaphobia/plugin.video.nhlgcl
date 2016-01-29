import sys
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import re, os, time
from datetime import date, datetime, timedelta
import urllib, urllib2
from urllib2 import URLError, HTTPError
import json
import cookielib
from resources.lib.globals import *


def categories():    
    localToEastern()

    addDir('Today\'s Games','/live',100,ICON,FANART)
    addDir('Goto Date','/date',200,ICON,FANART)
    addDir('Quick Picks','/qp',300,ICON,FANART)  
        

def todaysGames(game_day):
    print "GAME DAY = " + str(game_day)        
    display_day = stringToDate(game_day, "%Y-%m-%d")            
    prev_day = display_day - timedelta(days=1)                

    addDir('[B]<< Previous Day[/B]','/live',101,PREV_ICON,FANART,prev_day.strftime("%Y-%m-%d"))

    date_display = '[B][I]'+ colorString(display_day.strftime("%A, %m/%d/%Y"),GAMETIME_COLOR)+'[/I][/B]'
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
        createGameStream(game)
    
    next_day = display_day + timedelta(days=1)
    addDir('[B]Next Day >>[/B]','/live',101,NEXT_ICON,FANART,next_day.strftime("%Y-%m-%d"))


def createGameStream(game):
    away = game['gameInformation']['awayTeam']
    home = game['gameInformation']['homeTeam']
    #http://nhl.cdn.neulion.net/u/nhlgc_roku/images/HD/NJD_at_BOS.jpg
    #icon = 'http://nhl.cdn.neulion.net/u/nhlgc_roku/images/HD/'+away['teamAbb']+'_at_'+home['teamAbb']+'.jpg'
    icon = 'http://raw.githubusercontent.com/eracknaphobia/game_images/master/square_black/'+away['teamAbb']+'vs'+home['teamAbb']+'.png'

    if TEAM_NAMES == "0":
        away_team = away['teamCity']
        home_team = home['teamCity']
    elif TEAM_NAMES == "1":
        away_team = away['teamName']
        home_team = home['teamName']
    elif TEAM_NAMES == "2":
        away_team = away['teamCity'] + " " + away['teamName']
        home_team = home['teamCity'] + " " + home['teamName']
    elif TEAM_NAMES == "3":
        away_team = away['teamAbb']
        home_team = home['teamAbb']


    if away_team == "New York":
        away_team = away_team + " " + away['teamName']

    if home_team == "New York":
        home_team = home_team + " " + home['teamName']


    fav_game = False
    if away['teamCity'].encode('utf-8') == FAV_TEAM or away['teamCity'] + " " + away['teamName'].encode('utf-8') == FAV_TEAM:
        fav_game = True
        away_team = colorString(away_team,getFavTeamColor())           
    
    if home['teamCity'].encode('utf-8') == FAV_TEAM or home['teamCity'] + " " + home['teamName'].encode('utf-8') == FAV_TEAM:
        fav_game = True
        home_team = colorString(home_team,getFavTeamColor())


    game_time = ''
    if game['gameInformation']['currentGameTime'] != ' ':
        game_time = game['gameInformation']['currentGameTime']
        if NO_SPOILERS == '1' and game_time[:5] == "FINAL":
             game_time = game_time[:5]
        elif NO_SPOILERS == '2' and game_time[:5] == "FINAL":
             if fav_game:
                  game_time = game_time[:5]
    else:            
        game_time = game['gameInformation']['easternGameTime']            
        game_time = stringToDate(game_time, "%Y/%m/%d %H:%M:%S")
        game_time = easternToLocal(game_time)
       
        if TIME_FORMAT == '0':
             game_time = game_time.strftime('%I:%M %p').lstrip('0')
        else:
             game_time = game_time.strftime('%H:%M')

    game_time = colorString(game_time,GAMETIME_COLOR)            
    game_id = str(game['id'])


    live_video = game['gameLiveVideo']
    live_feeds = 0
    try:
        if int(live_video['hasLiveHomeVideo']):           

            if bool(live_video['hasLiveBroadcastVideo']):
                live_feeds += 1

            if bool(live_video['hasLiveAwayVideo']):
                live_feeds += 2

            if bool(live_video['hasLiveHomeVideo']):
                live_feeds += 4

            if bool(live_video['hasLiveFrenchVideo']):
                live_feeds += 8

            #-----------------------------
            #Always add Goalie Cams
            #-----------------------------
            #if bool(live_video['hasLiveCam1Video']):
            live_feeds += 64

            #if bool(live_video['hasLiveCam2Video']):
            live_feeds += 128
            #-----------------------------

            if bool(live_video['hasLiveRogersCam1Video']):
                live_feeds += 256

            if bool(live_video['hasLiveRogersCam2Video']):
                live_feeds += 512

            if bool(live_video['hasLiveRogersCam1Video']):
                live_feeds += 1024

            if bool(live_video['hasLivePregameVideo']):
                live_feeds += 2048

            if bool(live_video['hasLivePostgameVideo']):
                live_feeds += 4096
    except:
        pass

    archive_video = game['gameHighlightVideo']
    archive_feeds = 0
    if len(archive_video) > 0:

        if bool(archive_video['hasArchiveAwayVideo']):
                archive_feeds += 2

        if bool(archive_video['hasArchiveHomeVideo']):
            archive_feeds += 4

        #For some reason the live french stream is set to true when the game has a french archive stream            
        if bool(archive_video['hasArchiveFrenchVideo']) or bool(live_video['hasLiveFrenchVideo']):
            archive_feeds += 8


    if NO_SPOILERS == '1':
        name = game_time + ' ' + away_team + ' at ' + home_team
    elif NO_SPOILERS == '2' and fav_game:            
        name = game_time + ' ' + away_team + ' at ' + home_team
    else:
        name = game_time + ' ' + away_team + ' ' + colorString(str(away['teamScore']),SCORE_COLOR) + ' at ' + home_team + ' ' + colorString(str(home['teamScore']),SCORE_COLOR) 


    name = name.encode('utf-8')
    if fav_game:
        name = '[B]'+name+'[/B]'
    
    title = away_team + ' at ' + home_team
    title = title.encode('utf-8')
    
    #Set audio/video info based on stream quality setting
    audio_info, video_info = getAudioVideoInfo()
    addStream(name,'',title,game_id,live_feeds,archive_feeds,icon,None,None,video_info,audio_info)


def publishPoint(game_id,ft,gs):    
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
            #Clear cookies and attempt to login and try again
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
                        ("User-Agent", UA_PS4)]
                response = opener.open(url, game_data)
                stream_data = response.read()
                response.close()

                stream_url = find(stream_data,'![CDATA[',']]')
                print stream_url
                return stream_url
            except HTTPError as e:
                if e.code == 401:      
                    #alert user that credentials may not be correct         
                    msg = "Please make sure that your username and password are correct."
                    dialog = xbmcgui.Dialog() 
                    ok = dialog.ok('Invalid Login', msg)
                elif e.code == 403:
                    #Error 403 for blacked out games
                    msg = "This game was broadcast on television in your area and is not available to view at this time. Please check back after 48 hours."
                    dialog = xbmcgui.Dialog() 
                    ok = dialog.ok('Game Blacked Out', msg)            
                
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
        user_data = response.read()
        response.close()
        token = find(user_data,'token><![CDATA[',']]')

        #Save token to file for calls       
        #fname = os.path.join(ADDON_PATH_PROFILE, 'token')               
        #device_file = open(fname,'w')   
        #device_file.write(token)
        #device_file.close()

        cj.save(ignore_discard=True); 



def streamSelect(live_feeds,archive_feeds):
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
    # 512 = Rogers Cam 2
    # 1024 = Rogers Cam 3
    # 2048 = PreGame Press Conference
    # 4096 = PostGame Press Conference
    #---------------------

    #---------------------
    # gs key
    #---------------------
    # live 
    # dvr
    # archive 
    # condensed
    # highlights
    #---------------------
    print live_feeds
    print archive_feeds
    stream_title = []
    ft = []
    archive_type = ['Full Game','Condensed','Highlights']
    #archive_gs = ['dvr','condensed','highlights']
    archive_gs = ['archive','condensed','highlights']
    
    #Live Feeds    
    if int(live_feeds) > 1:
        gs = 'live'
        if live_feeds >= 4096:
            stream_title.append('Post-Game Press Conference')
            ft.append('4096')
            live_feeds -= 4096

        if live_feeds >= 2048:
            stream_title.append('Pre-Game Press Conference')
            ft.append('2048')
            live_feeds -= 2048

        if live_feeds >= 1024:
            stream_title.append('Rogers Cam 3')
            ft.append('1024')
            live_feeds -= 1024
            
        if live_feeds >= 512:
            stream_title.append('Rogers Cam 2')
            ft.append('512')
            live_feeds -= 512

        if live_feeds >= 256:
            stream_title.append('Rogers Cam 1')
            ft.append('256')
            live_feeds -= 256
            
        if live_feeds >= 128:
            stream_title.append('Goalie Cam 2')
            ft.append('128')
            live_feeds -= 128

        if live_feeds >= 64:
            stream_title.append('Goalie Cam 1')
            ft.append('64')
            live_feeds -= 64

        if live_feeds >= 8:
            stream_title.append('French')
            ft.append('8')
            live_feeds -= 8

        if live_feeds >= 4:
            stream_title.append('Away')
            ft.append('4')
            live_feeds -= 4
            
        if live_feeds >= 2:
            stream_title.append('Home')
            ft.append('2')
            live_feeds -= 2

        if live_feeds >= 1:
            stream_title.append('NBC')
            ft.append('1')            
       
    # Archive Feeds
    elif archive_feeds > 1:       
        dialog = xbmcgui.Dialog()          
        n = dialog.select('Choose Archive', archive_type)
        if n == -1:
            sys.exit()

        gs = archive_gs[n] 

        if archive_feeds >= 8:
            stream_title.append('French')
            ft.append('8')
            archive_feeds -= 8

        if archive_feeds >= 4:
            stream_title.append('Away')
            ft.append('4')
            archive_feeds -= 4
            
        if archive_feeds >= 2:
            stream_title.append('Home')
            ft.append('2')
        
    else:
        msg = "No playable streams found."
        dialog = xbmcgui.Dialog() 
        ok = dialog.ok('Streams Not Found', msg)
        sys.exit()

    
    #Reverse Order for display purposes
    stream_title.reverse()
    ft.reverse()

    n = -1
    is_highlights = 0
    if gs != 'highlights':
        dialog = xbmcgui.Dialog() 
        n = dialog.select('Choose Stream', stream_title)  
    else:
        #Make home stream
        is_highlights = 1
        gs = 'condensed'
        n = 0

    if n > -1:
        #Even though cookies haven't expired some calls won't run unless the cookies are fairly new???
        #Login checking is now done at the publishpoint. If error 401 is received a login is submitted and the stream url is requested again
        stream_url = publishPoint(game_id,ft[n],gs)
        
        if stream_url != None:
            #SD (800 kbps)|SD (1600 kbps)|HD (3000 kbps)|HD (5000 kbps)        
            bandwidth = find(QUALITY,'(',' kbps)')

            #Don't replace quality for special camera angles (64 and up) if quality is greater than 1600
            #The best quality will be selected by default (ex. 1600 kbps for goalie cams)            
            if int(ft[n]) < 64 or int(bandwidth) < 1600:
                stream_url = stream_url.replace('_hd_ced.m3u8', '_hd_'+bandwidth+'_ced.m3u8')    
                stream_url = stream_url.replace('whole_1_ced.mp4', 'whole_1_'+bandwidth+'_ced.mp4')
                stream_url = stream_url.replace('_condensed_1_ced.mp4', '_condensed_1_'+bandwidth+'_ced.mp4')

            if is_highlights:
                stream_url = stream_url.replace('_condensed_1_ced.mp4.m3u8', '_continuous_1_1600.mp4')

            '''            
            Print manifest contents to kodi log
            cookies = ''
            cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp')) 
            cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
            for cookie in cj:                            
                cookies = cookies + cookie.name + "=" + cookie.value + "; "
            req = urllib2.Request(stream_url)    
            req.add_header('Connection', 'keep-alive')
            req.add_header('Accept', '*/*')
            req.add_header('User-Agent', UA_IPAD)
            req.add_header('Accept-Language', 'en-us')
            req.add_header('Accept-Encoding', 'gzip, deflate')
            req.add_header('Cookie', cookies)
            response = urllib2.urlopen(req)
            print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
            print response.read()
            print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
            response.close()
            '''

            #Add user-agent to stream
            stream_url = stream_url + '|User-Agent='+UA_IPAD

            print "STREAM URL: "+stream_url

            listitem = xbmcgui.ListItem(path=stream_url)
            xbmcplugin.setResolvedUrl(addon_handle, True, listitem)            
        else:
            sys.exit()
    else:
        sys.exit()


def quickPicks():    
    url = 'http://smb.cdnak.neulion.com/fs/nhl/mobile/feed_new/data/catvideo/xbox/nhl_0.json'
    req = urllib2.Request(url)   
    req.add_header('User-Agent', UA_IPAD)
    
    try:    
        response = urllib2.urlopen(req)    
        json_source = json.load(response)                           
        response.close()                
    except HTTPError as e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code          
        sys.exit()
    
    for video in json_source['videos']:
        title = video['title']
        name = title
        icon = video['image']
        url = video['mediaGroup'][0]['url']
        desc = video['description']
        release_date = video['releaseDate'][0:10]

        info = {'plot':desc,'tvshowtitle':'NHL','title':name,'originaltitle':name,'duration':'','aired':release_date}
        video_info = { 'codec': 'h264', 'width' : 960, 'height' : 540, 'aspect' : 1.78 }
        audio_info = { 'codec': 'aac', 'language': 'en', 'channels': 2 }
        addLink(name,url,title,icon,info,video_info,audio_info)

    xbmc.executebuiltin("Container.SetViewMode(504)")



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
    live_feeds=int(urllib.unquote_plus(params["live_feeds"]))
except:
    pass
try:
    archive_feeds=int(urllib.unquote_plus(params["archive_feeds"]))
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
        if game_day != '':    
            msg = "The date entered is not in the format required."
            dialog = xbmcgui.Dialog() 
            ok = dialog.ok('Invalid Date', msg)

        sys.exit()

elif mode == 300:
    quickPicks()

elif mode == 999:
    sys.exit()


if mode == 100:
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
elif mode == 101:
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False, updateListing=True)
else:
    xbmcplugin.endOfDirectory(addon_handle)
    
