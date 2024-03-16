import hashlib
import hmac


def get_md5(src):
    m1 = hashlib.md5()
    m1.update(src.encode('utf-8'))
    return m1.hexdigest()


def u8_sign(data):
    sign = hmac.new('91240f70c09a08a6bc72af1a5c8d4670'.encode(), data.encode(), hashlib.sha1)
    return sign.hexdigest()


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
