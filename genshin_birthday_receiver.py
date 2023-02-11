import requests
import sys
import requests.utils
import os
import json
import logging
URL_CALENDAR = "https://hk4e-api.mihoyo.com/event/birthdaystar/account/calendar?lang=zh-cn&badge_uid=%s&badge_region=%s&game_biz=%s&activity_id=20220301153521&year=2023"
URL_INDEX = "https://hk4e-api.mihoyo.com/event/birthdaystar/account/index?badge_uid=%s&badge_region=%s&game_biz=%s&lang=zh-cn&activity_id=20220301153521"
URL_ROLES = "https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookieToken?game_biz=hk4e_cn"
URL_RECEIVE = "https://hk4e-api.mihoyo.com/event/birthdaystar/account/post_my_draw?lang=zh-cn&badge_uid=%s&badge_region=%s&game_biz=%s&activity_id=20220301153521"
URL_ACCOUNT = "https://api-takumi.mihoyo.com/common/badge/v1/login/account"
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
if len(sys.argv)==3:
    print("Use sys.argv to get cookies input")
    if sys.argv[1]=="COOKIES":
        cookies = json.loads(sys.argv[2])["cookies"]
    else:
        cookies = [sys.argv[2],]
elif len(sys.argv)==2:
    print("Unexcepted format!")
else:
    print("Use os.environ to get cookies input")
    if "COOKIES" in os.environ:
        cookies = json.loads(os.environ["COOKIES"])["cookies"]
    else:
        cookies = [os.environ["COOKIE"],]
        
# multi-account
for cookie in cookies:
    session = requests.Session()
    session.cookies = requests.utils.cookiejar_from_dict(
        {i.split("=", 1)[0]: i.split("=", 1)[-1] for i in cookie.split("; ")}, cookiejar=None, overwrite=True)
    session.headers["User-Agent"] = requests.utils.default_user_agent()
    roles = session.get(URL_ROLES).json()
    logging.info(f"Got: {roles}")

    # multi-role
    for role in roles["data"]["list"]:
        uid = role["game_uid"]
        region = role["region"]
        gamebiz = role["game_biz"]
        get_url = URL_INDEX % (uid, region, gamebiz)
        rec_url = URL_RECEIVE % (uid, region, gamebiz)
        clnd_url = URL_CALENDAR % (uid, region, gamebiz)
        acc = session.post(URL_ACCOUNT, json={"game_biz": gamebiz, "lang": "zh-cn",
                                              "region": region, "uid": str(uid)})
        logging.info(f"Account: {acc.json()}")
        g = session.get(get_url).json()
        logging.info(f"Indexed: {g}")
        for i in g["data"]['role']:
            if i["is_partake"] == False:
                t = session.post(rec_url, str({"role_id": int(i['role_id'])}).replace("'", '"'),
                                 headers={"Content-Type": "application/json;charset=UTF-8",
                                          "Referer": "https://webstatic.mihoyo.com/"})
                logging.info(f"Received: {t.text}")
                logging.debug(f"成功给 {uid} 的账号领取{i['name']}的画册")
logging.debug("Run finished")
