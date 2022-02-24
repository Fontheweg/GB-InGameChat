#!/usr/bin/env python3
import asyncio, websockets, json, hmac, hashlib, base64, datetime, time, os
from discord_webhook import DiscordWebhook, DiscordEmbed

#Gameconnection
game_entryURL = "URL"
game_hmac   = "HMAC"
max_player_onlinetime_to_kill = 2500

#Webhooks for Discord
Channel_Logging     = DiscordWebhook(url='WEBHOOK-URL FOR LOGGING', rate_limit_retry=True)
Channel_BGA_URL     = 'WEBHOOK-URL FOR ALL POSTS'
Channel_BGA_Chat    = DiscordWebhook(url=Channel_BGA_URL, rate_limit_retry=True)
Channel_BG_Chat     = DiscordWebhook(url=[Channel_BGA_URL,'WEBHOOK-URL FOR TEAM 1'], rate_limit_retry=True)
Channel_BG2_Chat    = DiscordWebhook(url=[Channel_BGA_URL,'WEBHOOK-URL FOR TEAM 2'], rate_limit_retry=True)
Channel_BG3_Chat    = DiscordWebhook(url=[Channel_BGA_URL,'WEBHOOK-URL FOR TEAM 3'], rate_limit_retry=True)

#npc
login_username  = "NPC-USER"
login_password  = "NPC-PW"

#playerdata team 1
login_name1     = "DISPLAYED NAME FOR PLAYER TEAM 1"
login_username1 = "USER PLAYER TEAM 1"
login_id1       = "ID PLAYER TEAM 1"
login_password1 = "PW PLAYER TEAM 1"
login_teamid1   = "TEAM-ID TEAM 1"
log_last_mgs1   = "Team1_LastMessage.log"

#playerdata team 2
login_name2     = ""
login_username2 = ""
login_id2       = "" 
login_password2 = ""
login_teamid2   = ""
log_last_mgs2   = ""

#playerdata team 3
login_name3     = ""
login_username3 = ""
login_id3       = ""
login_password3 = ""
login_teamid3   = ""
log_last_mgs3   = ""

#Messages
myMessages = []
myMessageCount = 100
myLog = ''

