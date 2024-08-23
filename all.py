import json
import random
import string
import sys

import requests

from game import temp, post, auto_checkin, auto_mail, auto_recruit, auto_building, auto_social, auto_campaign, \
    mission_auto_confirm, auto_social_buy, auto_gacha,auto_ra,auto_activity
from utils import get_md5, u8_sign

phone = sys.argv[1]
pwd = sys.argv[2]


def get_res_version():
    return requests.get("https://ak-conf.hypergryph.com/config/prod/official/Android/version").json()


def get_token(device_id1, device_id2, device_id3, phone, pwd):
    token1 = requests.post("https://as.hypergryph.com/user/auth/v1/token_by_phone_password",
                           json={"phone": phone, "password": pwd}).json()["data"]["token"]
    token2 = requests.post(
        "https://as.hypergryph.com/user/oauth2/v2/grant",
        json={"token": token1, "appCode": "7318def77669979d", "type": 0}
    ).json()["data"]["code"]

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
    return get_token_data["token"], get_token_data["uid"]


resv = get_res_version()

device_id1 = get_md5(''.join(random.choices(string.ascii_letters + string.digits, k=12)))
device_id2 = '85' + ''.join(random.choices(string.digits, k=13))
device_id3 = get_md5(''.join(random.choices(string.ascii_letters + string.digits, k=12)))

token, uid = get_token(device_id1, device_id2, device_id3, phone, pwd)

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

if 0:
    for i in range(20):
        auto_ra(player_data,token)
        print(f"{i + 1}/20")
    print("ra finish")

# checkIn
if player_data["checkIn"]["canCheckIn"]:
    post('/user/checkIn', {}, token)
print("checkIn finish")
# activity
auto_checkin(player_data, token)

# mail
auto_mail(token)
print("mail finish")

# recruit


auto_recruit(player_data, token)
print("recruit finish")

# building
auto_building(player_data, token)

auto_social(player_data, token)

print("building finish")

# social
auto_social_buy(player_data, token)

print("social finish")

# campaignV2
auto_campaign(player_data, token)
print("campaign finish")
auto_gacha(player_data,token)

# mission
mission_auto_confirm(token)
print("mission finish")
#activity
auto_activity(player_data, token)
print("activity finish")