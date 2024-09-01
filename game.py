import datetime
from time import time, sleep

import requests

from utils import select_tag, log, print_items

temp = {}


def post(cgi, data, token):
    res = requests.post('https://ak-gs-gf.hypergryph.com' + cgi, json=data, headers=temp[token])
    if 'seqnum' in res.headers.keys() and res.headers['seqnum'].isdigit():
        temp[token]["seqnum"] = res.headers['seqnum']
    else:
        temp[token]["seqnum"] = str(int(temp[token]["seqnum"]) + 1)
    return res.json()


def auto_checkin(player_data, token):
    # login only
    if act := player_data["activity"]["LOGIN_ONLY"]:
        log("Found LoginOnly Activity")
        for k in act:
            res = post('/activity/loginOnly/getReward', {"activityId": k}, token)
            #print_items(res["reward"])
    if act := player_data["activity"]["CHECKIN_ONLY"]:
        log("Found CheckinOnly Activity")
        for k, v in act.items():
            for index, value in enumerate(v["history"]):
                if value:
                    res = post('/activity/getActivityCheckInReward', {"activityId": k, "index": index}, token)
                    #print_items(res["items"])
    # bless only
    if act := player_data["activity"]["BLESS_ONLY"]:
        log("Found BlessOnly Activity")
        for k, v in act.items():
            for index, value in enumerate(v["history"]):
                if value:
                    res = post('/activity/actBlessOnly/getCheckInReward',
                               {"activityId": k, "index": index, "isFestival": 0},
                               token)
                    print_items(res["items"])

            for index, value in enumerate(v["festivalHistory"]):
                if value["state"] == 1:
                    res = post('/activity/actBlessOnly/getCheckInReward',
                               {"activityId": k, "index": index, "isFestival": 1},
                               token)
                    print_items(res["items"])
    # pray only
    if act := player_data["activity"]["PRAY_ONLY"]:
        log("Found PrayOnly Activity")
        for k, v in act.items():
            res = post('/activity/prayOnly/getReward',
                       {"activityId": k, "prayArray": list(range(1, v["prayDaily"] + 1))},
                       token)
            print_items(res["rewards"])

    if act := player_data["activity"]["GRID_GACHA_V2"]:
        log("Found GridGachaV2 Activity")
        for k in act:
            if act[k]["today"]["done"]: continue
            res = post('/activity/gridGachaV2/doTodayGacha', {"activityId": k}, token)
            print_items(res["items"])
    if act := player_data["activity"]["CHECKIN_ACCESS"]:
        log("Found Checkin Access Activity")
        for k in act:
            if not act[k]["currentStatus"]: continue
            res = post('/activity/actCheckinAccess/getCheckInReward', {"activityId": k}, token)
            #print_items(res["items"])


def auto_mail(token):
    mail_list = post('/mail/getMetaInfoList', {"from": int(time())}, token)['result']
    norm, sys = [], []
    for i in mail_list:
        if i['state'] or (not i['hasItem']): continue
        if i['type']:
            sys.append(i['mailId'])
        else:
            norm.append(i['mailId'])
    if (norm and sys):
        res = post('/mail/receiveAllMail', {"mailIdList": norm, "sysMailIdList": sys}, token)
        log("Received all mails")
        print_items(res["items"])


def auto_recruit(player_data, token):
    for i in range(0, 4):
        slot = player_data["recruit"]['normal']['slots'][str(i)]
        if not slot['state']: continue
        if slot['maxFinishTs'] > time(): continue
        if player_data["status"]['recruitLicense'] == 0: break
        if slot['state'] == 2:
            log(f"Found Unconfirmed Recruit:slot{i}")
            post('/gacha/finishNormalGacha', {"slotId": str(i)}, token)
        log(f"Found Empty Slot:{i}, tag: {slot['tags']}")
        tag_list, special_tag_id, duration = select_tag(slot['tags'])
        if (tag_list == []) and player_data["building"]["rooms"]["HIRE"]["slot_23"]["refreshCount"]:
            res = post('/gacha/refreshTags', {"slotId": i}, token)
            slot = res["playerDataDelta"]["modified"]["recruit"]["normal"]["slots"][str(i)]
            log(f"Refreshed Slot:{i}, tag: {slot['tags']}")
            player_data["building"]["rooms"]["HIRE"]["slot_23"]["refreshCount"] -= 1
            tag_list, special_tag_id, duration = select_tag(slot['tags'])
        if not (special_tag_id == 11):
            post('/gacha/normalGacha', {
                "slotId": str(i), "tagList": tag_list, "specialTagId": special_tag_id, "duration": duration
            }, token)
            player_data["status"]['recruitLicense'] -= 1