# ========================================================================================================================================================================
# Get Playerstatus by using NPC for lookup
async def getPlayer(myUser,myPW):
    status = [True,True,True]
    myLog = ''
    ws1 = await websockets.connect(
        game_entryURL, 
        compression=None
    )
    info = await ws1.recv()
    
    ws2 = await websockets.connect(
        json.loads(info)["connectUrl"],
        compression=None
    )
    info2 = await ws2.recv()
    
    outobj = {
        "@class": ".AuthenticatedConnectRequest",
        "hmac": base64.b64encode(hmac.new(game_hmac,
        json.loads(info2)["nonce"].encode('utf-8'),
        hashlib.sha256).digest()).decode('utf-8'),
        "os": "uh"
    }
    await ws2.send(
        json.dumps(outobj)
    )
    await ws2.recv()
    await ws2.send(
        json.dumps(
            {
                "@class": ".AuthenticationRequest",
                "userName": myUser,
                "password": myPW,
                "scriptData": {
                    "game_version": 9999,
                    "client_version": 99999
                },
                "requestId": "ok"
            }
        )
    )
    print("Login as: NPC")

    # User BrettGang prüfen
    await ws2.send(
        json.dumps(
            {
                "@class": ".LogEventRequest",
                "eventKey": "GET_TEAM_REQUEST",
                "team_id": login_teamid1,
                "requestId": "thanks a lot"
            }
        )
    )
    async for message in ws2:
        Data0 = json.loads(message)
        if Data0["@class"] == ".LogEventResponse":
            Data1 = Data0["scriptData"]
            Data2 = Data1["members"]
            for Player in Data2:
                if Player["id"] == login_id1:
                    status[0] = bool(Player["online"])
                    onlinetime = int(time.time() - Player['scriptData']['last_login']/1000)
                    print(' => BrettGang¹: ' + login_name1 + ' is online: ' + str(Player["online"]) + ' [' + str(onlinetime) + ']')
                    if str(Player['online']) == 'True' and onlinetime >= max_player_onlinetime_to_kill:
                        print(' => Player über 2,5 Stunden online => killen!')
                        myLog += login_name1 + ' ist seit über 2,5h online => kill\r\n'
                        status[0] = False
                    break
            break

    # User BrettGang² prüfen
    await ws2.send(
        json.dumps(
            {
                "@class": ".LogEventRequest",
                "eventKey": "GET_TEAM_REQUEST",
                "team_id": login_teamid2,
                "requestId": "thanks a lot"
            }
        )
    )
    async for message in ws2:
        Data0 = json.loads(message)
        if Data0["@class"] == ".LogEventResponse":
            Data1 = Data0["scriptData"]
            Data2 = Data1["members"]
            for Player in Data2:
                if Player["id"] == login_id2:
                    status[1] = bool(Player["online"])
                    onlinetime = int(time.time() - Player['scriptData']['last_login']/1000)
                    print(' => BrettGang²: ' + login_name2 + ' is online: ' + str(Player["online"]) + ' [' + str(onlinetime) + ']')
                    if str(Player['online']) == 'True' and onlinetime >= max_player_onlinetime_to_kill:
                        print(' => Player über 2,5 Stunden online => killen!')
                        myLog += login_name1 + ' ist seit über 2,5h online => kill\r\n'
                        status[1] = False
                    break
            break
    
    # User BrettGang³ prüfen
    await ws2.send(
        json.dumps(
            {
                "@class": ".LogEventRequest",
                "eventKey": "GET_TEAM_REQUEST",
                "team_id": login_teamid3,
                "requestId": "thanks a lot"
            }
        )
    )
    async for message in ws2:
        Data0 = json.loads(message)
        if Data0["@class"] == ".LogEventResponse":
            Data1 = Data0["scriptData"]
            Data2 = Data1["members"]
            for Player in Data2:
                if Player["id"] == login_id3:
                    status[2] = bool(Player["online"])
                    onlinetime = int(time.time() - Player['scriptData']['last_login']/1000)
                    print(' => BrettGang³: ' + login_name3 + ' is online: ' + str(Player["online"]) + ' [' + str(onlinetime) + ']')
                    if str(Player['online']) == 'True' and onlinetime >= max_player_onlinetime_to_kill:
                        print(' => Player über 2,5 Stunden online => killen!')
                        myLog += login_name1 + ' ist seit über 2,5h online => kill\r\n'                       
                        status[2] = False
                    break
            break
    
    await ws2.send(
        json.dumps(
            {
                "@class": ".EndSessionRequest"
            }
        )
    )
    result = await ws2.recv()
    result = json.loads(result)
    print(" => done in " + str(result["sessionDuration"]) + "ms")
    print(" => logout")
    print("")

    #Kills veröffentlichen
    if len(myLog) > 0:
        Post = DiscordEmbed(
            title='Script: IngameChat (KillSwitch)',
            description=myLog,
            color='ff0000'
        )
        Post.set_timestamp(time.time())
        Channel_Logging.add_embed(Post)
        Channel_Logging.execute()

    return status 

# ========================================================================================================================================================================
# Get InGameChat by using Teamplayers if actually offline
async def getGBChat(myDisplayame,myUser,myPW,myTeam,myCount):
    ws1 = await websockets.connect(
        game_entryURL, 
        compression=None
    )
    info = await ws1.recv()
    
    ws2 = await websockets.connect(
        json.loads(info)["connectUrl"],
        compression=None
    )
    info2 = await ws2.recv()
    
    outobj = {
        "@class": ".AuthenticatedConnectRequest",
        "hmac": base64.b64encode(hmac.new(game_hmac,
        json.loads(info2)["nonce"].encode('utf-8'),
        hashlib.sha256).digest()).decode('utf-8'),
        "os": "uh"
    }
    await ws2.send(
        json.dumps(outobj)
    )
    await ws2.recv()
    await ws2.send(
        json.dumps(
            {
                "@class": ".AuthenticationRequest",
                "userName": myUser,
                "password": myPW,
                "scriptData": {
                    "game_version": 9999,
                    "client_version": 99999
                },
                "requestId": "ok"
            }
        )
    )
    print("Login as: " + myDisplayame )
    print(" => Requesting Messages")

