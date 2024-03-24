from time import time

import requests

from utils import select_tag

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
        for k in act:
            post('/activity/loginOnly/getReward', {"activityId": k}, token)
    if act := player_data["activity"]["CHECKIN_ONLY"]:
        for k, v in act.items():
            for index, value in enumerate(v["history"]):
                if value:
                    post('/activity/getActivityCheckInReward', {"activityId": k, "index": index}, token)
    # bless only
    if act := player_data["activity"]["BLESS_ONLY"]:
        for k, v in act.items():
            for index, value in enumerate(v["history"]):
                if value:
                    post('/activity/actBlessOnly/getCheckInReward', {"activityId": k, "index": index, "isFestival": 0},
                         token)
            for index, value in enumerate(v["festivalHistory"]):
                if value["state"] == 1:
                    post('/activity/actBlessOnly/getCheckInReward', {"activityId": k, "index": index, "isFestival": 1},
                         token)
    # pray only
    if act := player_data["activity"]["PRAY_ONLY"]:
        for k, v in act.items():
            post('/activity/prayOnly/getReward', {"activityId": k, "prayArray": list(range(1, v["prayDaily"] + 1))},
                 token)


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
        post('/mail/receiveAllMail', {"mailIdList": norm, "sysMailIdList": sys}, token)


def auto_recruit(player_data, token):
    for i in range(0, 4):
        slot = player_data["recruit"]['normal']['slots'][str(i)]
        if not slot['state']: continue
        if slot['maxFinishTs'] > time(): continue
        if player_data["status"]['recruitLicense'] == 0: break
        if slot['state'] == 2:
            post('/gacha/finishNormalGacha', {"slotId": str(i)}, token)
        tag_list, special_tag_id, duration = select_tag(slot['tags'])
        if (tag_list == []) and player_data["building"]["rooms"]["HIRE"]["slot_23"]["refreshCount"]:
            post('/gacha/refreshTags', {"slotId": i}, token)
        if not (special_tag_id == 11):
            post('/gacha/normalGacha', {
                "slotId": str(i), "tagList": tag_list, "specialTagId": special_tag_id, "duration": duration
            }, token)
            player_data["status"]['recruitLicense'] -= 1


def auto_building(player_data, token):
    for cid, d in player_data["building"]["chars"].items():
        if d["ap"] == 8640000: continue
        for i in range(10):
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
