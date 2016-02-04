import sys
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import re, os, time
from datetime import date, datetime, timedelta
import urllib, urllib2
from urllib2 import URLError, HTTPError
import json
import cookielib
import time
from resources.lib.globals import *


def categories():    
    localToEastern()

    addDir('Today\'s Games','/live',100,ICON,FANART)
    addDir('Goto Date','/date',200,ICON,FANART)
    addDir('Quick Picks','/qp',300,ICON,FANART)  
    addDir('Logout','/logout',400,ICON,FANART)
        

def todaysGames(game_day):
    print "GAME DAY = " + str(game_day)        
    display_day = stringToDate(game_day, "%Y-%m-%d")            
    prev_day = display_day - timedelta(days=1)                

    addDir('[B]<< Previous Day[/B]','/live',101,PREV_ICON,FANART,prev_day.strftime("%Y-%m-%d"))

    date_display = '[B][I]'+ colorString(display_day.strftime("%A, %m/%d/%Y"),GAMETIME_COLOR)+'[/I][/B]'
    addDir(date_display,'/nothing',999,ICON,FANART)


    #NEW
    '''
    GET https://statsapi.web.nhl.com/api/v1/schedule?date=2016-01-31&expand=schedule.game.content.media.epg,schedule.teams HTTP/1.1
    Host: statsapi.web.nhl.com
    Connection: keep-alive
    User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36
    Origin: https://www.nhl.com
    Accept: */*
    Referer: https://www.nhl.com/tv?&affiliateId=NHLTVLOGIN
    Accept-Encoding: gzip, deflate, sdch
    Accept-Language: en-US,en;q=0.8
    '''
        
    #url = 'http://f.nhl.com/livescores/nhl/leagueapp/20142015/scores/'+game_day+'_O1T1.json'
    #https://statsapi.web.nhl.com/api/v1/schedule?teamId=&startDate=2016-01-27&endDate=2016-01-27&expand=schedule.teams,schedule.linescore,schedule.game.content.media.epg,schedule.broadcasts&
    url = 'http://statsapi.web.nhl.com/api/v1/schedule?date='+game_day+'&expand=schedule.game.content.media.epg,schedule.teams'    
    req = urllib2.Request(url)    
    req.add_header('Connection', 'keep-alive')
    req.add_header('Accept', '*/*')
    req.add_header('Origin', 'https://www.nhl.com')
    req.add_header('User-Agent', UA_PC)
    req.add_header('Referer', 'https://www.nhl.com/tv?&affiliateId=NHLTVLOGIN')
    req.add_header('Accept-Language', 'en-US,en;q=0.8')
    req.add_header('Accept-Encoding', 'deflate')

    try:    
        response = urllib2.urlopen(req)    
        print response.info()
        #print response.read()          
        '''      
        from StringIO import StringIO
        import gzip
        
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO( response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()

        print data
        '''
        json_source = json.load(response)                           
        response.close()                
    except HTTPError as e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code          
        sys.exit()

    try:
        for game in json_source['dates'][0]['games']:        
            createGameListItem(game)
    except:
        pass
    
    next_day = display_day + timedelta(days=1)
    addDir('[B]Next Day >>[/B]','/live',101,NEXT_ICON,FANART,next_day.strftime("%Y-%m-%d"))


