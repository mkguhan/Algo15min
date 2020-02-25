import requests
import json
import numpy as np
import pandas as pd
import csv

tokens = ["1000236,1000275"]

def login():
    try:
      payload = {'mediaType': 'application/x-www-form-urlencoded', 'UserId': 'Tdapi007', 'Password' : 'guhan007', 'Content-Type' : 'application/json','Provider': 'TRUEDATA' }
      response = requests.post('http://180.179.151.146/IDAUTH/Login.aspx', data = payload)
      response.content
      res_content = response.content.decode('utf-8').split('\n')
      return res_content[0], True
    except:
      return "Login Failure", False

def subscribe_token(auth_token):
    try:
      payload =tokens
      #json = {xauth,mediaType}
      headers = {'X-Authz' : auth_token}
      response = requests.post('http://180.179.151.146/mxds/idmdata.aspx?cmd=SNAPM,Tdapi007', data=json.dumps(payload),headers=headers)
      if response.status_code == 200:
          return True
      else:
          return False
    except:
      return False






    
