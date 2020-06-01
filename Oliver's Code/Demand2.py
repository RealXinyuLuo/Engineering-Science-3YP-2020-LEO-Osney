import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import Forecast
import Date




def getdaywanted(datewanted):

    from datetime import datetime
    import datetime as dt

    datestring = datewanted
    date = datetime.strptime(datestring, '%m/%d/%Y')
    year = date.year
    month = date.month
    day = date.day
    daywanted = (dt.date(year, month, day) - dt.date(year,1,1)).days + 1
    return daywanted




def getTESAdemand(daywanted):
    
    rows_to_keep = [0,daywanted]
    
    TESA_elec_demand = pd.read_csv('Data/TESA1718.csv', index_col='Date', skiprows = lambda x: x not in rows_to_keep)
    
    TESA_elec_demand = TESA_elec_demand.T
    
    return TESA_elec_demand




def getGAdemand(daywanted):

    rows_to_keep = [0,daywanted+2]

    GA_elec_demand = pd.read_csv('Data/CastleMillHousingArea_Elec_1617.csv', index_col='Date', skiprows = lambda x: x not in rows_to_keep)

    GA_elec_demand = GA_elec_demand.drop(['Meter Id','Site Code','Meter Reference'], axis = 1);
    
    GA_elec_demand = GA_elec_demand.T
    
    return GA_elec_demand



####    simple heat demand at the moment   ####

def getheatelecdemand():
    
    heat_demand = pd.read_csv('Data/simpleheatdemand.csv', index_col='Date')
    
    heat_demand = heat_demand.T
    
    return heat_demand




def gettotaldemand(daywanted):
    
    TESA = getTESAdemand(daywanted)
    
    GA = getGAdemand(daywanted)
    
#     Heat = getheatelecdemand()
    HEAT = getHEATdemand(daywanted)*0.25
    
    COOL = getCOOLdemand(daywanted)*0.25
    
    bigdata =pd.concat([TESA, GA, HEAT, COOL], axis=1)
    
    bigdata['Total Demand (kWh)'] = bigdata.sum(axis=1)
    
    bigdata.drop(bigdata.columns[[0, 1, 2, 3]], axis = 1, inplace = True) 
    
    bigdata = bigdata.drop("00:00.1", axis=0)
    
    return bigdata



## date in    %month / %day / %year    ##
def getrawHEATdemand(datewanted,annual):
    
    daywanted = Date.getdaywanted(datewanted)
    T = pd.read_csv('Data/Yearly_out_temp_2014.csv', usecols=[daywanted])
    
#     [T, UV] = Forecast.forecastF(datewanted)
    
#     T = pd.DataFrame(T)
    
    T.columns = ['Temp (°C)']
    
    T.rename(index={0:'00:00',1:'01:00',2:'02:00',3:'03:00',4:'04:00',5:'05:00',6:'06:00',7:'07:00',8:'08:00',9:'09:00',10:'10:00',11:'11:00',12:'12:00',13:'13:00',14:'14:00',15:'15:00',16:'16:00',17:'17:00',18:'18:00',19:'19:00',20:'20:00',21:'21:00',22:'22:00',23:'23:00'}, inplace=True)
    
    T['const'] = [18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5,18.5]
    
    T['diff'] = T['const']-T['Temp (°C)']
    
    T['Degree Days'] = T['diff']*(1/24)
    
    T['Raw Heating Demand (kWh)'] = T['Degree Days']*211.3*(annual/15)
    
    ## trying to include internal heat generation ##
    
#     T['Heating Demand (kWh)'] = T['Heating Demand (kWh)']-50
    
    ## trying to include internal heat generation ##
    
#     T['Heating Demand (kWh)'] = T['Heating Demand (kWh)'].clip(lower=0)
    
    T = T.drop(['Temp (°C)','const','diff','Degree Days'], axis = 1);
    
    return T