def createGameListItem(game):
    away = game['teams']['away']['team']
    home = game['teams']['home']['team']
    #http://nhl.cdn.neulion.net/u/nhlgc_roku/images/HD/NJD_at_BOS.jpg
    #icon = 'http://nhl.cdn.neulion.net/u/nhlgc_roku/images/HD/'+away['teamAbb']+'_at_'+home['teamAbb']+'.jpg'
    icon = 'http://raw.githubusercontent.com/eracknaphobia/game_images/master/square_black/'+away['abbreviation']+'vs'+home['abbreviation']+'.png'

    if TEAM_NAMES == "0":
        away_team = away['locationName']
        home_team = home['locationName']
    elif TEAM_NAMES == "1":
        away_team = away['teamName']
        home_team = home['teamName']
    elif TEAM_NAMES == "2":
        away_team = away['name']
        home_team = home['name']
    elif TEAM_NAMES == "3":
        away_team = away['abbreviation']
        home_team = home['abbreviation']


    if away_team == "New York":
        away_team = away['name']

    if home_team == "New York":
        home_team = home['name']


    fav_game = False
    if away['locationName'].encode('utf-8') == FAV_TEAM or away['name'].encode('utf-8') == FAV_TEAM:
        fav_game = True
        away_team = colorString(away_team,getFavTeamColor())           
    
    if home['locationName'].encode('utf-8') == FAV_TEAM or home['name'].encode('utf-8') == FAV_TEAM:
        fav_game = True
        home_team = colorString(home_team,getFavTeamColor())


    game_time = ''
    if game['status']['detailedState'] != 'Scheduled':
        game_time = game['status']['detailedState']
        if NO_SPOILERS == '1' and game_time[:5] == "Final":
             game_time = game_time[:5]
        elif NO_SPOILERS == '2' and game_time[:5] == "Final":
             if fav_game:
                  game_time = game_time[:5]
    else:            
        game_time = game['gameDate']
        game_time = stringToDate(game_time, "%Y-%m-%dT%H:%M:%SZ")
        game_time = UTCToLocal(game_time)
       
        if TIME_FORMAT == '0':
             game_time = game_time.strftime('%I:%M %p').lstrip('0')
        else:
             game_time = game_time.strftime('%H:%M')

    game_time = colorString(game_time,GAMETIME_COLOR)            
    game_id = str(game['gamePk'])


    #live_video = game['gameLiveVideo']
    epg = json.dumps(game['content']['media']['epg'])
    live_feeds = 0
    archive_feeds = 0
    '''
    for item in epg:



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

    '''    

    if NO_SPOILERS == '1':
        name = game_time + ' ' + away_team + ' at ' + home_team
    elif NO_SPOILERS == '2' and fav_game:            
        name = game_time + ' ' + away_team + ' at ' + home_team
    else:
        name = game_time + ' ' + away_team + ' ' + colorString(str(game['teams']['away']['score']),SCORE_COLOR) + ' at ' + home_team + ' ' + colorString(str(game['teams']['home']['score']),SCORE_COLOR) 


    name = name.encode('utf-8')
    if fav_game:
        name = '[B]'+name+'[/B]'
    
    title = away_team + ' at ' + home_team
    title = title.encode('utf-8')
    
    #Set audio/video info based on stream quality setting
    audio_info, video_info = getAudioVideoInfo()
    addStream(name,'',title,game_id,epg,icon,None,None,video_info,audio_info)



