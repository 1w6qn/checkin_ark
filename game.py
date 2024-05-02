from time import time

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
            res=post('/activity/loginOnly/getReward', {"activityId": k}, token)
            print_items(res["reward"])
    if act := player_data["activity"]["CHECKIN_ONLY"]:
        log("Found CheckinOnly Activity")
        for k, v in act.items():
            for index, value in enumerate(v["history"]):
                if value:
                    res=post('/activity/getActivityCheckInReward', {"activityId": k, "index": index}, token)
                    print_items(res["items"])
    # bless only
    if act := player_data["activity"]["BLESS_ONLY"]:
        log("Found BlessOnly Activity")
        for k, v in act.items():
            for index, value in enumerate(v["history"]):
                if value:
                    res=post('/activity/actBlessOnly/getCheckInReward', {"activityId": k, "index": index, "isFestival": 0},
                         token)
                    print_items(res["items"])

            for index, value in enumerate(v["festivalHistory"]):
                if value["state"] == 1:
                    res=post('/activity/actBlessOnly/getCheckInReward', {"activityId": k, "index": index, "isFestival": 1},
                         token)
                    print_items(res["items"])
    # pray only
    if act := player_data["activity"]["PRAY_ONLY"]:
        log("Found PrayOnly Activity")
        for k, v in act.items():
            res=post('/activity/prayOnly/getReward', {"activityId": k, "prayArray": list(range(1, v["prayDaily"] + 1))},
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
            if not act[k]["currentStatus"]:continue
            res = post('/activity/actCheckinAccess/getCheckInReward', {"activityId": k}, token)
            print_items(res["items"])


def auto_mail(token):
    mail_list = post('/mail/getMetaInfoList', {"from": int(time())}, token)['result']
    norm, sys = [], []
    for i in mail_list:
        if i['state'] or (not i['hasItem']): continue
        if i['type']:
            sys.append(i['mailId'])
        else:
            norm.append(i['mailId'])
    if not (norm and sys):
        res=post('/mail/receiveAllMail', {"mailIdList": norm, "sysMailIdList": sys}, token)
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
            post('/gacha/refreshTags', {"slotId": i}, token)
            log(f"Refreshed Slot:{i}, tag: {slot['tags']}")
        if not (special_tag_id == 11):
            post('/gacha/normalGacha', {
                "slotId": str(i), "tagList": tag_list, "specialTagId": special_tag_id, "duration": duration
            }, token)
            player_data["status"]['recruitLicense'] -= 1


def auto_building(player_data, token):
    for cid, d in player_data["building"]["chars"].items():
        if d["ap"] == 8640000: continue
        post('/building/assignChar', {"roomSlotId": "slot_9", "charInstIdList": [int(cid)]}, token)
        post('/building/assignChar', {"roomSlotId": "slot_9", "charInstIdList": []}, token)
        break
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
    id_list=post('/building/getClueFriendList', {}, token)
    j=0
    for i in id_list["result"]:
        if j == 10: break
        post('/building/visitBuilding', {"friendId": i["uid"]}, token)
        j+=1
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
    for k,v in player_data["gacha"]["limit"].items():
        if v["leastFree"]:
            res=post("/gacha/advancedGacha", {"poolId":k,"useTkt":3,"itemId":None}, token)
            #print_items(res["charGet"])

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
