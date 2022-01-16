import threading
import requests
import random
import time
import json
import os
import re


class Brush_Box:
    def __init__(self, cookie):
        self.get_cookie = cookie
        self.betting_dog = False
        self.three = True
        self.one = True

    def get_box_data(self):
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"}
        url = "https://api.bilibili.com/x/garb/kuji/v3/box/next"
        response = requests.get(url, headers=header, cookies=self.get_cookie)
        print(response.json())
        code = int(response.json()['code'])
        return response.json()['data'] if code == 0 else None, code

    def judge_box_pay(self, data):
        number_list = [int(li['count']) for li in data['rewards']]
        l, s, a, b, c, d, e, f, g, h = tuple(number_list)
        print(l, s, a, b, c, d, e, f, g, h)
        box_number = sum(number_list[1:])
        if box_number == 1 and self.one:
            return True, 22
        if box_number == 3 and self.three:
            if self.betting_dog and s == 1:
                return True, 23
        return False, 0


class BUY:
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"}

    def __init__(self, buy_cookie):
        self.cookie = buy_cookie

    def get_pay_data(self, box_id, box_token, buy_number):
        data = {
            "box_id": str(box_id),
            "platform": "android",
            "draw_method": str(buy_number),
            "box_token": str(box_token),
            "device_info": json.dumps({}),
            "draw_num": "1",
            "is_draw_all": 0,
            "consume_lucky": "false",
            "invite_token": "",
            "multi_channel_pay": "true",
            "csrf": self.cookie['bili_jct']
        }
        url = "https://api.bilibili.com/x/garb/kuji/v3/trade/create"
        response = requests.post(url, headers=self.header, cookies=self.cookie, data=data)
        print(response.json())
        return json.loads(response.json()['data']['pay_data'])

    def pay_pay(self, data):
        url = "https://pay.bilibili.com/payplatform/pay/pay"
        data_json = {
            "appName": "tv.danmaku.bili",
            "appVersion": "6521000",
            "payChannelId": "99",
            "sdkVersion": "1.4.9",
            "payChannel": "bp"
        }
        data_json.update(data)

        response = requests.post(url, headers=self.header, json=data_json)
        print(response.json())
        cookie_set = response.headers['Set-Cookie']
        cookie_list = re.split(";", cookie_set)[0]
        pay_cookie = {"payzone": cookie_list.replace("payzone=", "")}
        json_data_ = json.loads(response.json()['data']['payChannelParam'])
        return pay_cookie, json_data_

    def payment(self, pay_cookie, json_data):
        url = "https://pay.bilibili.com/paywallet/pay/payBp"
        r1 = requests.post(url, cookies=pay_cookie, json=json_data, headers=self.header)
        print(r1.text)


class MAIN(BUY, Brush_Box):
    def __init__(self, cookie):
        BUY.__init__(self, cookie)
        Brush_Box.__init__(self, cookie)

    def box(self):
        box_data, code = self.get_box_data()
        if code == 26120:
            return code
        elif code == 0:
            box_judge, number = self.judge_box_pay(box_data)
            if box_judge:
                box_id, box_token = (box_data['box_id'], box_data['box_token'])
                pay_data = self.get_pay_data(box_id, box_token, number)
                pay_cookie, json_data = self.pay_pay(pay_data)
                print(pay_cookie, json_data)
                self.payment(pay_cookie, json_data)
                return True
            return code
        else:
            return code

    def start(self):
        a = 0
        while True:
            code = self.box()
            if code is True:
                break
            if code == 26120:
                time.sleep(2)
                a += 1
                if a >= 5:
                    print("好好好")
                    time.sleep(60 * 60)
            if code != 26120 and code != 0:
                print(code)
                break
            else:
                a = 0
                time.sleep(1)


if __name__ == '__main__':
    m = MAIN(json.loads(open("1701735549.json", "r", encoding="utf-8").read()))
    m.start()
