#!/usr/bin/env python

import requests
from math import floor
from datetime import datetime
import time
import pathlib
import csv
import json
import hashlib
import hmac
from settings import BITFLYER_API_KEY, BITFLYER_API_SECRET

API_ENDPOINT = 'https://api.bitflyer.jp'


def str2json(s: str):
    return json.loads(s)


class BitFlyerPrvAPI:
    def __init__(self, api_key, api_secret, api_endpoint=API_ENDPOINT):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_endpoint = api_endpoint

    def get_api_call(self, path):
        method = 'GET'
        timestamp = str(time.time())
        text = timestamp + method + path
        sign = hmac.new(bytes(self.api_secret.encode('utf-8')),
                        bytes(text.encode('utf-8')),
                        hashlib.sha256).hexdigest()
        try:
            request_data = requests.get(
                self.api_endpoint + path,
                headers={
                    'ACCESS-KEY': self.api_key,
                    'ACCESS-TIMESTAMP': timestamp,
                    'ACCESS-SIGN': sign,
                    'Content-Type': 'application/json',
                }
            )
            return request_data
        except Exception as e:
            print(e)
            return None

    def post_api_call(self, path, body):
        body = json.dumps(body)
        method = 'POST'
        timestamp = str(time.time())
        text = timestamp + method + path + body
        sign = hmac.new(bytes(self.api_secret.encode('utf-8')),
                        bytes(text.encode('utf-8')),
                        hashlib.sha256).hexdigest()
        try:
            request_data = requests.post(
                self.api_endpoint + path,
                data=body,
                headers={
                    'ACCESS-KEY': self.api_key,
                    'ACCESS-TIMESTAMP': timestamp,
                    'ACCESS-SIGN': sign,
                    'Content-Type': 'application/json',
                }
            )
            return request_data
        except Exception as e:
            print(e)
            return None


# ltp: last traded price
def get_ltp(product_code='BTC_JPY'):
    url_ticker = f'/v1/getticker?product_code={product_code}'
    url = ''.join([API_ENDPOINT, url_ticker])
    try:
        res = requests.get(url)
        res = str2json(res.text)
        ltp = res['ltp']
        return ltp
    except Exception as e:
        print(e)
        return None


# 43200 sec: 30 days
# GTC: good till cancelled
def post_order(api_key, api_secret, price, size,
               product_code='BTC_JPY', child_order_type='LIMIT', side='BUY',
               minute_to_expire=43200, time_in_force='GTC'):
    url_order = f'/v1/me/sendchildorder'
    body = {
        "product_code": product_code,
        "child_order_type": child_order_type,
        'side': side,
        'price': price,
        'size': size,
        'minute_to_expire': minute_to_expire,
        'time_in_force': time_in_force,
    }
    try:
        api = BitFlyerPrvAPI(api_key, api_secret, API_ENDPOINT)
        res = api.post_api_call(url_order, body).json()
        return res
    except Exception as e:
        print(e)
        return None


def get_balance(api_key, api_secret):
    path = '/v1/me/getbalance'
    prv_api = BitFlyerPrvAPI(format(api_key), format(api_secret), API_ENDPOINT)
    balance = prv_api.get_api_call(path)
    return balance

def get_trade_history(api_key, api_secret, product_code='BTC_JPY', count=1000):
    path = f'/v1/me/getexecutions?product_code={product_code}&count={count}'
    prv_api = BitFlyerPrvAPI(format(api_key), format(api_secret), API_ENDPOINT)
    history = prv_api.get_api_call(path)
    return history


def main():
    # res = get_balance(BITFLYER_API_KEY, BITFLYER_API_SECRET)
    # print(json.dumps(str2json(res.text), indent=4))

    unit = 5000  # unit of rounding order
    dca_amount = 25000  # jpy to buy for each day
    log_file_path = pathlib.Path.home() / 'Devel/bitFlyer-dca/log.csv'  # log file path

    # Get last traded price and calculate amount
    ltp = get_ltp('BTC_JPY')
    if ltp % unit == 0:
        order_price = ltp - 2000
    else:
        order_price = unit * (ltp // unit)
    # find amount closest to dca amount on the 3rd decimal
    amount = dca_amount / order_price
    amount = floor(amount * 10 ** 3 + 0.5) / 10 ** 3
    t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Write to log file
    if log_file_path.exists():
        with open(log_file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([t, str(order_price), str(amount), str(ltp)])
    else:
        log_file_path.touch()
        with open(log_file_path, 'w+', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['time', 'order_price', 'amount', 'current_price'])
            writer.writerow([t, str(order_price), str(amount), str(ltp)])

    res = post_order(api_key=format(BITFLYER_API_KEY), api_secret=format(BITFLYER_API_SECRET), price=order_price, size=amount)
    print(res)


if __name__ == '__main__':
    main()