#    for i in range(4):
#         await ws2.recv()

    await ws2.send(json.dumps(
        {
            "@class" : ".ListTeamChatRequest",
            "entryCount" : myCount,
            "offset" : 0,
            "ownerId" : "me",
            "teamId" : myTeam,
            "teamType" : "BASIC_TEAM"        
            }
        )
    )
    await ws2.recv()

    async for message in ws2:
        Data0 = json.loads(message)
        if Data0["@class"] == ".ListTeamChatResponse":
            Data0Sorted = sorted(Data0["messages"], key=lambda ts: ts['when'])
            for message in Data0Sorted:
                Data1 = json.loads(message["message"])
                if Data1["type"] == "chat":
                    strID = message["id"]
                    strTS = int(message["when"]/1000)
                    strWHO = message["who"]
                    strMSG = Data1["msg"]
                    myMessages.append ([strID,strTS,strWHO,strMSG,myTeam])
            break
    
    await ws2.send(
        json.dumps(
            {
                "@class": ".EndSessionRequest"
            }
        )
    )
    result = await ws2.recv()
    result = json.loads(result)
    print(" => done in " + str(result["sessionDuration"]) + "ms")
    print(" => logout")
    print("")
       
# ========================================================================================================================================================================
# Array of Teamdata for posting on Discord [Color, Name, Id, Icon, Webhook]
def getTeam(TeamID):
    if TeamID == login_teamid1:             #Brettgang
        return ['ffd700', 'BrettGang¹', '¹', 'https://cdn.discordapp.com/emojis/944582795236343848.webp?size=96&quality=lossless', Channel_BG_Chat]
    elif TeamID == login_teamid2:           #Brettgang²
        return ['c0c0c0', 'BrettGang²', '²', 'https://cdn.discordapp.com/emojis/944582795190239272.webp?size=96&quality=lossless', Channel_BG2_Chat]
    elif TeamID == login_teamid3:           #Brettgang³
        return ['bf8970', 'BrettGang³', '³', 'https://cdn.discordapp.com/emojis/944582795169247302.webp?size=96&quality=lossless', Channel_BG3_Chat]            
    else:                                   #Unbekannt
        return ['ffffff', 'Unknown   ', ' ', 'https://cdn.discordapp.com/emojis/593134589183000577.webp?size=96&quality=lossless', Channel_Logging]

# ========================================================================================================================================================================
# ========================================================================================================================================================================
# ========================================================================================================================================================================

# Get Playerstatus
PlayerStatus = asyncio.get_event_loop().run_until_complete(getPlayer(login_username, login_password))

# Get Ingamechat
if PlayerStatus[0] == False:
    myLog += 'Brettgang¹ => checking ' + login_name1 + '\r\n'
    asyncio.get_event_loop().run_until_complete(getGBChat(login_name1,login_username1, login_password1, login_teamid1, myMessageCount))
else:
    myLog += 'Brettgang¹ => ' + login_name1 + ' is online, cancel!\r\n'

if PlayerStatus[1] == False:
    myLog += 'Brettgang² => checking ' + login_name2 + '\r\n'
    asyncio.get_event_loop().run_until_complete(getGBChat(login_name2,login_username2, login_password2, login_teamid2, myMessageCount))
else:
    myLog += 'Brettgang² => ' + login_name2 + ' is online, cancel!\r\n'

