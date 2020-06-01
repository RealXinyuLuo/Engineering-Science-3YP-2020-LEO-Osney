import pandas as pd

def getconstantbuyprice(daywanted):
    
    data = {'Grid Buy Price':[14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4, 14.4]}
    
    Price = pd.DataFrame(data)
    
    Price.rename(index={0:'00:00',1:'01:00',2:'02:00',3:'03:00',4:'04:00',5:'05:00',6:'06:00',7:'07:00',8:'08:00',9:'09:00',10:'10:00',11:'11:00',12:'12:00',13:'13:00',14:'14:00',15:'15:00',16:'16:00',17:'17:00',18:'18:00',19:'19:00',20:'20:00',21:'21:00',22:'22:00',23:'23:00'}, inplace=True)
    
    Price = Price*0.01     # convert into £
    
    return Price


''' this is the old variable sell price for if the new one doesnt work '''


# def getvariablesellprice():
    
#     data = {'Grid Price':[7.15,7.15,7.15,7.15,7.15,7.15,7.15,7.6,7.6,7.6,7.6,7.6,7.6,7.6,7.6,7.6,7.6,16,16,16,7.6,7.6,7.15,7.15]}
    
#     Price = pd.DataFrame(data)
    
#     Price.rename(index={0:'00:00',1:'01:00',2:'02:00',3:'03:00',4:'04:00',5:'05:00',6:'06:00',7:'07:00',8:'08:00',9:'09:00',10:'10:00',11:'11:00',12:'12:00',13:'13:00',14:'14:00',15:'15:00',16:'16:00',17:'17:00',18:'18:00',19:'19:00',20:'20:00',21:'21:00',22:'22:00',23:'23:00'}, inplace=True)
    
#     Price = Price*0.01   # convert into £
    
#     return Price

''' this is the oly variable sell price for if the new one doesnt work '''

def getvariablebuyprice(daywanted):
    
    prices = pd.read_csv('Data/Midlands_agile_rates_2019.csv')
    
    prices = prices.iloc[::2]
    
    prices = prices.drop(['date','from','to','code','gsp','region_name','unit_rate_excl_vat'], axis = 1)
    
    prices.columns = ['Grid Buy Price']
    
    prices = prices[0+(daywanted)*24:24+(daywanted)*24]
    
    prices.rename(index={0+(daywanted)*24*2:'00:00',2+(daywanted)*24*2:'01:00',4+(daywanted*2)*24:'02:00',6+(daywanted*2)*24:'03:00',8+(daywanted*2)*24:'04:00',5*2+(daywanted*2)*24:'05:00',6*2+(daywanted*2)*24:'06:00',7*2+(daywanted*2)*24:'07:00',8*2+(daywanted*2)*24:'08:00',9*2+(daywanted*2)*24:'09:00',10*2+(daywanted*2)*24:'10:00',11*2+(daywanted*2)*24:'11:00',12*2+(daywanted*2)*24:'12:00',13*2+(daywanted*2)*24:'13:00',14*2+(daywanted*2)*24:'14:00',15*2+(daywanted*2)*24:'15:00',16*2+(daywanted*2)*24:'16:00',17*2+(daywanted*2)*24:'17:00',18*2+(daywanted*2)*24:'18:00',19*2+(daywanted*2)*24:'19:00',20*2+(daywanted*2)*24:'20:00',21*2+(daywanted*2)*24:'21:00',22*2+(daywanted*2)*24:'22:00',23*2+(daywanted*2)*24:'23:00'}, inplace=True)
    
    prices = prices*0.01     # convert into £

    return prices

def getconstantsellprice(daywanted):
    
    data = {'Grid Sell Price':[0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055, 0.055]}
    
    Price = pd.DataFrame(data)
    
    Price.rename(index={0:'00:00',1:'01:00',2:'02:00',3:'03:00',4:'04:00',5:'05:00',6:'06:00',7:'07:00',8:'08:00',9:'09:00',10:'10:00',11:'11:00',12:'12:00',13:'13:00',14:'14:00',15:'15:00',16:'16:00',17:'17:00',18:'18:00',19:'19:00',20:'20:00',21:'21:00',22:'22:00',23:'23:00'}, inplace=True)
    
    return Price

def getvariablesellprice(daywanted):
    
    prices = pd.read_csv('Data/midlands_outgoing_rates.csv')

    prices = prices.iloc[::2]

    prices = prices.drop(['local_time'], axis = 1)

    prices.columns = ['Grid Sell Price']

    prices = prices[0+(daywanted)*24:24+(daywanted)*24]

    prices.rename(index={0+(daywanted)*24*2:'00:00',2+(daywanted)*24*2:'01:00',4+(daywanted*2)*24:'02:00',6+(daywanted*2)*24:'03:00',8+(daywanted*2)*24:'04:00',5*2+(daywanted*2)*24:'05:00',6*2+(daywanted*2)*24:'06:00',7*2+(daywanted*2)*24:'07:00',8*2+(daywanted*2)*24:'08:00',9*2+(daywanted*2)*24:'09:00',10*2+(daywanted*2)*24:'10:00',11*2+(daywanted*2)*24:'11:00',12*2+(daywanted*2)*24:'12:00',13*2+(daywanted*2)*24:'13:00',14*2+(daywanted*2)*24:'14:00',15*2+(daywanted*2)*24:'15:00',16*2+(daywanted*2)*24:'16:00',17*2+(daywanted*2)*24:'17:00',18*2+(daywanted*2)*24:'18:00',19*2+(daywanted*2)*24:'19:00',20*2+(daywanted*2)*24:'20:00',21*2+(daywanted*2)*24:'21:00',22*2+(daywanted*2)*24:'22:00',23*2+(daywanted*2)*24:'23:00'}, inplace=True)

    prices = prices*0.01     # convert into £
    
    return prices