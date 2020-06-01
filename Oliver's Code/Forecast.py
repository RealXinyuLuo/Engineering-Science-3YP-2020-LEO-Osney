import requests
import pandas as pd
import numpy as np
import json
import datetime
import matplotlib.pyplot as plt
import Date


###    [T, UV] = forecastF("02/20/2020")   ## month / day / year     ### 


"""defining the functions """


def getData(timestamp):

    T = np.zeros(24)
    
    UV = np.zeros(24)

    date = str(timestamp)
    
#     st annes account = 2e3b8852d632edf46296b8e13bf6dc07
#     yahoo account = b70ca871df29d06201ed9d389f340c4e

    response = requests.get('https://api.darksky.net/forecast/2e3b8852d632edf46296b8e13bf6dc07/51.7520,1.2577,' + date)

    response = response.json()
    
    if len(response['hourly']['data']) <= 24:
        length = len(response['hourly']['data'])
    else:
        length = 24

    for n in range (0, length):

        T[n] = (response['hourly']['data'][n]['temperature'] - 32)*5/9
#         if len(response['hourly']['data'][9]) > 12:
#             UV[n] = response['hourly']['data'][n]['uvIndex']
        if 'uvIndex' in response['hourly']['data'][n]:
            UV[n] = response['hourly']['data'][n]['uvIndex']
        else:
            UV[n] = UV[n-1]
    
    if T[23] == 0:
        T[23] = T[22]
    
    return T, UV

def forecastF(date):

    date_string = date
    date = datetime.datetime.strptime(date_string, "%m/%d/%Y")
    timestamp = datetime.datetime.timestamp(date)
    timestamp = round(timestamp)
    
    
    
    return getData(timestamp)

def getSolarPower(UV):
    
    SolarPower = np.zeros(24)
    
    for n in range (24):
        SolarPower[n] = (104*UV[n]-18.365)/1000
        
    return SolarPower

def getcloudcover(daywanted):
    
#     date = Date.getdatewanted(daywanted, 2014)
#     date_string = date
#     date = datetime.datetime.strptime(date_string, "%m/%d/%Y")
#     timestamp = datetime.datetime.timestamp(date)
#     timestamp = round(timestamp)
#     date = str(timestamp)

#  #     st annes account = 2e3b8852d632edf46296b8e13bf6dc07
# #     yahoo account = b70ca871df29d06201ed9d389f340c4e   
    
#     response = requests.get('https://api.darksky.net/forecast/2e3b8852d632edf46296b8e13bf6dc07/51.7520,1.2577,' + date)
#     response = response.json()

# #     cloud_cover = np.zeros(24)
#     cloud_cover = []
#     for n in range(len(response['hourly']['data'])):
    

#         if 'cloudCover' in response['hourly']['data'][n]:
#             cloud_cover.append(response['hourly']['data'][n]['cloudCover'])
    
    data = pd.read_csv('Data/cloud_cover_2014.csv')
    
    cloud = data.iloc[daywanted-1][1]
    
    return cloud #np.sum(cloud_cover)