import requests
import json
import numpy as np
import pandas as pd
import csv
import time

#tokens = ["1000236", "1000275"]
ip = "180.179.151.146"
userid = "Tdapi007"

# ####
#Candle Stick Pattern
def is_shooting_star(data_s):
    open_p = data_s[0]
    close = data_s[3]
    high = data_s[1]
    low = data_s[2]
    lower_wick = open_p - low
    #Upper Wick Calculation
    upper_wick = high - close
    if open_p < 500:
      low_wick_per = 1
    else:
      low_wick_per = 1.5
    #Body Calculation
    Body = close - open_p
    #print("Low Wick: {} ;Body {} ; Upper Wick {}".format(lower_wick,Body,upper_wick))
    if open_p >= low and open_p < close:
      if lower_wick == 0 or lower_wick < low_wick_per:
          if upper_wick > (1.25 * Body):
              if lower_wick < Body:
                  #print("Open: {} High {} Low {} Close{}".format(open,high,low,close))
                  return True
              else:
                  return False
          else:
              return False
      else:
          return False
    else:
          return False


def is_hammer(data_s):
    open_p = data_s[0]
    close = data_s[3]
    high = data_s[1]
    low = data_s[2]
    if open_p < 500:
      low_wick_per = 1
    else:
      low_wick_per = 1.5
    if open_p > close and (close - low) < low_wick_per :
       if (1.75*(open_p-close)) < (high - open_p ) < (3.6*(open_p-close)):
            #print("Open: {} High {} Low {} Close{}".format(open_p,high,low,close))
            return True
       else:
            return False
    else:
       return False

def is_inverted_hammer(data_s):
    open_p = data_s[0]
    close = data_s[3]
    high = data_s[1]
    low = data_s[2]
    if open_p < 500:
       low_wick_per = 1
    else:
       low_wick_per = 1.5
    if open_p < close and (high - close) < low_wick_per:
       if (1.75*(close-open_p)) < (open_p - low) < (3.6*(close - open_p)):
          #print("Open: {} High {} Low {} Close{}".format(open_p, high, low, close))
          return True
       else:
          return False
    else:
        return False


def set_subscrip_token():
    script = pd.read_csv("scrip.csv", header=None)
    df = pd.read_csv('Master.txt', header=None, index_col=1, usecols=[0, 1, 5])
    token = []
    script_token = {}
    for i, j in script.iterrows():
        script_tok = df.loc[j[0]]
        token.append(script_tok[0])
        script_token[script_tok[0]] = j[0]
    return token, script_token


def login():
    try:
        payload = {'mediaType': 'application/x-www-form-urlencoded', 'UserId': userid, 'Password': 'guhan007',
                   'Content-Type': 'application/json', 'Provider': 'TRUEDATA'}
        url = "http://{}/IDAUTH/Login.aspx".format(ip)
        response = requests.post('http://180.179.151.146/IDAUTH/Login.aspx', data=payload)
        response.content
        res_content = response.content.decode('utf-8').split('\n')
        return res_content[0], True
    except:
        return "Login Failure", False


def subscribe_token(auth_token, tokens):
    try:
        payload = tokens
        # json = {xauth,mediaType}

        headers = {'X-Authz': auth_token}
        url = "http://{}/mxds/idmdata.aspx?cmd=SNAPM,{}".format(ip, userid)
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False


def get_tick_data(auth_token, token):
        # json = {xauth,mediaType}
        headers = {'X-Authz': auth_token}
        url = "http://{}/mxds/idticks.aspx?t={}&nd=0&p=0".format(ip, token)
        response = requests.get(url, headers=headers)
        return response.content.decode('utf-8').split('\r\n'), True



def write_toCsv(data_array, scrip):
    data_ar = []
    for data_arr in data_array:
        data_ar.append(data_arr.split(','))

    file_name = "{}.csv".format(scrip)
    csvfile = open(file_name, 'a', newline='')
    for da in data_ar:
            obj = csv.writer(csvfile, delimiter=',')
            obj.writerow(da)
    csvfile.close()

