import hashlib
import hmac
import json
import random
import string
from time import time

import requests

temp = {}


def GetMd5(src):
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
token1 = requests.post(
    "https://as.hypergryph.com/user/auth/v1/token_by_phone_password",
    json={"phone": "13105612936", "password": "zhu159637"}
).json()["data"]["token"]
token2 = requests.post(
    "https://as.hypergryph.com/user/oauth2/v2/grant",
    json={"token": token1, "appCode": "7318def77669979d", "type": 0}
).json()["data"]["code"]
device_id1 = GetMd5(''.join(random.choices(string.ascii_letters + string.digits, k=12)))
device_id2 = '85' + ''.join(random.choices(string.digits, k=13))
device_id3 = GetMd5(''.join(random.choices(string.ascii_letters + string.digits, k=12)))
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
        post('/activity/prayOnly/getReward', {"activityId": k, "prayArray": list(range(1,v["prayDaily"]+1))}, token)

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
# social
if player_data["social"]["yesterdayReward"]["canReceive"]:
    post("/social/receiveSocialPoint", {}, token)

# TODO buy social good

print("social finish")


# recruit
def select_tag(tags):
    # TODO
    return [], 0, 32400


for i in range(0, 4):
    slot = player_data["recruit"]['normal']['slots'][str(i)]
    if not slot['state']: continue
    if slot['maxFinishTs'] > time(): continue
    if player_data["status"]['recruitLicense'] == 0: break
    if slot['state'] == 2:
        res = post('/gacha/finishNormalGacha', {"slotId": str(i)}, token)
    tag_list, special_tag_id, duration = select_tag(slot['tags'])
    post('/gacha/normalGacha',
         {"slotId": str(i), "tagList": tag_list, "specialTagId": special_tag_id, "duration": duration}, token)
print("recruit finish")
# building
"""
post("/building/gainAllIntimacy", {}, token)
if player_data["building"]["rooms"]["MEETING"]["slot_36"]["socialReward"]["daily"]:
    post('/building/getDailyClue', {}, token)
if player_data["building"]["rooms"]["MEETING"]["slot_36"]["socialReward"]["daily"]:
    post('/building/getMeetingroomReward', {"type": [0, 1]}, token)
"""
post('/building/settleManufacture',
     {"roomSlotIdList": list(player_data["building"]["rooms"]["MANUFACTURE"].keys()), "supplement": 1}, token)
post("/building/deliveryBatchOrder", {"slotList": list(player_data["building"]["rooms"]["TRADING"].keys())}, token)
print("building finish")
# mission
post("/mission/autoConfirmMissions", {"type": "DAILY"}, token)
post("/mission/autoConfirmMissions", {"type": "WEEKLY"}, token)
print("mission finish")