def streamSelect(game_id, epg):
    #print epg
    #0 = NHLTV
    #1 = Audio
    #2 = Extended Highlights
    #3 = Recap
    epg = json.loads(epg)    
    full_game_items = epg[0]['items']
    audio_items = epg[1]['items']
    highlight_items = epg[2]['items']
    recap_items = epg[3]['items']

    stream_title = []
    content_id = []
    event_id = []
    media_state = []
    archive_type = ['Recap','Extended Highlights','Full Game']    
    #archive_gs = ['dvr','condensed','highlights']
    #archive_gs = ['archive','condensed','highlights']

    '''
    Video Item Ex. ARCHIVE
    "mediaState": "MEDIA_ARCHIVE",
    "mediaPlaybackId": "40465403",
    "mediaFeedType": "HOME",
    "callLetters": "Sun",
    "eventId": "221-1000843",
    "language": "eng",
    "freeGame": false,
    "feedName": "",
    "gamePlus": false


    Video Item Ex. LIVE
    "mediaState" : "MEDIA_ON",
    "mediaPlaybackId" : "40699203",
    "mediaFeedType" : "AWAY",
    "callLetters" : "TSN4",
    "eventId" : "221-1000847",
    "language" : "eng",
    "freeGame" : true,
    "feedName" : "",
    "gamePlus" : false
    '''
    
    if len(full_game_items) > 0:
        for item in full_game_items:
            media_state.append(item['mediaState'])
            stream_title.append(item['mediaFeedType'].encode('utf-8'))
            content_id.append(item['mediaPlaybackId'])
            event_id.append(item['eventId'])
    else:
        msg = "No playable streams found."
        dialog = xbmcgui.Dialog() 
        ok = dialog.ok('Streams Not Found', msg)
        sys.exit()

    
    #Reverse Order for display purposes
    #stream_title.reverse()
    #ft.reverse()
    print "MEDIA STATE"
    print media_state
    
    if media_state[0] == 'MEDIA_ARCHIVE':
        dialog = xbmcgui.Dialog() 
        a = dialog.select('Choose Archive', archive_type)
        if a < 2:
            if a == 0:
                #Recap
                stream_url = createHighlightStream(recap_items[0]['playbacks'][3]['url'])
            elif a == 1:
                #Extended Highlights
                stream_url = createHighlightStream(highlight_items[0]['playbacks'][3]['url'])
        elif a == 2:
            dialog = xbmcgui.Dialog() 
            n = dialog.select('Choose Stream', stream_title)
            if n > -1:
                stream_url, media_auth = fetchStream(game_id, content_id[n],event_id[n])
                #media_auth = 'mediaAuth_v2=6455209108eaa22507b1b305ff7466270d11c4e1da95b07350c56bb10f338607b5d98f2ed6ead08cd6a1bcf2e19f10d29e024a4bca234c1a109b468bf250faa565a1cbc5e0df334e8d5e29ad29741d2346125603140f0a7003a55906116037d14dc440d39fe59a8829cd3eb560928d76f2ddcee3a015f942a516ef5006d02c80b775f88ff32ee7fb23ec9fa467495e3f059519b2bf2efb44a5c033300205ed855668994c9503ba121bdacd28f4080016eec9931353665a430919d8a2bbcc1da3011db9a866bbc89371c59d0a72af0135da62c4946f214c31ce12f5f02a5843e63ab2f709cca8b65b3b152458e523bd6412566562db76ae6e3917ccf8dd96c1c09a02d80f0c45af74abf8e1df7fbdb20fcaf26624e30418286b3d50f446fa94ce4fa870fc15ff99d0068992b18745715f38b47f939c6161593247ddd143ea0239ab65533c951ce45892c04d0f6e410edbdd9d78df07e6ea9c62c06b0df8d1d2dfd0f1afb9f9837056fa5be96dba27293b2d1e22edd4c61eae647957e869ba885ec0a7149070a8a38f9075d2df8f2d068de30456bb1184738425bc5c9cdfc566da704f79bf6f90d73ee7fd0de31cefdcfec0402898d40733039d347d4499f45345e0e3bd26fa0b3609b2d46474a72d4e3ca299001ff41c549c5d1f7ad0d0e58fd1693175111df970dd21bb4a059235afd397a8dbcfec0905bf'                
                #stream_url = 'http://hlslive-l3c.med2.med.nhl.com/ls04/nhl/2016/02/03/NHL_GAME_VIDEO_OTTPIT_M2_HOME_20160203/master_wired_web.m3u8'                
                stream_url = createFullGameStream(stream_url,media_auth,media_state[n])    
            else:
                sys.exit()
        else:
            sys.exit()
    else:
        dialog = xbmcgui.Dialog() 
        n = dialog.select('Choose Stream', stream_title)
        if n > -1:
            stream_url, media_auth = fetchStream(game_id, content_id[n],event_id[n])
            stream_url = createFullGameStream(stream_url,media_auth,media_state[n])
            #media_auth = 'mediaAuth_v2=6455209108eaa22507b1b305ff7466270d11c4e1da95b07350c56bb10f338607b5d98f2ed6ead08cd6a1bcf2e19f10d29e024a4bca234c1a109b468bf250faa565a1cbc5e0df334e8d5e29ad29741d2346125603140f0a7003a55906116037d14dc440d39fe59a8829cd3eb560928d76f2ddcee3a015f942a516ef5006d02c80b775f88ff32ee7fb23ec9fa467495e3f059519b2bf2efb44a5c033300205ed855668994c9503ba121bdacd28f4080016eec9931353665a430919d8a2bbcc1da3011db9a866bbc89371c59d0a72af0135da62c4946f214c31ce12f5f02a5843e63ab2f709cca8b65b3b152458e523bd6412566562db76ae6e3917ccf8dd96c1c09a02d80f0c45af74abf8e1df7fbdb20fcaf26624e30418286b3d50f446fa94ce4fa870fc15ff99d0068992b18745715f38b47f939c6161593247ddd143ea0239ab65533c951ce45892c04d0f6e410edbdd9d78df07e6ea9c62c06b0df8d1d2dfd0f1afb9f9837056fa5be96dba27293b2d1e22edd4c61eae647957e869ba885ec0a7149070a8a38f9075d2df8f2d068de30456bb1184738425bc5c9cdfc566da704f79bf6f90d73ee7fd0de31cefdcfec0402898d40733039d347d4499f45345e0e3bd26fa0b3609b2d46474a72d4e3ca299001ff41c549c5d1f7ad0d0e58fd1693175111df970dd21bb4a059235afd397a8dbcfec0905bf'
            #stream_url = 'http://hlslive-l3c.med2.med.nhl.com/ls04/nhl/2016/02/03/NHL_GAME_VIDEO_OTTPIT_M2_HOME_20160203/master_wired_web.m3u8'
            #media_auth = 'mediaAuth_v2=6455209108eaa22507b1b305ff7466270d11c4e1da95b07350c56bb10f33860786db6d4fe9f572bd0f9ed4d6f1485c5053ba2ce26aaa4855149c199926ede2c1d8b6b51ed25f99333e7873d689f560afc8ba6a2651a53ff9d07614b74bef3e71d801164e74179b435d293a7d6ebd1072a18a5f1c6db62f04b420057f6c773d175668918d75ad3c36e1ffabbc46f9b50e2b94beede308566d37bb4d4ba6636df87e9ccc55219bacbf29dcf93736da0a5915ece5275156f54e4b33299998caa2964020b38f805dfb4055402bff7f37280a3639c904c857c8cc0c16fe359635a24d7aa9f3518fb2eb2c6df6c497f5362f793befddd248c909f4e6ab33bad872ade3a2d3719773558a5411198861cb0d669b16e971e48d6ee0e2e9375ab7b237d95199ecb199ed140ae2da21b539d16e91c0cf626a12ea62246631bb00720f2efdcb475a0774b0d9b54d7234b10fb688fe6b21ff4192dbcaa3fd9d4d84fe28c499ffc3c4bd4fcd760a7a232c4242642e0430305a41e0d99f269718634b00a1666927a070e5980e0755949c148bb87f596d9609cb0a411509c0d43a0e6cdba5bd3b84593d0219efe4492dd4a56cb10a8da34f24bba47a083aac81ecb811ac59673d9380c62ebe4a44557970f6eeb3b6f8a4319f2a4100fc243f5a3769ca713b444b0284fc0a5172ce0c45b0b72092f1b0e1dbe7dcf12ce6004c48'
            #stream_url = "http://hlslive-l3c.med2.med.nhl.com/ls04/nhl/2016/02/03/NHL_GAME_VIDEO_TORBOS_M2_COMPOSITE_3X_20160203/master_wired_web.m3u8"
            #stream_url = 'http://hlslive-l3c.med2.med.nhl.com/ls04/nhl/2016/02/03/NHL_GAME_VIDEO_CBJEDM_M2_ISO_3_20160203/master_wired_web.m3u8'
        else:
            sys.exit()

    if stream_url != '':
        listitem = xbmcgui.ListItem(path=stream_url)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
        #logout()
    else:
        sys.exit()
        