def convert_toDataFrame(scrip):
    url = "{}.csv".format(scrip)
    df = pd.read_csv(url, parse_dates=True, header=None,
                     names=["date", "tick", "Volume", "oi"])
    df = df.dropna()
    df['date'] = pd.to_datetime(df['date'])

    df.set_index('date', inplace=True)
    data_ohlc = df['tick'].resample('15Min').ohlc()
    return data_ohlc


if __name__ == "__main__":
    # Login to the TrueData
    # No Parameter need to pass, all are already
    # embedded
    print("Logging In to get the Data")
    auth_token, status = login()
    token, script_token = set_subscrip_token()
    if status:
        print("Logged IN")
        print("Subscribing the Scripts for Today")
        subscribe_scrip = subscribe_token(auth_token,token)
        if subscribe_scrip:
            print("Subscription Completed")
            count =0
            for scrip in token:
                if count == 10:
                    #time.sleep(70)
                    #count = 0
                    #print("Sleeping ...")
                    pass
                count = count + 1
                data, get_data_status = get_tick_data(auth_token, scrip)
                if get_data_status:
                    write_toCsv(data, scrip)
                else:
                    print("Error getting the Data for script {}".format(script_token[scrip]))
                ohlc15min = convert_toDataFrame(scrip)
                #print(script_token[scrip])
                #print(ohlc15min.iloc[0])
                data_915 = [ohlc15min.iloc[0]['open'], ohlc15min.iloc[0]['high'], ohlc15min.iloc[0]['low'], ohlc15min.iloc[0]['close']]
                #print(data_915)
                is_shooting_star_check = is_shooting_star(data_915)
                is_hammer_check = is_hammer(data_915)
                is_inverted_hammer_chk = is_inverted_hammer(data_915)
                if is_shooting_star_check:
                    openp = ohlc15min.iloc[0]['open']
                    if openp < 500:
                        target = ohlc15min.iloc[0]['close'] - 2
                    elif 500 < openp < 1000:
                        target = ohlc15min.iloc[0]['close'] - 4
                    elif 1000 < openp < 2000:
                        target = ohlc15min.iloc[0]['close'] - 8
                    else:
                        target = ohlc15min.iloc[-1]['close'] - 10
                    print("Strategy: Shooting Star;  Scrip Name: {}".format(script_token[scrip]))
                    print("Sell at {} ; Stop Loss {} ; Target {}".format(ohlc15min.iloc[0]['close'], ohlc15min.iloc[0]['high'],
                                                                         target))
                if is_hammer_check:
                    #print("Hammer")
                    open_p = ohlc15min.iloc[0]['open']
                    if open_p < 500:
                        target = ohlc15min.iloc[0]['close'] - 2
                    elif 500 < open_p < 1000:
                        target = ohlc15min.iloc[0]['close'] - 4
                    elif 1000 < open_p < 2000:
                        target = ohlc15min.iloc[0]['close'] - 8
                    else:
                        target = ohlc15min.iloc[0]['close'] - 10

                    print(" Strategy: Hammer;  Scrip Name: {}".format(script_token[scrip]))
                    print("Sell at {} ; Stop Loss {} ; Target {}".format(ohlc15min.iloc[0]['close'], ohlc15min.iloc[0]['high'],
                                                                         target))

                if is_inverted_hammer_chk:
                    #print("Inverted Hammer")
                    open_p = ohlc15min.iloc[-1]['open']
                    if open_p < 500:
                        target = ohlc15min.iloc[0]['close'] + 2
                    elif 500 < open_p < 1000:
                        target = ohlc15min.iloc[0]['close'] + 4
                    elif 1000 < open_p < 2000:
                        target = ohlc15min.iloc[0]['close'] + 8
                    else:
                        target = ohlc15min.iloc[0]['close'] + 10

                    print("Strategy: Inverted Hammer;  Scrip Name: {}".format(script_token[scrip]))
                    print("Buy at {} ; Stop Loss {} ; Target {}".format(ohlc15min.iloc[0]['close'], ohlc15min.iloc[0]['low'], target))

        else:
            print("Subscription Failure")
    else:
        print("Login Failure")