if PlayerStatus[2] == False:
    myLog += 'Brettgang³ => checking ' + login_name3 + '\r\n'
    asyncio.get_event_loop().run_until_complete(getGBChat(login_name3,login_username3, login_password3, login_teamid3, myMessageCount))
else:
    myLog += 'Brettgang³ => ' + login_name3 + ' is online, cancel!\r\n'

# Load last posted message timestamp
myLatestMessage1_Updated = False
myLatestMessage2_Updated = False
myLatestMessage3_Updated = False

File = open(log_last_mgs1 ,'r')
myLatestMessage1 = File.read()
File.close

File = open(log_last_mgs2 ,'r')
myLatestMessage2 = File.read()
File.close

File = open(log_last_mgs3 ,'r')
myLatestMessage3 = File.read()
File.close

# Sort all messages by timestamp
SortedMessages = sorted(myMessages, key=lambda ts: ts[1])
i = 0

# go through all messages
print("Messages:")
for message in SortedMessages:
    strID = message[0]
    strTS = message[1]
    strPLAYER = message[2]
    strMESSAGE = message[3]
    strTEAM = message[4]
    

    # load last timestamp from team for this message
    if strTEAM == login_teamid1:
        myLatestMessage = myLatestMessage1
        if len(myLatestMessage) == 0:
            myLatestMessage = time.time()
    elif strTEAM == login_teamid2:
        myLatestMessage = myLatestMessage2
        if len(myLatestMessage) == 0:
            myLatestMessage = time.time()
    elif strTEAM == login_teamid3:
        myLatestMessage = myLatestMessage3
        if len(myLatestMessage) == 0:
            myLatestMessage = time.time()
    else:
        myLatestMessage = time.time()

    # only post messages which are newer than the saved timestamp
    if int(myLatestMessage) < int(strTS):
        i += 1      
        strWebhook = getTeam(strTEAM)[4]

        strDATE = str(datetime.datetime.utcfromtimestamp(strTS))
        print(strDATE + " => " + getTeam(strTEAM)[1] + ": " + strPLAYER)
                
        Post = DiscordEmbed(
            description=strMESSAGE,
            color=getTeam(strTEAM)[0]       # color
        )
        Post.set_author(
            name=strPLAYER
        )
        Post.set_footer(
            text=getTeam(strTEAM)[1],       # Teamname
            icon_url=getTeam(strTEAM)[3]    # Teampicture (Number)
        )
        Post.set_timestamp(strTS)

        # >>> Post on Discord
        strWebhook.add_embed(Post)
        strWebhook.execute(remove_embeds=True)

        # notice that a messege is posted on channel
        if strTEAM == login_teamid1:
            myLatestMessage1_Updated = True
        elif strTEAM == login_teamid2:
            myLatestMessage2_Updated = True
        elif strTEAM == login_teamid3:
            myLatestMessage3_Updated = True        

print("Gelesene Nachrichten:  " + str(len(SortedMessages)))
print("Gepostete Nachrichten: " + str(i))
myLog += '\r\n'
myLog += 'New Posts: ' + str(i) + '\r\n'

# if a message is posted, save to file for next run
myLog += '\r\n'
if myLatestMessage1_Updated == True:
    File = open(log_last_mgs1,'w')
    File.write(str(strTS)) 
    File.close
    myLog += 'Brettgang¹ => latest Message updated\r\n'

if myLatestMessage2_Updated == True:
    File = open(log_last_mgs2,'w')
    File.write(str(strTS)) 
    File.close
    myLog += 'Brettgang² => latest Message updated\r\n'

if myLatestMessage3_Updated == True:
    File = open(log_last_mgs3,'w')
    File.write(str(strTS)) 
    File.close        
    myLog += 'Brettgang³ => latest Message updated\r\n'

# End >>> post log to Discord
Post = DiscordEmbed(
    title='Script: IngameChat',
    description=myLog,
    color='00ff00'
)
Post.set_timestamp(time.time())
Channel_Logging.add_embed(Post)
Channel_Logging.execute()

print("Finished")