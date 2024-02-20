
import os
import json
import time
import base64
import requests

import schedule
import pandas as pd
pd.set_option('display.max_rows', None)

import warnings
warnings.filterwarnings('ignore')

import numpy as np
from datetime import datetime
import time


from aevo import AevoClient
from clientConfig import CLIENT_CONFIG

from datetime import datetime
from loguru import logger as log



def get_data(symbol, bar):
    
    d = requests.get(f'https://www.okx.com/api/v5/market/index-candles?instId={symbol}&bar={bar}').json()
    data = pd.DataFrame(d['data'],columns=['timestamp','open','high','low','close','confirm'])
    data['timestamp'] = pd.to_datetime(data['timestamp'],utc=True, unit='ms')
    return data

# Add Credentials
aevo = AevoClient(**CLIENT_CONFIG)


c = 0
def run_bot():
    
    
    global c
    c+=1
    aevo.rest_cancel_all_orders()

    print(f"[CLEAR] clear existing positions {datetime.now().isoformat()}")
    while len(aevo.rest_get_data("positions")['positions'])>0:
        pos = aevo.rest_get_data("positions")['positions'][0]
        side = pos['side']
        amount = float(pos['amount'])

        if side == 'buy':
            aevo.rest_create_order(5197,False,float(aevo.get_orderbook('SOL-PERP')['asks'][0][0]),amount)
        else:
            aevo.rest_create_order(5197,True,float(aevo.get_orderbook('SOL-PERP')['bids'][0][0]),amount)
       
        time.sleep(10)
        aevo.rest_cancel_all_orders()

    
    print(f"[OREDER] epoch {c} time {datetime.now().isoformat()}")
    aevo.rest_create_order(5197,True,float(aevo.get_orderbook('SOL-PERP')['bids'][0][0]),10) 
    aevo.rest_create_order(5197,False,float(aevo.get_orderbook('SOL-PERP')['asks'][5][0]),10) 
    open_time = datetime.now()

    print(f"opentime {open_time.isoformat()} checking all position filled")

    while len(aevo.rest_get_data("positions")['positions'])>0 or len(aevo.rest_get_open_orders()) > 0 :
        print(f"{datetime.now().isoformat()} position not filled")
        if (datetime.now() - open_time).seconds > 60*10:
            print(f"[TIMEOUT] timeout {datetime.now().isoformat()}")
            break
        time.sleep(30)


while True:
    run_bot()
    time.sleep(1)