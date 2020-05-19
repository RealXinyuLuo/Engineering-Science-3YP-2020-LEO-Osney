#!/usr/bin/env python
# coding: utf-8

# In[2]:


#################################
#           battery EV          #
#################################

__version__ = '0.3'

import pandas as pd
import numpy as np
from datetime import timedelta


# In[3]:


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
                if price < 10:       # Charge/Buys 
                    signal[time] = 1
                else:
                    signal[time] = 0  # Set all other cases to "do nothing" first
                    
            for time,price in enumerate(export_price_value):
                if price > 10 :       # Discharge/Sells
                    signal[time] = -1 # Corrects some cases to sell electricity 
                
        elif request_status == 1: 
            signal = np.zeros((T, 1))  # Always connected to the buildings in this verison 
                   
        return signal


# In[4]:


class EV_Component:
    """EV Component base class"""
    def __init__(self):
        self.dispatch_type = "EV Component"
        self.capacity = 0
        self.install_cost = 0
        self.depreciation_cost = 0
        self.lifetime = 15    # Assume all components have a lifespan of 15 years 


# In[5]:


class EV_battery(EV_Component):
    """
    EV battery class

    Input
    -----
    Capacity : float
        Battery capacity, kWh.

    power : float
        Maximum power, kW.

    eff : float
        Charging/discharging efficiency between 0-1.

    dt : float
        Time interval (hours)

    T : int
        Number of intervales
    """
    def __init__(self, capacity, power, efficiency, dt, install_cost, signal):
        super().__init__()
        self.asset_type = 'EV Battery'
        self.capacity = capacity
        self.power = power * dt   # Convert kW to kWh
        self.eff = efficiency
        self.soc = np.ones(signal.size) * self.capacity
        self.install_cost = install_cost * 100  # p/kWh
        self.depreciation_cost = install_cost/self.lifetime
        self.signal = signal
        
    def getOutput(self, signal):
        """
        Battery control of charging/discharging in response to the signal

        Input
        -----
        Signal : numpy array

        Returns
        -------
        Battery energy use profile in kWh for each time interval : numpy array 
        """
  
        T = len(signal)
        output = np.zeros((T, 1))   # zero array of T rows, 1 column
        
        for time, signal_status in enumerate(signal):
            if time == 0:
                soc = self.capacity
            else:
                soc = self.soc[time - 1]
                
            if signal[time] == -1:    # Signal indicating selling/ Discharging 
                output[time] = min(self.power, self.eff*soc)
                self.soc[time] = soc - (1/self.eff)*output[time]
            elif signal[time] == 1:  # Signal indicating buying/ Charging 
                output[time] = max(-self.power, - (1/self.eff) * (self.capacity - soc))
                self.soc[time] = soc - self.eff * output[time]        
            elif signal[time] == 0:  # do nothing
                self.soc[time] = soc
            print(self.soc[time])
                
        return output   
         


# In[6]:


class V2G_Charger(EV_Component): 
    def __init__(self, install_cost = 0):
        super().__init__()
        self.asset_type = 'EV Charger'
        self.install_cost = install_cost * 100  # p/kWh


# In[7]:


dt = 30/60 


# In[8]:



request_status = 0


# In[9]:


signal = control_class(request_status)
signal1 = signal.signalGen(request_status)
signal1


# In[10]:



print(signal1.size)


# In[11]:



# Battery
battery_capacity = 65  # kWh
battery_power = 10  # kW
battery_eff = 0.8
battery_cost = 0 
battery_site1 = EV_battery(battery_capacity,battery_power,battery_eff, dt, battery_cost,signal1)
        


# In[12]:


output1 = battery_site1.getOutput(signal1)


# In[13]:


output1


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