def auto_building(player_data, token):
    if datetime.date.today().isoweekday() % 2:
        post('/building/assignChar', {"roomSlotId": "slot_34", "charInstIdList": [244, 224, 257, 134, 132]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_26", "charInstIdList": [27]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_25", "charInstIdList": [46, 53, 205]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_24", "charInstIdList": [24, 201, 204]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_28", "charInstIdList": [193, 249, 165, 9, 253]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_36", "charInstIdList": [213, 160]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_16", "charInstIdList": [263]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_15", "charInstIdList": [141, 11, 22]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_14", "charInstIdList": [28, 29, 50]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_20", "charInstIdList": [60, 179, 94, 217, 97]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_23", "charInstIdList": [79]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_7", "charInstIdList": [98]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_6", "charInstIdList": [5, 2, 34]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_5", "charInstIdList": [15, 33, 92]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_9", "charInstIdList": [240, 10, 28, 12, 19]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_3", "charInstIdList": [42, 206, 178, 29, 50]}, token)
    else:
        post('/building/assignChar', {"roomSlotId": "slot_34", "charInstIdList": [128, 190, 170, 278, 280]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_26", "charInstIdList": [193]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_25", "charInstIdList": [249, 165, 9]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_24", "charInstIdList": [124, 135, 93]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_28", "charInstIdList": [192, 92, 151, 213, 27]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_36", "charInstIdList": [253, 60]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_16", "charInstIdList": [179]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_15", "charInstIdList": [94, 217, 97]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_14", "charInstIdList": [28, 29, 50]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_20", "charInstIdList": [263, 98, 79, 160, 34]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_23", "charInstIdList": [240]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_7", "charInstIdList": [10]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_6", "charInstIdList": [2, 12, 19]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_5", "charInstIdList": [42, 206, 178]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_9", "charInstIdList": [5, 205, 15, 33, 204]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_3", "charInstIdList": [24, 201, 141, 11, 46]}, token)

    post("/building/gainAllIntimacy", {}, token)
    post('/building/settleManufacture',
         {"roomSlotIdList": list(player_data["building"]["rooms"]["MANUFACTURE"].keys()), "supplement": 1}, token)
    post("/building/deliveryBatchOrder", {"slotList": list(player_data["building"]["rooms"]["TRADING"].keys())}, token)


def auto_social(player_data, token):
    if player_data["building"]["rooms"]["MEETING"]["slot_36"]["dailyReward"]:
        post('/building/getDailyClue', {}, token)
    t = []
    if player_data["building"]["rooms"]["MEETING"]["slot_36"]["socialReward"]["daily"]:
        t.append(0)
    if player_data["building"]["rooms"]["MEETING"]["slot_36"]["socialReward"]["search"]:
        t.append(1)
    if t:
        post('/building/getMeetingroomReward', {"type": t}, token)
    id_list = post('/building/getClueFriendList', {}, token)
    j = 0
    for i in id_list["result"]:
        if j == 10: break
        post('/building/visitBuilding', {"friendId": i["uid"]}, token)
        j += 1
    if len(player_data["building"]["rooms"]["MEETING"]["slot_36"]["board"]) == 7:
        post('/building/startInfoShare', {}, token)


def auto_campaign(player_data, token):
    stage_id = player_data["campaignsV2"]["open"]["rotate"]
    inst_id = 0
    for k, v in player_data["consumable"]["EXTERMINATION_AGENT"].items():
        if v["count"] > 0:
            inst_id = int(k)
            break
    if (player_data["campaignsV2"]["sweepMaxKills"].get(stage_id, 0) == 400) and inst_id \
            and (player_data["campaignsV2"]["campaignCurrentFee"] < player_data["campaignsV2"]["campaignTotalFee"]):
        post("/campaignV2/battleSweep", {"stageId": stage_id, "itemId": "EXTERMINATION_AGENT", "instId": inst_id},
             token)


def auto_gacha(player_data, token):
    for k, v in player_data["gacha"]["limit"].items():
        if v["leastFree"]:
            res = post("/gacha/advancedGacha", {"poolId": k, "useTkt": 3, "itemId": None}, token)
            # print_items(res["charGet"])


def mission_auto_confirm(token):
    post("/mission/autoConfirmMissions", {"type": "DAILY"}, token)
    post("/mission/autoConfirmMissions", {"type": "WEEKLY"}, token)


def auto_social_buy(player_data, token):
    friend_list = \
        post("/social/getSortListInfo", {"type": 1, "sortKeyList": ["level", "infoShare"], "param": {}}, token)[
            "result"]
    for index, friend in enumerate(friend_list):
        if index > 10: break
        post("/building/visitBuilding", {"friendId": friend["uid"]}, token)
    if player_data["social"]["yesterdayReward"]["canReceive"]:
        post("/social/receiveSocialPoint", {}, token)
    good_list = post("/shop/getSocialGoodList", {}, token)["goodList"]
    for good in good_list:
        if player_data["status"]["socialPoint"] >= good["price"]:
            post("/shop/buySocialGood", {"goodId": good['goodId'], "count": 1}, token)
            player_data["status"]["socialPoint"] -= good["price"]
def auto_activity(player_data, token):
    for k,v in player_data["activity"]["TYPE_ACT27SIDE"].items():
        if v["signedIn"]:
            continue
        post("/activity/act27side/nextDay", {"activityId":k}, token)
        post("/activity/act27side/saleStart", {"activityId":k}, token)
        post("/activity/act27side/purchase", {"activityId":k,"strategyIds":[2,2,2]}, token)
        post("/activity/act27side/sell", {"activityId":k,"price":45}, token)
        post("/activity/act27side/sell", {"activityId":k,"price":35}, token)
        post("/activity/act27side/sell", {"activityId":k,"price":950}, token)
        post("/activity/act27side/saleSettle", {"activityId":k}, token)

def auto_battle(player_data, token):
    post("/quest/battleStart",{"isRetro":0,"pry":0,"battleType":0,"continuous":None,"usePracticeTicket":0,"stageId":"main_01-07","squad":{"squadId":"0","name":None,"slots":[{"charInstId":78,"skillIndex":0,"currentEquip":"uniequip_002_myrtle"},{"charInstId":131,"skillIndex":1,"currentEquip":"uniequip_002_bpipe"},{"charInstId":72,"skillIndex":0,"currentEquip":"uniequip_001_elysm"},{"charInstId":176,"skillIndex":2,"currentEquip":"uniequip_002_mostma"},{"charInstId":79,"skillIndex":1,"currentEquip":"uniequip_002_amgoat"},{"charInstId":24,"skillIndex":2,"currentEquip":"uniequip_002_angel"},{"charInstId":141,"skillIndex":1,"currentEquip":"uniequip_002_plosis"},None,None,None,None,None]},"assistFriend":None,"isReplay":1,"startTs":time()},token)
    sleep(73)
    post("/quest/battleFinish",{},token)

def auto_ra(player_data, token):
    post("/sandboxPerm/sandboxV2/build",
         {"topicId": "sandbox_1", "itemId": "sandbox_1_tactical_22", "count": 62, "autoSquad": 1}, token)
    post("/sandboxPerm/sandboxV2/discardAp", {"topicId": "sandbox_1"}, token)
    post("/sandboxPerm/sandboxV2/nextDay", {"topicId": "sandbox_1"}, token)
    post("/sandboxPerm/sandboxV2/discardAp", {"topicId": "sandbox_1"}, token)
    post("/sandboxPerm/sandboxV2/nextDay", {"topicId": "sandbox_1"}, token)
    post("/sandboxPerm/sandboxV2/discardAp", {"topicId": "sandbox_1"}, token)
    res = post("/sandboxPerm/sandboxV2/nextDay", {"topicId": "sandbox_1"}, token)
    print(res["playerDataDelta"]["modified"]["tshop"]["sandbox_1"]["coin"])
    post("/sandboxPerm/sandboxV2/settleDay", {"topicId": "sandbox_1"}, token)
    sleep(30)
    post("/sandboxPerm/sandboxV2/toLoad", {"topicId": "sandbox_1"}, token)
    post("/sandboxPerm/sandboxV2/load", {"topicId": "sandbox_1", "day": 37}, token)
    post("/sandboxPerm/sandboxV2/settleDay", {"topicId": "sandbox_1"}, token)
