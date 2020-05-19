#!/usr/bin/env python
# coding: utf-8
# Version 2 of the control_class used foe V2G


__version__ = '0.3'
import pandas as pd
import numpy as np


class control_class:
    """
     Input
    ----
    request status from the buildings 
    
    Return
    ----
    a control signal
    """
    def __init__(self,request_status):
        self.request_status = request_status
        
    
    
    def signalGen(self,request_status):
        import_price1 = pd.read_csv('data/octopus_imprt_price_southern.csv', index_col=0,parse_dates=True,header = 0)
        export_price1 = pd.read_csv('data/octopus_export_price_southern.csv', index_col=0,parse_dates=True,header = 0)

        start_time = "2019-1-31 00:00:00"
        end_time = "2019-5-15 22:30:00"
        
        import_price2 =import_price1.loc[start_time:end_time]
        export_price2 =export_price1.loc[start_time:end_time]
        
        import_price3 = import_price2.between_time('09:00:00','16:30:00')
        export_price3 = export_price2.between_time('09:00:00','16:30:00')
        
        for column in import_price3 [['Import Rate (p/kWh)']]:
            import_price = import_price3[column] 
            import_price_value = import_price.values
            
        for column in export_price3 [['Outgoing Agile Rate (p/kWh)']]:
            export_price = export_price3[column]
            export_price_value = export_price.values
            
        
        T = len(import_price_value) 
        signal = np.zeros((T, 1))
        
                
        if request_status == 0:  
            for time,price in enumerate(import_price_value):
                if price < 5:       # Charge/Buys 
                    signal[time] = 1
                else:
                    signal[time] = 0  # Set all other cases to "do nothing" first
                    
            for time,price in enumerate(export_price_value):
                if price > 5 :       # Discharge/Sells
                    signal[time] = -1 # Corrects some cases to sell electricity 
                
        elif request_status == 1: 
            signal = np.zeros((T, 1))  # Always connected to the buildings in this verison 
                   
        return signal





request_status = 0
signal = control_class(request_status)
signal1 = signal.signalGen(request_status)
signal1




