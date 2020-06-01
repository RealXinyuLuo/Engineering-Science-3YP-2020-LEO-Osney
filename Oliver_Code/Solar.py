import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



def getsolarsupply(daywanted):
    
    efficiency = 0.2
    roofarea = 8000

    SOLAR = pd.read_csv('Data/oxon_solar_2014.csv')

    SOLAR = SOLAR[((daywanted-1)*24):(24+(daywanted-1)*24)]
    
    SOLAR['Total Supply (kWh)'] = SOLAR['kW']*roofarea*efficiency
    
    SOLAR.rename(index={0+(daywanted-1)*24:'00:00',1+(daywanted-1)*24:'01:00',2+(daywanted-1)*24:'02:00',3+(daywanted-1)*24:'03:00',4+(daywanted-1)*24:'04:00',5+(daywanted-1)*24:'05:00',6+(daywanted-1)*24:'06:00',7+(daywanted-1)*24:'07:00',8+(daywanted-1)*24:'08:00',9+(daywanted-1)*24:'09:00',10+(daywanted-1)*24:'10:00',11+(daywanted-1)*24:'11:00',12+(daywanted-1)*24:'12:00',13+(daywanted-1)*24:'13:00',14+(daywanted-1)*24:'14:00',15+(daywanted-1)*24:'15:00',16+(daywanted-1)*24:'16:00',17+(daywanted-1)*24:'17:00',18+(daywanted-1)*24:'18:00',19+(daywanted-1)*24:'19:00',20+(daywanted-1)*24:'20:00',21+(daywanted-1)*24:'21:00',22+(daywanted-1)*24:'22:00',23+(daywanted-1)*24:'23:00'}, inplace=True)
    
    SOLAR = SOLAR.drop(['Datetime','kW'], axis = 1)
    
    return SOLAR

def getinsolance(daywanted):
    
    SOLAR = pd.read_csv('Data/oxon_solar_2014.csv')
    SOLAR = SOLAR[((daywanted-1)*24):(24+(daywanted-1)*24)]
    
    SOLAR = SOLAR.drop(['Datetime'], axis = 1)
    
    return SOLAR
    

