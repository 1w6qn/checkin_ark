import hashlib
import hmac
import json
import os
import random
import string
from time import time

import requests

temp = {}
phone=os.environ["PHONE"]
pwd=os.environ["PWD"]

def get_md5(src):
    m1 = hashlib.md5()
    m1.update(src.encode('utf-8'))
    return m1.hexdigest()

def u8_sign(data):
    sign = hmac.new('91240f70c09a08a6bc72af1a5c8d4670'.encode(), data.encode(), hashlib.sha1)
    return sign.hexdigest()


def post(cgi, data, token):
    res = requests.post('https://ak-gs-gf.hypergryph.com' + cgi, json=data, headers=temp[token])
    if 'seqnum' in res.headers.keys() and res.headers['seqnum'].isdigit():
        temp[token]["seqnum"] = res.headers['seqnum']
    else:
        temp[token]["seqnum"] = str(int(temp[token]["seqnum"]) + 1)
    return res.json()


resv = requests.get("https://ak-conf.hypergryph.com/config/prod/official/Android/version").json()

res = requests.post("https://as.hypergryph.com/user/auth/v1/token_by_phone_password",json={"phone": phone, "password": pwd}).json()
print(res)
token1 = res["data"]["token"]


token2 = requests.post(
    "https://as.hypergryph.com/user/oauth2/v2/grant",
    json={"token": token1, "appCode": "7318def77669979d", "type": 0}
).json()["data"]["code"]

device_id1 = get_md5(''.join(random.choices(string.ascii_letters + string.digits, k=12)))
device_id2 = '85' + ''.join(random.choices(string.digits, k=13))
device_id3 = get_md5(''.join(random.choices(string.ascii_letters + string.digits, k=12)))
get_token_req = {
    "appId": "1",
    "channelId": "1",
    "extension": json.dumps({"code": token2, "isSuc": True, "type": 1}),
    "worldId": "1",
    "platform": 1,
    "subChannel": "1",
    "deviceId": device_id1,
    "deviceId2": device_id2,
    "deviceId3": device_id3
}
sign_str = ''
for i in get_token_req:
    sign_str.join('{}={}&'.format(i, get_token_req[i]))
sign_ = u8_sign(sign_str[:-1])
get_token_req.update({"sign": sign_})
get_token_data = requests.post(
    "https://as.hypergryph.com/u8/user/v1/getToken",
    json=get_token_req
).json()
token = get_token_data["token"]
uid = get_token_data["uid"]

temp.update({
    token: {
        "uid": uid,
        "secret": "",
        "seqnum": "0",
        'Content-Type': 'application/json',
        'X-Unity-Version': '2017.4.39f1',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; X Build/V417IR)',
        'Connection': 'Keep-Alive'
    }
})
temp[token]["secret"] = post("/account/login", {
    "networkVersion": "5",
    "uid": uid,
    "token": token,
    "assetsVersion": resv["resVersion"],
    "clientVersion": resv["clientVersion"],
    "platform": 1,
    "deviceId": device_id1,
    "deviceId2": device_id2,
    "deviceId3": device_id3
}, token)["secret"]

player_data = post("/account/syncData", {"platform": 1}, token)["user"]
# checkIn
if player_data["checkIn"]["canCheckIn"]:
    post('/user/checkIn', {}, token)
print("checkIn finish")
# activity
# login only
if act := player_data["activity"]["LOGIN_ONLY"]:
    for k in act:
        post('/activity/loginOnly/getReward', {"activityId": k}, token)

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
        post('/activity/prayOnly/getReward', {"activityId": k, "prayArray": list(range(1, v["prayDaily"] + 1))}, token)

# mail
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
print("mail finish")


