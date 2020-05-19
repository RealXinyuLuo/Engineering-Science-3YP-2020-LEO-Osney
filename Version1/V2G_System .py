#!/usr/bin/env python
# coding: utf-8

# In[13]:


#################################
#           battery EV          #
#################################

__version__ = '0.3'

import pandas as pd
import numpy as np
from datetime import timedelta


# In[14]:


class control_class:
    """
     Input
    ----
    net energy price profile, request status from the buildings 
    
    Return
    ----
    a control signal
    """
    def __init__(self,net_price,request_status):
        self.net_price = net_price
        self.request_status = request_status
        
    
    
    def signalGen(self,net_price,request_status):
        
        T = len(net_price) 
        signal = np.zeros((T, 1))
        
        for time,price in enumerate(net_price):
            if price > 0 or request_status == 1: # Discharge/Sells 
                signal[time] = 0
            elif price <= 0:      # Charge/Buys 
                signal[time] = 1
        self.signal = signal       
        return signal


# In[15]:


class EV_Component:
    """EV Component base class"""
    def __init__(self):
        self.dispatch_type = "EV Component"
        self.capacity = 0
        self.install_cost = 0
        self.depreciation_cost = 0
        self.lifetime = 15    # Assume all components have a lifespan of 15 years 


# In[16]:


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
    def __init__(self, capacity, power, efficiency, dt, T, install_cost, signal):
        super().__init__()
        self.asset_type = 'EV Battery'
        self.capacity = capacity
        self.power = power * dt   # Convert kW to kWh
        self.eff = efficiency
        self.soc = np.ones(T) * self.capacity
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
            if signal[time] == 0:    # Signal indicating selling/ Discharging 
                output[time] = min(self.power, self.eff*soc)
                self.soc[time] = soc - (1/self.eff)*output[time]
            elif signal[time] == 1:  # Signal indicating buying/ Charging 
                output[time] = max(-self.power, - (1/self.eff) * (self.capacity - soc))
                self.soc[time] = soc - self.eff * output[time]        
            else:  # do nothing
                self.soc[time] = soc
            print(self.soc[time])
                
        self.output = output     
        return output   
         


# In[17]:


class V2G_Charger(EV_Component): 
    def __init__(self, install_cost = 0):
        super().__init__()
        self.asset_type = 'EV Charger'
        self.install_cost = install_cost * 100  # p/kWh


# In[18]:


dt = 30/60       # 30-minute time intervals 
T = int((24)/dt) # Number of intervals, T=48 intervals of 30 mins each 


# In[19]:



request_status = 0
net_price = [1,3,-1,-1,-1]


# In[ ]:





# In[20]:


signal = control_class(net_price,request_status)
signal1 = signal.signalGen(net_price,request_status)


# In[21]:



# Battery
battery_capacity = 65  # kWh
battery_power = 10  # kW
battery_eff = 0.8
battery_cost = 0 
battery_site1 = EV_battery(battery_capacity,battery_power,battery_eff, dt, T, battery_cost,signal1)
        


# In[22]:


output1 = battery_site1.getOutput(signal1)


# In[23]:


print(output1)


# In[24]:


T


# In[ ]:




