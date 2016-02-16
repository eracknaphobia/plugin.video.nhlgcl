import xbmc, xbmcplugin, xbmcgui, xbmcaddon
from time import sleep
from datetime import datetime
import urllib, urllib2
import json

ADDON = xbmcaddon.Addon(id='plugin.video.nhlgcl')
ADDON_PATH = xbmc.translatePath(ADDON.getAddonInfo('path'))
UA_IPAD = 'Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12H143 ipad nhl 5.0925'
nhl_logo = ADDON_PATH+'/resources/lib/nhl_logo.png'

#Colors
SCORE_COLOR = 'FF00B7EB'
GAMETIME_COLOR = 'FFFFFF66'


def getScoreBoard(date):
    #url = "http://live.nhle.com/GameData/GCScoreboard/"+date+".jsonp"    
    url = 'http://statsapi.web.nhl.com/api/v1/schedule?teamId=&date='+date+'&expand=schedule.teams,schedule.linescore,schedule.game.content.media.epg,schedule.broadcasts,schedule.scoringplays,team.leaders,leaders.person,schedule.ticket,schedule.game.content.highlights.scoreboard,schedule.ticket&leaderCategories=points'
    print url    
    req = urllib2.Request(url)    
    req.add_header('Connection', 'keep-alive')
    req.add_header('Accept', 'application/json')
    req.add_header('User-Agent', UA_IPAD)
    req.add_header('Accept-Language', 'en-us')
    req.add_header('Accept-Encoding', 'deflate')

    response = urllib2.urlopen(req)    
    json_source = json.load(response)  
    #content = response.read()
    response.close()
    #jsonData = content.strip()

    #jsonData = jsonData.replace('loadScoreboard(', '')
    #jsonData = jsonData.rstrip(')')

    #json_source = json.loads(jsonData)

    return json_source


def startScoringUpdates():
        
    FIRST_TIME_THRU = 1  
    OLD_GAME_STATS = []   
    todays_date = datetime.now().strftime("%Y-%m-%d")          
    
    while ADDON.getSetting(id="score_updates") == 'true':  
        game_url = ''
        try:   
            #Get the url of the video that is currently playing
            if xbmc.Player().isPlayingVideo():
                game_url = xbmc.Player().getPlayingFile()                                                    
        except:
            pass
        json_source = getScoreBoard(todays_date)                                  
        NEW_GAME_STATS = []
        #refreshInterval = json_source['refreshInterval']
        refreshInterval = 60
        for game in json_source['dates'][0]['games']:
            #Break out of loop if updates disabled
            if ADDON.getSetting(id="score_updates") == 'false':                                       
                break

            gid = str(game['gamePk'])
            ateam = game['teams']['away']['team']['abbreviation']
            hteam = game['teams']['home']['team']['abbreviation']
            ascore = str(game['linescore']['teams']['away']['goals'])
            hscore = str(game['linescore']['teams']['home']['goals'])
            
            print gid
            #Team names (these can be found in the live streams url)
            atcommon = game['teams']['away']['team']['abbreviation']
            htcommon = game['teams']['home']['team']['abbreviation']

            gameclock = game['status']['detailedState']
            
            if 'In Progress' in gameclock:            
                gameclock = game['linescore']['currentPeriodTimeRemaining']+' '+game['linescore']['currentPeriodOrdinal']
            
            #Disable spoiler by not showing score notifications for the game the user is currently watching
            if game_url.find(atcommon.lower()) == -1 and game_url.find(htcommon.lower()) == -1:
                NEW_GAME_STATS.append([gid,ateam,hteam,ascore,hscore,gameclock])
                

        if FIRST_TIME_THRU != 1:
            display_seconds = int(ADDON.getSetting(id="display_seconds"))
            if display_seconds > 60:
                #Max Seconds 60
                display_seconds = 60
            elif display_seconds < 1:
                #Min Seconds 1
                display_seconds = 1

            #Convert to milliseconds
            display_milliseconds = display_seconds * 1000
            all_games_finished = 1
            for new_item in NEW_GAME_STATS:                    
                if ADDON.getSetting(id="score_updates") == 'false':                                       
                    break
                #Check if all games have finished
                if new_item[5].find('FINAL') == -1:
                    all_games_finished = 0

                for old_item in OLD_GAME_STATS:                    
                    #Break out of loop if updates disabled
                    if ADDON.getSetting(id="score_updates") == 'false':                                       
                        break
                    if new_item[0] == old_item[0]:
                        #If the score for either team has changed and is greater than zero.                                                       #Or if the game has just ended show the final score
                        if  ((new_item[3] != old_item[3] and int(new_item[3]) != 0) or (new_item[4] != old_item[4] and int(new_item[4]) != 0)) or (new_item[5].find('Final') != -1 and old_item[5].find('Final') == -1):
                            #Game variables                                                    
                            ateam = new_item[1]
                            hteam = new_item[2]
                            ascore = new_item[3]
                            hscore = new_item[4]
                            gameclock = new_item[5]                            
                            
                            #Highlight goal(s) or the winning team
                            if new_item[5].find('Final') != -1:
                                title = 'Final Score'
                                if int(ascore) > int(hscore):
                                    message = '[COLOR='+SCORE_COLOR+']' + ateam + ' ' + ascore + '[/COLOR]    ' + hteam + ' ' + hscore + '    [COLOR='+GAMETIME_COLOR+']' + gameclock + '[/COLOR]'
                                else:
                                    message = ateam + ' ' + ascore + '    [COLOR='+SCORE_COLOR+']' + hteam + ' ' + hscore + '[/COLOR]    [COLOR='+GAMETIME_COLOR+']' + gameclock  + '[/COLOR]'
                            else:                                
                                title = 'Score Update'
                                #Highlight if changed
                                if new_item[3] != old_item[3]:
                                    ascore = '[COLOR='+SCORE_COLOR+']'+new_item[3]+'[/COLOR]'                                
                                
                                if new_item[4] != old_item[4]:                                
                                    hscore = '[COLOR='+SCORE_COLOR+']'+new_item[4]+'[/COLOR]'

                                message = ateam + ' ' + ascore + '    ' + hteam + ' ' + hscore + '    [COLOR='+GAMETIME_COLOR+']' + gameclock + '[/COLOR]'

                            if ADDON.getSetting(id="score_updates") != 'false':                                       
                                #print message                   
                                dialog = xbmcgui.Dialog()
                                dialog.notification(title, message, nhl_logo, display_milliseconds, False)
                                sleep(display_seconds)
            #if all games have finished for the night kill the thread
            if all_games_finished == 1 and ADDON.getSetting(id="score_updates") == 'true':
                ADDON.setSetting(id='score_updates', value='false')
                dialog = xbmcgui.Dialog() 
                title = "Score Notifications"
                dialog.notification(title, 'All games have ended, good night.', nhl_logo, 5000, False)



        OLD_GAME_STATS = []
        OLD_GAME_STATS = NEW_GAME_STATS              
        FIRST_TIME_THRU = 0          
        sleep(int(refreshInterval))   
    

dialog = xbmcgui.Dialog()  
title = "Score Notifications"  
#Toggle the setting
if ADDON.getSetting(id="score_updates") == 'false':        
    dialog.notification(title, 'Starting...', nhl_logo, 5000, False)  
    ADDON.setSetting(id='score_updates', value='true')
    startScoringUpdates()    
else:    
    ADDON.setSetting(id='score_updates', value='false')    
    dialog.notification(title, 'Stopping...', nhl_logo, 5000, False)