# recruit
def select_tag(tags):
    selected, sp, duration_ = [], 0, 32400
    if 11 in tags:
        sp = 11  # 6
    elif 14 in tags:
        sp = 14  # 5
        selected = [14]
    elif 27 in tags:
        selected = [27]
    elif 7 in tags and 12 in tags:
        selected = [7, 12]
    elif 7 in tags and 20 in tags:
        selected = [7, 20]
    elif 7 in tags and 23 in tags:
        selected = [7, 23]
    elif 7 in tags and 24 in tags:
        selected = [7, 24]
    elif 26 in tags and 19 in tags:
        selected = [26, 19]
    elif 26 in tags and 22 in tags:
        selected = [26, 22]
    elif 26 in tags and 3 in tags:
        selected = [26, 3]
    elif 26 in tags and 23 in tags:
        selected = [26, 23]
    elif 25 in tags and 12 in tags:
        selected = [25, 12]
    elif 25 in tags and 24 in tags:
        selected = [25, 24]
    elif 21 in tags and 24 in tags:
        selected = [21, 24]
    elif 9 in tags and 24 in tags:
        selected = [9, 24]
    elif 4 in tags and 24 in tags:
        selected = [4, 24]
    elif 13 in tags and 21 in tags:
        selected = [13, 21]
    elif 13 in tags and 6 in tags:
        selected = [4, 24]
    elif 13 in tags and 19 in tags and 10 in tags:
        selected = [13, 19, 10]
    elif 13 in tags and 19 in tags and 2 in tags:
        selected = [13, 19, 2]
    elif 12 in tags and 8 in tags:
        selected = [12, 8]
    elif 12 in tags and 18 in tags:
        selected = [12, 18]
    elif 12 in tags and 23 in tags:
        selected = [12, 23]
    elif 16 in tags and 8 in tags:
        selected = [16, 8]
    elif 16 in tags and 18 in tags:
        selected = [16, 18]
    elif 16 in tags and 5 in tags:
        selected = [16, 5]
    elif 16 in tags and 20 in tags:
        selected = [16, 20]
    elif 15 in tags and 6 in tags:
        selected = [15, 6]
    elif 15 in tags and 19 in tags:
        selected = [15, 19]
    elif 23 in tags and 19 in tags and 6 in tags:
        selected = [23, 19, 6]
    elif 19 in tags and 5 in tags:
        selected = [19, 5]
    elif 19 in tags and 21 in tags:
        selected = [19, 21]
    elif 19 in tags and 3 in tags:
        selected = [19, 3]
    elif 22 in tags and 1 in tags:
        selected = [22, 1]
    elif 22 in tags and 6 in tags:
        selected = [22, 6]
    elif 22 in tags and 10 in tags:
        selected = [22, 10]
    elif 22 in tags and 21 in tags:
        selected = [22, 21]
    elif 20 in tags and 22 in tags:
        selected = [20, 22]
    elif 20 in tags and 3 in tags:
        selected = [20, 3]
    elif 20 in tags and 5 in tags:
        selected = [20, 5]
    elif 7 in tags:
        selected = [7]  # 4
    elif 26 in tags:
        selected = [26]
    elif 24 in tags:
        selected = [24]
    elif 25 in tags:
        selected = [25]
    elif 12 in tags:
        selected = [12]
    elif 13 in tags:
        selected = [13]
    elif 16 in tags:
        selected = [16]
    elif 15 in tags and 8 in tags:
        selected = [15, 8]
    elif 15 in tags and 18 in tags:
        selected = [15, 18]
    elif 15 in tags and 5 in tags:
        selected = [15, 5]
    elif 15 in tags and 23 in tags:
        selected = [15, 23]
    elif 20 in tags and 2 in tags:
        selected = [20, 2]
    elif 20 in tags and 10 in tags:
        selected = [20, 10]
    elif 23 in tags and 19 in tags and 2 in tags:
        selected = [23, 19, 6]
    elif 23 in tags and 6 in tags:
        selected = [23, 6]
    elif 23 in tags and 2 in tags:
        selected = [23, 2]
    elif 23 in tags and 9 in tags:
        selected = [23, 9]
    elif 23 in tags and 1 in tags:
        selected = [23, 1]
    return selected, sp, duration_


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
print("recruit finish")
# building
post("/building/gainAllIntimacy", {}, token)

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
post('/building/settleManufacture',
     {"roomSlotIdList": list(player_data["building"]["rooms"]["MANUFACTURE"].keys()), "supplement": 1}, token)
post("/building/deliveryBatchOrder", {"slotList": list(player_data["building"]["rooms"]["TRADING"].keys())}, token)
print("building finish")
# social
friend_list=post("/social/getSortListInfo", {"type":1,"sortKeyList":["level","infoShare"],"param":{}}, token)["result"]
for index,friend in enumerate(friend_list):
    if index>10:break
    post("/building/visitBuilding", {"friendId": friend["uid"]}, token)
if player_data["social"]["yesterdayReward"]["canReceive"]:
    post("/social/receiveSocialPoint", {}, token)

good_list = post("/shop/getSocialGoodList", {}, token)["goodList"]
for good in good_list:
    if player_data["status"]["socialPoint"] >= good["price"]:
        post("/shop/buySocialGood", {"goodId": good['goodId'], "count": 1}, token)
        player_data["status"]["socialPoint"] -= good["price"]

print("social finish")

# campaignV2
stage_id = player_data["campaignsV2"]["open"]["rotate"]
inst_id = 0
for k, v in player_data["consumable"]["EXTERMINATION_AGENT"].items():
    if v["count"] > 0:
        inst_id = int(k)
        break

if (player_data["campaignsV2"]["sweepMaxKills"].get(stage_id, 0) == 400) and inst_id and (
        player_data["status"]["ap"] >= 25) \
        and (player_data["campaignsV2"]["campaignCurrentFee"] < player_data["campaignsV2"]["campaignTotalFee"]):
    post("/campaignV2/battleSweep", {"stageId": stage_id, "itemId": "EXTERMINATION_AGENT", "instId": inst_id}, token)
print("campaign finish")
# mission
post("/mission/autoConfirmMissions", {"type": "DAILY"}, token)
post("/mission/autoConfirmMissions", {"type": "WEEKLY"}, token)
print("mission finish")