def createHighlightStream(stream_url):
    bandwidth = find(QUALITY,'(',' kbps)')
    #asset_5000k.m3u8
    stream_url = stream_url.replace('master_wired.m3u8', 'asset_'+bandwidth+'k.m3u8')
    stream_url = stream_url + '|User-Agent='+UA_PS4
    print stream_url
    return stream_url

def createFullGameStream(stream_url, media_auth, media_state):
    #SD (800 kbps)|SD (1600 kbps)|HD (3000 kbps)|HD (5000 kbps)        
    bandwidth = find(QUALITY,'(',' kbps)')

    #Reduce max bandwidth if composite video selected
    if ('COMPOSITE' in stream_url or 'ISO' in stream_url) and int(bandwidth) >= 5000:
            bandwidth = '3500'
    
    if media_state == 'MEDIA_ARCHIVE':                
        #ARCHIVE
        stream_url = stream_url.replace('master_wired_web.m3u8', bandwidth+'K/'+bandwidth+'_complete-trimmed.m3u8') 

    elif media_state == 'MEDIA_ON':
        #LIVE    
        #5000K/5000_slide.m3u8 OR #3500K/3500_complete.m3u8
        # Slide = Live, Complete = Watch from beginning?
        stream_url = stream_url.replace('master_wired_web.m3u8', bandwidth+'K/'+bandwidth+'_slide.m3u8') 
                
    
    cj = cookielib.LWPCookieJar()
    cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)

    cookies = ''
    for cookie in cj:            
        if cookie.name == "Authorization":
            cookies = cookies + cookie.name + "=" + cookie.value + "; "
    stream_url = stream_url + '|User-Agent='+UA_PS4+'&Cookie='+cookies+media_auth

    print "STREAM URL: "+stream_url
    return stream_url
                