def getHEATdemand(daywanted,annual):
    
    datewanted = Date.getdatewanted(daywanted, 2014)
#     T = Demand.getrawHEATdemand(datewanted)
    T = getrawHEATdemand(datewanted,annual)
    
    ## GA internal generation ##
    T['GA Int Gen - Occupants(weekday)'] = [82.5,82.5,82.5,82.5,82.5,82.5,82.5,115,115,0,0,0,0,0,0,0,0,115,115,115,115,115,95,95]
    T['GA Int Gen - Occupants(weekday)'] = T['GA Int Gen - Occupants(weekday)']*500/1000
    T['GA Int Gen - Occupants(weekend)'] = [82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,115,115,115,115,115,115,115,115,115,115,115,95,95,95]
    T['GA Int Gen - Occupants(weekend)'] = T['GA Int Gen - Occupants(weekend)']*500/1000
    T['GA Int Gen - Lighting(weekday)'] = [0,0,0,0,0,0,0,10.166,10.166,0,0,0,0,0,0,0,0,10.166,10.166,10.166,10.166,10.166,10.166,10.166]
    T['GA Int Gen - Lighting(weekend)'] = [0,0,0,0,0,0,0,0,0,0,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166]
    T['GA Int Gen - Cooking(weekday)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,81,81,81,0,0,0,0]
    T['GA Int Gen - Cooking(weekday)'] = T['GA Int Gen - Cooking(weekday)']*500/1000
    T['GA Int Gen - Cooking(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,81,81,81,0,0,0,0]
    T['GA Int Gen - Cooking(weekend)'] = T['GA Int Gen - Cooking(weekday)']*500/1000
    T['GA Total Int Gen - weekday'] = T['GA Int Gen - Occupants(weekday)']+T['GA Int Gen - Lighting(weekday)']+T['GA Int Gen - Cooking(weekday)']
    T['GA Total Int Gen - weekend'] = T['GA Int Gen - Occupants(weekend)']+T['GA Int Gen - Lighting(weekend)']+T['GA Int Gen - Cooking(weekend)']
    T = T.drop(['GA Int Gen - Occupants(weekday)','GA Int Gen - Occupants(weekend)','GA Int Gen - Lighting(weekday)','GA Int Gen - Lighting(weekend)','GA Int Gen - Cooking(weekday)','GA Int Gen - Cooking(weekend)'], axis=1)

    ## TESA internal generation ##
    T['TESA Int Gen - Occupants(weekday)'] = [0,0,0,0,0,0,0,0,0,130,130,130,130,130,130,130,130,0,0,0,0,0,0,0]
    T['TESA Int Gen - Occupants(weekday)'] = T['TESA Int Gen - Occupants(weekday)']*750/1000
    T['TESA Int Gen - Occupants(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    T['TESA Int Gen - Lighting(weekday)'] = [0,0,0,0,0,0,0,0,10.8,10.8,10.8,10.8,10.8,10.8,10.8,10.8,10.8,0,0,0,0,0,0,0]
    T['TESA Int Gen - Lighting(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    T['TESA Int Gen - Monitors(weekday)'] = [0,0,0,0,0,0,0,0,17.475,17.475,17.475,17.475,17.475,17.475,17.475,17.475,17.475,0,0,0,0,0,0,0]
    T['TESA Int Gen - Monitors(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    T['TESA Int Gen - Computers(weekday)'] = [12.225,12.225,12.225,12.225,12.225,12.225,12.225,12.225,61.125,61.125,61.125,61.125,61.125,61.125,61.125,61.125,61.125,12.225,12.225,12.225,12.225,12.225,12.225,12.225]
    T['TESA Int Gen - Computers(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    T['TESA Total Int Gen - weekend'] = T['TESA Int Gen - Computers(weekend)']+T['TESA Int Gen - Monitors(weekend)']+T['TESA Int Gen - Lighting(weekend)']+T['TESA Int Gen - Occupants(weekend)']
    T['TESA Total Int Gen - weekday'] = T['TESA Int Gen - Computers(weekday)']+T['TESA Int Gen - Monitors(weekday)']+T['TESA Int Gen - Lighting(weekday)']+T['TESA Int Gen - Occupants(weekday)']
    T = T.drop(['TESA Int Gen - Computers(weekend)','TESA Int Gen - Computers(weekday)','TESA Int Gen - Monitors(weekend)','TESA Int Gen - Monitors(weekday)','TESA Int Gen - Lighting(weekend)','TESA Int Gen - Lighting(weekday)','TESA Int Gen - Occupants(weekend)','TESA Int Gen - Occupants(weekday)'], axis = 1)
    
    day = Date.getweekday(datewanted)
    ## if day = 3 or 4 then its the weekend 
    if day == 3 or day == 4:
        T['Heating Demand (kWh)'] = T['Raw Heating Demand (kWh)']-T['GA Total Int Gen - weekend']-T['TESA Total Int Gen - weekend']

    else:
        T['Heating Demand (kWh)'] = T['Raw Heating Demand (kWh)']-T['GA Total Int Gen - weekday']-T['TESA Total Int Gen - weekday']
        
    ## drop now useless columns
    T = T.drop(['Raw Heating Demand (kWh)','GA Total Int Gen - weekend','GA Total Int Gen - weekday','TESA Total Int Gen - weekend','TESA Total Int Gen - weekday'], axis = 1)
    
    T = T.clip(lower=0)
    
    return T

def getCOOLdemand(daywanted,annual):
    
    datewanted = Date.getdatewanted(daywanted, 2014)
#     T = Demand.getrawHEATdemand(datewanted)
    T = getrawHEATdemand(datewanted,annual)
    
    ## GA internal generation ##
    T['GA Int Gen - Occupants(weekday)'] = [82.5,82.5,82.5,82.5,82.5,82.5,82.5,115,115,0,0,0,0,0,0,0,0,115,115,115,115,115,95,95]
    T['GA Int Gen - Occupants(weekday)'] = T['GA Int Gen - Occupants(weekday)']*500/1000
    T['GA Int Gen - Occupants(weekend)'] = [82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,115,115,115,115,115,115,115,115,115,115,115,95,95,95]
    T['GA Int Gen - Occupants(weekend)'] = T['GA Int Gen - Occupants(weekend)']*500/1000
    T['GA Int Gen - Lighting(weekday)'] = [0,0,0,0,0,0,0,10.166,10.166,0,0,0,0,0,0,0,0,10.166,10.166,10.166,10.166,10.166,10.166,10.166]
    T['GA Int Gen - Lighting(weekend)'] = [0,0,0,0,0,0,0,0,0,0,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166]
    T['GA Int Gen - Cooking(weekday)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,81,81,81,0,0,0,0]
    T['GA Int Gen - Cooking(weekday)'] = T['GA Int Gen - Cooking(weekday)']*500/1000
    T['GA Int Gen - Cooking(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,81,81,81,0,0,0,0]
    T['GA Int Gen - Cooking(weekend)'] = T['GA Int Gen - Cooking(weekday)']*500/1000
    T['GA Total Int Gen - weekday'] = T['GA Int Gen - Occupants(weekday)']+T['GA Int Gen - Lighting(weekday)']+T['GA Int Gen - Cooking(weekday)']
    T['GA Total Int Gen - weekend'] = T['GA Int Gen - Occupants(weekend)']+T['GA Int Gen - Lighting(weekend)']+T['GA Int Gen - Cooking(weekend)']
    T = T.drop(['GA Int Gen - Occupants(weekday)','GA Int Gen - Occupants(weekend)','GA Int Gen - Lighting(weekday)','GA Int Gen - Lighting(weekend)','GA Int Gen - Cooking(weekday)','GA Int Gen - Cooking(weekend)'], axis=1)

    ## TESA internal generation ##
    T['TESA Int Gen - Occupants(weekday)'] = [0,0,0,0,0,0,0,0,0,130,130,130,130,130,130,130,130,0,0,0,0,0,0,0]
    T['TESA Int Gen - Occupants(weekday)'] = T['TESA Int Gen - Occupants(weekday)']*750/1000
    T['TESA Int Gen - Occupants(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    T['TESA Int Gen - Lighting(weekday)'] = [0,0,0,0,0,0,0,0,10.8,10.8,10.8,10.8,10.8,10.8,10.8,10.8,10.8,0,0,0,0,0,0,0]
    T['TESA Int Gen - Lighting(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    T['TESA Int Gen - Monitors(weekday)'] = [0,0,0,0,0,0,0,0,17.475,17.475,17.475,17.475,17.475,17.475,17.475,17.475,17.475,0,0,0,0,0,0,0]
    T['TESA Int Gen - Monitors(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    T['TESA Int Gen - Computers(weekday)'] = [12.225,12.225,12.225,12.225,12.225,12.225,12.225,12.225,61.125,61.125,61.125,61.125,61.125,61.125,61.125,61.125,61.125,12.225,12.225,12.225,12.225,12.225,12.225,12.225]
    T['TESA Int Gen - Computers(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    T['TESA Total Int Gen - weekend'] = T['TESA Int Gen - Computers(weekend)']+T['TESA Int Gen - Monitors(weekend)']+T['TESA Int Gen - Lighting(weekend)']+T['TESA Int Gen - Occupants(weekend)']
    T['TESA Total Int Gen - weekday'] = T['TESA Int Gen - Computers(weekday)']+T['TESA Int Gen - Monitors(weekday)']+T['TESA Int Gen - Lighting(weekday)']+T['TESA Int Gen - Occupants(weekday)']
    T = T.drop(['TESA Int Gen - Computers(weekend)','TESA Int Gen - Computers(weekday)','TESA Int Gen - Monitors(weekend)','TESA Int Gen - Monitors(weekday)','TESA Int Gen - Lighting(weekend)','TESA Int Gen - Lighting(weekday)','TESA Int Gen - Occupants(weekend)','TESA Int Gen - Occupants(weekday)'], axis = 1)
    
    day = Date.getweekday(datewanted)
    ## if day = 3 or 4 then its the weekend 
    if day == 3 or day == 4:
        T['Heating Demand (kWh)'] = T['Raw Heating Demand (kWh)']-T['GA Total Int Gen - weekend']-T['TESA Total Int Gen - weekend']

    else:
        T['Heating Demand (kWh)'] = T['Raw Heating Demand (kWh)']-T['GA Total Int Gen - weekday']-T['TESA Total Int Gen - weekday']
        
    ## drop now useless columns
    T = T.drop(['Raw Heating Demand (kWh)','GA Total Int Gen - weekend','GA Total Int Gen - weekday','TESA Total Int Gen - weekend','TESA Total Int Gen - weekday'], axis = 1)
    
    T['Cooling Demand (kWh)'] = T['Heating Demand (kWh)']
    
    T = T.drop(['Heating Demand (kWh)'], axis=1)
    
    T = T*(-1)
    
    T = T.clip(lower=0)
    
    return T

def TESA_HEAT(daywanted,people,annual):
    
    datewanted = Date.getdatewanted(daywanted, 2014)
    T = getrawHEATdemand(datewanted,annual)*(50.99/211.3)
    ## TESA internal generation ##
    T['TESA Int Gen - Occupants(weekday)'] = [0,0,0,0,0,0,0,0,0,130,130,130,130,130,130,130,130,0,0,0,0,0,0,0]
    T['TESA Int Gen - Occupants(weekday)'] = T['TESA Int Gen - Occupants(weekday)']*people/1000
    T['TESA Int Gen - Occupants(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    T['TESA Int Gen - Lighting(weekday)'] = [0,0,0,0,0,0,0,0,10.8,10.8,10.8,10.8,10.8,10.8,10.8,10.8,10.8,0,0,0,0,0,0,0]
    T['TESA Int Gen - Lighting(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    T['TESA Int Gen - Monitors(weekday)'] = [0,0,0,0,0,0,0,0,17.475,17.475,17.475,17.475,17.475,17.475,17.475,17.475,17.475,0,0,0,0,0,0,0]
    T['TESA Int Gen - Monitors(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    T['TESA Int Gen - Computers(weekday)'] = [12.225,12.225,12.225,12.225,12.225,12.225,12.225,12.225,61.125,61.125,61.125,61.125,61.125,61.125,61.125,61.125,61.125,12.225,12.225,12.225,12.225,12.225,12.225,12.225]
    T['TESA Int Gen - Computers(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    T['TESA Total Int Gen - weekend'] = T['TESA Int Gen - Computers(weekend)']+T['TESA Int Gen - Monitors(weekend)']+T['TESA Int Gen - Lighting(weekend)']+T['TESA Int Gen - Occupants(weekend)']
    T['TESA Total Int Gen - weekday'] = T['TESA Int Gen - Computers(weekday)']+T['TESA Int Gen - Monitors(weekday)']+T['TESA Int Gen - Lighting(weekday)']+T['TESA Int Gen - Occupants(weekday)']
    T = T.drop(['TESA Int Gen - Computers(weekend)','TESA Int Gen - Computers(weekday)','TESA Int Gen - Monitors(weekend)','TESA Int Gen - Monitors(weekday)','TESA Int Gen - Lighting(weekend)','TESA Int Gen - Lighting(weekday)','TESA Int Gen - Occupants(weekend)','TESA Int Gen - Occupants(weekday)'], axis = 1)

    day = Date.getweekday(datewanted)
    ## if day = 3 or 4 then its the weekend 
    if day == 3 or day == 4:
        T['Heating Demand (kWh)'] = T['Raw Heating Demand (kWh)']-T['TESA Total Int Gen - weekend']

    else:
        T['Heating Demand (kWh)'] = T['Raw Heating Demand (kWh)']-T['TESA Total Int Gen - weekday']

    ## drop now useless columns
    T = T.drop(['Raw Heating Demand (kWh)','TESA Total Int Gen - weekend','TESA Total Int Gen - weekday'], axis = 1)
    T = T.clip(lower=0)
    
    return T

def TESA_COOL(daywanted,people,annual):
    
    datewanted = Date.getdatewanted(daywanted, 2014)
    T = getrawHEATdemand(datewanted,annual)*(50.99/211.3)
    ## TESA internal generation ##
    T['TESA Int Gen - Occupants(weekday)'] = [0,0,0,0,0,0,0,0,0,130,130,130,130,130,130,130,130,0,0,0,0,0,0,0]
    T['TESA Int Gen - Occupants(weekday)'] = T['TESA Int Gen - Occupants(weekday)']*people/1000
    T['TESA Int Gen - Occupants(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    T['TESA Int Gen - Lighting(weekday)'] = [0,0,0,0,0,0,0,0,10.8,10.8,10.8,10.8,10.8,10.8,10.8,10.8,10.8,0,0,0,0,0,0,0]
    T['TESA Int Gen - Lighting(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    T['TESA Int Gen - Monitors(weekday)'] = [0,0,0,0,0,0,0,0,17.475,17.475,17.475,17.475,17.475,17.475,17.475,17.475,17.475,0,0,0,0,0,0,0]
    T['TESA Int Gen - Monitors(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    T['TESA Int Gen - Computers(weekday)'] = [12.225,12.225,12.225,12.225,12.225,12.225,12.225,12.225,61.125,61.125,61.125,61.125,61.125,61.125,61.125,61.125,61.125,12.225,12.225,12.225,12.225,12.225,12.225,12.225]
    T['TESA Int Gen - Computers(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    T['TESA Total Int Gen - weekend'] = T['TESA Int Gen - Computers(weekend)']+T['TESA Int Gen - Monitors(weekend)']+T['TESA Int Gen - Lighting(weekend)']+T['TESA Int Gen - Occupants(weekend)']
    T['TESA Total Int Gen - weekday'] = T['TESA Int Gen - Computers(weekday)']+T['TESA Int Gen - Monitors(weekday)']+T['TESA Int Gen - Lighting(weekday)']+T['TESA Int Gen - Occupants(weekday)']
    T = T.drop(['TESA Int Gen - Computers(weekend)','TESA Int Gen - Computers(weekday)','TESA Int Gen - Monitors(weekend)','TESA Int Gen - Monitors(weekday)','TESA Int Gen - Lighting(weekend)','TESA Int Gen - Lighting(weekday)','TESA Int Gen - Occupants(weekend)','TESA Int Gen - Occupants(weekday)'], axis = 1)

    day = Date.getweekday(datewanted)
    ## if day = 3 or 4 then its the weekend 
    if day == 3 or day == 4:
        T['Heating Demand (kWh)'] = T['Raw Heating Demand (kWh)']-T['TESA Total Int Gen - weekend']

    else:
        T['Heating Demand (kWh)'] = T['Raw Heating Demand (kWh)']-T['TESA Total Int Gen - weekday']

    ## drop now useless columns
    T = T.drop(['Raw Heating Demand (kWh)','TESA Total Int Gen - weekend','TESA Total Int Gen - weekday'], axis = 1)
    T = T*(-1)
    T = T.clip(lower=0)
    
    return T

def GA_HEAT(daywanted,annual):
    
    datewanted = Date.getdatewanted(daywanted, 2014)
    T = getrawHEATdemand(datewanted,annual)*(160.29/211.3)
    ## GA internal generation ##
    T['GA Int Gen - Occupants(weekday)'] = [82.5,82.5,82.5,82.5,82.5,82.5,82.5,115,115,0,0,0,0,0,0,0,0,115,115,115,115,115,95,95]
    T['GA Int Gen - Occupants(weekday)'] = T['GA Int Gen - Occupants(weekday)']*500/1000
    T['GA Int Gen - Occupants(weekend)'] = [82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,115,115,115,115,115,115,115,115,115,115,115,95,95,95]
    T['GA Int Gen - Occupants(weekend)'] = T['GA Int Gen - Occupants(weekend)']*500/1000
    T['GA Int Gen - Lighting(weekday)'] = [0,0,0,0,0,0,0,10.166,10.166,0,0,0,0,0,0,0,0,10.166,10.166,10.166,10.166,10.166,10.166,10.166]
    T['GA Int Gen - Lighting(weekend)'] = [0,0,0,0,0,0,0,0,0,0,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166]
    T['GA Int Gen - Cooking(weekday)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,81,81,81,0,0,0,0]
    T['GA Int Gen - Cooking(weekday)'] = T['GA Int Gen - Cooking(weekday)']*500/1000
    T['GA Int Gen - Cooking(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,81,81,81,0,0,0,0]
    T['GA Int Gen - Cooking(weekend)'] = T['GA Int Gen - Cooking(weekday)']*500/1000
    T['GA Total Int Gen - weekday'] = T['GA Int Gen - Occupants(weekday)']+T['GA Int Gen - Lighting(weekday)']+T['GA Int Gen - Cooking(weekday)']
    T['GA Total Int Gen - weekend'] = T['GA Int Gen - Occupants(weekend)']+T['GA Int Gen - Lighting(weekend)']+T['GA Int Gen - Cooking(weekend)']
    T = T.drop(['GA Int Gen - Occupants(weekday)','GA Int Gen - Occupants(weekend)','GA Int Gen - Lighting(weekday)','GA Int Gen - Lighting(weekend)','GA Int Gen - Cooking(weekday)','GA Int Gen - Cooking(weekend)'], axis=1)

    day = Date.getweekday(datewanted)
    ## if day = 3 or 4 then its the weekend 
    if day == 3 or day == 4:
        T['Heating Demand (kWh)'] = T['Raw Heating Demand (kWh)']-T['GA Total Int Gen - weekend']

    else:
        T['Heating Demand (kWh)'] = T['Raw Heating Demand (kWh)']-T['GA Total Int Gen - weekday']

    ## drop now useless columns
    T = T.drop(['Raw Heating Demand (kWh)','GA Total Int Gen - weekend','GA Total Int Gen - weekday'], axis = 1) 

    T = T.clip(lower=0)
    
    return T

def GA_COOL(daywanted,annual):
    
    datewanted = Date.getdatewanted(daywanted, 2014)
    T = getrawHEATdemand(datewanted,annual)*(160.29/211.3)
    ## GA internal generation ##
    T['GA Int Gen - Occupants(weekday)'] = [82.5,82.5,82.5,82.5,82.5,82.5,82.5,115,115,0,0,0,0,0,0,0,0,115,115,115,115,115,95,95]
    T['GA Int Gen - Occupants(weekday)'] = T['GA Int Gen - Occupants(weekday)']*500/1000
    T['GA Int Gen - Occupants(weekend)'] = [82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,115,115,115,115,115,115,115,115,115,115,115,95,95,95]
    T['GA Int Gen - Occupants(weekend)'] = T['GA Int Gen - Occupants(weekend)']*500/1000
    T['GA Int Gen - Lighting(weekday)'] = [0,0,0,0,0,0,0,10.166,10.166,0,0,0,0,0,0,0,0,10.166,10.166,10.166,10.166,10.166,10.166,10.166]
    T['GA Int Gen - Lighting(weekend)'] = [0,0,0,0,0,0,0,0,0,0,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166,10.166]
    T['GA Int Gen - Cooking(weekday)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,81,81,81,0,0,0,0]
    T['GA Int Gen - Cooking(weekday)'] = T['GA Int Gen - Cooking(weekday)']*500/1000
    T['GA Int Gen - Cooking(weekend)'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,81,81,81,0,0,0,0]
    T['GA Int Gen - Cooking(weekend)'] = T['GA Int Gen - Cooking(weekday)']*500/1000
    T['GA Total Int Gen - weekday'] = T['GA Int Gen - Occupants(weekday)']+T['GA Int Gen - Lighting(weekday)']+T['GA Int Gen - Cooking(weekday)']
    T['GA Total Int Gen - weekend'] = T['GA Int Gen - Occupants(weekend)']+T['GA Int Gen - Lighting(weekend)']+T['GA Int Gen - Cooking(weekend)']
    T = T.drop(['GA Int Gen - Occupants(weekday)','GA Int Gen - Occupants(weekend)','GA Int Gen - Lighting(weekday)','GA Int Gen - Lighting(weekend)','GA Int Gen - Cooking(weekday)','GA Int Gen - Cooking(weekend)'], axis=1)

    day = Date.getweekday(datewanted)
    ## if day = 3 or 4 then its the weekend 
    if day == 3 or day == 4:
        T['Heating Demand (kWh)'] = T['Raw Heating Demand (kWh)']-T['GA Total Int Gen - weekend']

    else:
        T['Heating Demand (kWh)'] = T['Raw Heating Demand (kWh)']-T['GA Total Int Gen - weekday']

    ## drop now useless columns
    T = T.drop(['Raw Heating Demand (kWh)','GA Total Int Gen - weekend','GA Total Int Gen - weekday'], axis = 1) 
    
    T = T*(-1)

    T = T.clip(lower=0)
    
    return T