def fetchStream(game_id, content_id,event_id):        
    #login()    
   
    authorization = ''    
    try:
        cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))     
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)    

        #If authorization cookie is missing or stale, perform login    
        for cookie in cj:            
            if cookie.name == "Authorization" and not cookie.is_expired():            
                authorization = cookie.value 
    except:
        pass


    if authorization == '':
        login()
        cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))     
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)    
        for cookie in cj:            
            if cookie.name == "Authorization":
                authorization = cookie.value 

    #cj.close()

    epoch_time_now = str(int(round(time.time()*1000)))    
    url = 'https://mf.svc.nhl.com/ws/media/mf/v2.4/stream?eventId='+event_id+'&format=json&platform=WEB_MEDIAPLAYER&subject=NHLTV&_='+epoch_time_now

    req = urllib2.Request(url)       
    req.add_header("Accept", "application/json")
    req.add_header("Accept-Encoding", "deflate")
    req.add_header("Accept-Language", "en-US,en;q=0.8")                       
    req.add_header("Connection", "keep-alive")
    req.add_header("Authorization", authorization)
    req.add_header("User-Agent", UA_PC)
    req.add_header("Origin", "https://www.nhl.com")
    req.add_header("Referer", "https://www.nhl.com/tv/"+game_id+"/"+event_id+"/"+content_id)
    
    response = urllib2.urlopen(req)
    json_source = json.load(response)   
    response.close()

    if json_source['status_code'] == 1:
        session_key = json_source['session_key']
    else:
        msg = json_source['status_message']
        dialog = xbmcgui.Dialog() 
        ok = dialog.ok('Error Fetching Stream', msg)
        sys.exit()

   
    epoch_time_now = str(int(round(time.time()*1000)))

    #url = 'https://mf.svc.nhl.com/ws/media/mf/v2.4/stream?contentId='+content_id+'&playbackScenario=HTTP_CLOUD_WIRED_WEB&sessionKey='+session_key+'&auth=response&format=json&platform=WEB_MEDIAPLAYER&_='+epoch_time_now       
    url = 'https://mf.svc.nhl.com/ws/media/mf/v2.4/stream?contentId='+content_id+'&playbackScenario=HTTP_CLOUD_WIRED_WEB&sessionKey='+session_key+'&auth=response&format=json&platform=WEB_MEDIAPLAYER&_='+epoch_time_now       
    req = urllib2.Request(url)       
    req.add_header("Accept", "application/json")
    req.add_header("Accept-Encoding", "deflate")
    req.add_header("Accept-Language", "en-US,en;q=0.8")                       
    req.add_header("Connection", "keep-alive")
    req.add_header("Authorization", authorization)
    req.add_header("User-Agent", UA_PC)
    req.add_header("Origin", "https://www.nhl.com")    
    req.add_header("Referer", "https://www.nhl.com/tv/"+game_id+"/"+event_id+"/"+content_id)
    
    response = urllib2.urlopen(req)
    json_source = json.load(response)   
    response.close()
    '''
    return codes
    {"status_code":1,"status_message":"Success Status","session_key":"803U9tXqp8+2O+dr0ESCF67QZNo=","session_info":{...
    {"status_code":-1600,"status_message":"Invalid media state: Media is not in a playable state","session_key":"803U9tXqp8+2O+dr0ESCF67QZNo="}
    {"status_code":-3500,"status_message":"Sign-on restriction: Too many usage attempts"}
    '''
    stream_url = ''
    media_auth = ''

    if json_source['status_code'] == 1:
        if json_source['user_verified_event'][0]['user_verified_content'][0]['user_verified_media_item'][0]['blackout_status']['status'] == 'BlackedOutStatus':
            msg = "This game was broadcast on television in your area and is not available to view at this time. Please check back after 48 hours."
            dialog = xbmcgui.Dialog() 
            ok = dialog.ok('Game Blacked Out', msg) 
        else:
            stream_url = json_source['user_verified_event'][0]['user_verified_content'][0]['user_verified_media_item'][0]['url']    
            media_auth = str(json_source['session_info']['sessionAttributes'][0]['attributeName']) + "=" + str(json_source['session_info']['sessionAttributes'][0]['attributeValue'])

            '''
            Possibly used to keep too many usage errors at bay???
            GET https://mf.svc.nhl.com/ws/media/mf/v2.3/key/silk/mediaid/40699103/kid/20106583 HTTP/1.1
            Host: mf.svc.nhl.com
            Connection: keep-alive
            Cookie: mediaAuth_v2=6455209108eaa22507b1b305ff7466270d11c4e1da95b07350c56bb10f3386075f66e69b12f9d9c1edbbf7c4ce3cfb2e67e792013032c3a167920c42f28925bc3c987f6ab3ec425e4af8df799c332151906fad874b3df2127dec5c3458ba9609b52d29ad5d59a271b34dbbe82ebf18027ccb6128e171aa390555f0cce70427974e48fa221226417e482b20e406718108d2911569ccdc69c40e78577dce3aae97f8ae801c482cada83cea211f720232687509311e4cae274f37f7e2493d0755467deabe3fc3b77ca2d5b5d33e3fdcb31eb95c843f52f2648755355bd8ca542ed6f8f7072e50b8ac6bbc1f7e2105c47efbf065af05d98535c7dd0b4296f32a7df5dd3df12234487a421ed510866f005221334fd5dbf9a1916328bf87b89180e51756ca34cb1d37aab1ac20c817b5c37a7f0fa8102a9be94066a53c6998fc3ab6a756d6edf5f0d06ccdaeef62d161ef08920e770a1ed41014a4404cc0e3ee5b35983aead99e097fbc736a63f46687bf99f23c1d7c62249bfe202795c7c80482060e903e625c33faf572dbd7c4dd7646fed97bceb8d94b9dee8c2f419d722e7065ff23454d45fb1a7e8d82f402675d327c18aeee8ebd64a049b17fa460ac36424b1c956526b7fd396d2641d1e24e7479830f7276828e18cce647e38b407dbbf8a50700476d001bebb82e50a1d7214dce96ad2ecc546f9bdaec37; Authorization=eyJhbGciOiJIUzI1NiJ9.eyJzaWdub24tbG9jYXRpb24iOm51bGwsInNpZ25vbi1zZXNzaW9uLWtleSI6bnVsbCwiY2xpZW50SWQiOiJhY3RpdmF0aW9uX25obC12MS4wLjAiLCJ2ZXJpZmljYXRpb25MZXZlbCI6MiwidHlwZSI6IlVzZXIiLCJ1c2VyaWQiOiIxMzM4OTgzIiwidmVyc2lvbiI6InYxLjAiLCJwY19tYXhfcmF0aW5nX3R2IjoiIiwiZXhwaXJlc0F0IjoxNDg2MDUyMjgwMjczLCJpcGlkIjoibmhsR2F0ZXdheUlkOjIwMDcyMDQiLCJzaWdub24tdHlwZSI6bnVsbCwicGNfbWF4X3JhdGluZ19tb3ZpZSI6IiIsImNvbnRleHQiOnt9LCJjcmVhdGVkX2RhdGUiOjE0NTQ1MTYyODAyNzMsImVtYWlsIjoiZXJhY2tuYXBob2JpYUBob3RtYWlsLmNvbSJ9.LV5MJj6ENjDNATGwL6g9EPPM1l8j5Q9SXQi3gmJb6WE
            Cache-Control: no-cache
            User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36
            Accept: */*
            Accept-Encoding: gzip, deflate, sdch
            Accept-Language: en-US,en;q=0.8
            '''
            url = 'https://mf.svc.nhl.com/ws/media/mf/v2.3/key/silk/mediaid/40699103/kid/20106583'       
            req = urllib2.Request(url)       
            req.add_header("Accept", "*/*")
            req.add_header("Accept-Encoding", "gzip, deflate, sdch")
            req.add_header("Accept-Language", "en-US,en;q=0.8")                               
            req.add_header("Cookie", media_auth+"; Authorization="+authorization)
            req.add_header("User-Agent", UA_PC)            
            req.add_header("Cache-Control", "no-cache")
            req.add_header("Connection", "keep-alive")
            
            response = urllib2.urlopen(req)
            
            response.close()
    else:
        msg = json_source['status_message']
        dialog = xbmcgui.Dialog() 
        ok = dialog.ok('Error Fetching Stream', msg)
       
    
    return stream_url, media_auth    


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
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))   
 
        if ROGERS_SUBSCRIBER == 'true':            
            #Get Token
            url = 'https://user.svc.nhl.com/oauth/token?grant_type=client_credentials'
            req = urllib2.Request(url)       
            req.add_header("Accept", "application/json")
            req.add_header("Accept-Encoding", "gzip, deflate, sdch")
            req.add_header("Accept-Language", "en-US,en;q=0.8")                                           
            req.add_header("User-Agent", UA_PC)
            req.add_header("Referer", "https://www.nhl.com/login/rogers")
            req.add_header("Authorization", "Basic d2ViX25obC12MS4wLjA6MmQxZDg0NmVhM2IxOTRhMThlZjQwYWM5ZmJjZTk3ZTM=")

            response = urllib2.urlopen(req, '')
            json_source = json.load(response)   
            access_token = json_source['access_token']
            response.close()

            #Login
            url = 'https://activation-rogers.svc.nhl.com/ws/subscription/flow/rogers.login-check'            
            login_data = '{"rogerCredentials":{"email":"'+USERNAME+'","password":"'+PASSWORD+'"}}'
            req = urllib2.Request(url, data=login_data,
               headers={"Accept": "*/*",
                         "Accept-Encoding": "gzip, deflate",
                         "Accept-Language": "en-US,en;q=0.8",
                         "Content-Type": "application/json",                            
                         "Origin": "https://www.nhl.com",
                         "Connection": "keep-alive",
                         "Authorization": access_token,
                         "Referer": "https://www.nhl.com/login/rogers",
                         "User-Agent": UA_PC})
        else:
            url = 'https://gateway.web.nhl.com/ws/subscription/flow/nhlPurchase.login'
            login_data = '{"nhlCredentials":{"email":"'+USERNAME+'","password":"'+PASSWORD+'"}}'
            req = urllib2.Request(url, data=login_data,
               headers={"Accept": "*/*",
                         "Accept-Encoding": "gzip, deflate",
                         "Accept-Language": "en-US,en;q=0.8",
                         "Content-Type": "application/json",                            
                         "Origin": "https://www.nhl.com",
                         "Connection": "keep-alive",
                         "User-Agent": UA_PC})     
       
        response = opener.open(req)              
        user_data = response.read()
        response.close()
      

        cj.save(ignore_discard=True); 


def logout():
    cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))     
    cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
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
epg=None

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
    epg=urllib.unquote_plus(params["epg"])
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
    streamSelect(game_id, epg)
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

elif mode == 400:
    logout()

elif mode == 999:
    sys.exit()


if mode == 100:
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
elif mode == 101 or mode == 400:
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False, updateListing=True)
else:
    xbmcplugin.endOfDirectory(addon_handle)