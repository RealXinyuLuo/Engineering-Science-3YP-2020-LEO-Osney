#!/usr/bin/env python
# coding: utf-8

# In[23]:


#################################
#           battery EV          #
#################################

__version__ = '0.3'

import pandas as pd
import numpy as np
from datetime import timedelta


# In[24]:


class price_profiles:
    def __init__(self,request_status):
        self.request_status = request_status
    
    def getProfiles(self):
        import_price1 = pd.read_csv('data/octopus_imprt_price_southern.csv', index_col=0,parse_dates=True,header = 0)
        export_price1 = pd.read_csv('data/octopus_export_price_southern.csv', index_col=0,parse_dates=True,header = 0)

        start_time1 = "2019-1-31 00:00:00"
        end_time1 = "2020-1-30 22:30:00"
        
        start_time2 = "2018-1-31 00:00:00"
        end_time2 = "2019-1-30 22:30:00"
        
        import_price2 =import_price1.loc[start_time1:end_time1]
        export_price2 =export_price1.loc[start_time2:end_time2]
        
        
        import_price3 = import_price2.between_time('09:00:00','16:30:00')
        export_price3 = export_price2.between_time('09:00:00','16:30:00')
        
        for column in import_price3 [['Import Rate (p/kWh)']]:
            import_price = import_price3[column] 
            import_price_value = import_price.values
            
        for column in export_price3 [['Outgoing Agile Rate (p/kWh)']]:
            export_price = export_price3[column]
            export_price_value = export_price.values 
            
        return import_price_value, export_price_value 


# In[25]:


class building_profiles:
    def __init__(self,request_status):
        self.request_status = request_status
        
        
    def getProfiles(self):
        excess_profile1 = pd.read_csv('data/Export_vector.csv', index_col=0, parse_dates=True)  # W/kWp
        excess_profile2 = excess_profile1.resample('0.5H').mean()
        excess_profile3 = excess_profile2.append(pd.DataFrame({excess_profile2.columns[0]: np.nan},
                                              index=[(excess_profile2.index[-1] +
                                                      timedelta(minutes=30))]))
        excess_profile4 = excess_profile3.interpolate()
        excess_profile5 = excess_profile4.between_time('09:00:00','16:30:00')
        excess_vector = excess_profile5.values


        import_profile1 = pd.read_csv('data/Import_vector.csv', index_col=0,parse_dates=True)  # W/kWp
        import_profile2 = import_profile1.resample('0.5H').mean()
        import_profile3 = import_profile2.append(pd.DataFrame({import_profile2.columns[0]: np.nan},
                                              index=[(import_profile2.index[-1] +timedelta(minutes=30))]))
        import_profile4 = import_profile3.interpolate()
        import_profile5 = import_profile4.between_time('09:00:00','16:30:00')
        import_vector = import_profile5.values
     
        return import_vector,excess_vector
        


# In[26]:


class control_class:
    def __init__(self,request_status):
        self.request_status = request_status
        
    def signalGen(self,import_price_value,export_price_value, max_buy_price, min_sell_price,import_vector,excess_vector):     
        T = len(import_price_value) 
        signal = np.zeros((T, 1))
        
        if self.request_status == 0:  
            for time,price in enumerate(import_price_value):
                if price < max_buy_price:   # Charge/Buys when price < Maximum_Buy_Price
                    signal[time] = 1
                else:
                    signal[time] = 0  # Set all other cases to "do nothing" first
                    
            for time,price in enumerate(export_price_value):
                if price > min_sell_price :  # Discharge/Sells when price > Minimum_Sell_Price 
                    signal[time] = -1 # Corrects some cases to sell electricity 
                
        elif self.request_status == 1:       
            for time,excess_amount in enumerate(excess_vector):
                if excess_amount > 0:   # Charge the batteries for free when excess generation 
                    signal[time] = 1
                else:
                    signal[time] = 0  # Set all other cases to "do nothing" first
                    
            for time,import_amount in enumerate(import_vector):
                if import_amount > 0 :  # Discharge when building in need for more electricity  
                    signal[time] = -1 # Corrects some cases to discharge
                #print(time,signal[time])
                
        return signal


# In[27]:


class EV_Component:
    def __init__(self):
        self.dispatch_type = "EV Component"
        self.capacity = 0
        self.install_cost = 0
        self.depreciation_cost = 1
        self.lifetime = 15    # Assume all components have a lifespan of 15 years 


# In[39]:


class EV_battery(EV_Component):
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
        
    def getOutput(self, signal,request_status,import_vector,excess_vector,energy_reserved):
        T = len(signal)
        output = np.zeros((T, 1))   # zero array of T rows, 1 column
        SOC_histrory = np.zeros((T, 1)) # to record historic SOC values 
        
        if request_status == 0:
            for time, signal_status in enumerate(signal):
                if time % 16 == 0:           # Reset the soc every morning at 9 am  
                    soc = self.capacity - 5  # Capacity minus the energy used for commuting to work 
                else:
                    soc = self.soc[time - 1]           
                if signal[time] == -1 and self.soc[time-1]>energy_reserved:       # Signal indicating selling/ Discharging 
                                                                # Whilst also reserving enough for traveling home
                    output[time] = min(self.power, self.eff*(soc-energy_reserved))
                    self.soc[time] = soc - (1/self.eff)*output[time]
                elif signal[time] == 1:  # Signal indicating buying/ Charging 
                    output[time] = max(-self.power, - (1/self.eff) * (self.capacity - soc))
                    self.soc[time] = soc - self.eff * output[time]        
                else:  # do nothing
                    self.soc[time] = soc
                SOC_histrory[time] = soc
            
        if request_status == 1:
            for time, signal_status in enumerate(signal):
                if time % 16 == 0:           # Reset the soc every morning at 9 am  
                    soc = self.capacity - 5  # Capacity minus the energy used for commuting to work 
                else:
                    soc = self.soc[time - 1]           
                if signal[time] == -1 and self.soc[time-1]>energy_reserved:       # Signal indicating discharging
                                                                # Whilst also reserving enough for traveling home
                    output[time] = min(self.power, self.eff*(soc-energy_reserved),self.eff*import_vector[time])
                    self.soc[time] = soc -(1/self.eff)*output[time]
                elif signal[time] == 1:  # Signal indicating Charging 
                    output[time] = max(-self.power, -(1/self.eff)*(self.capacity - soc),-(1/self.eff)*excess_vector[time])
                    self.soc[time] = soc - self.eff * output[time]        
                else:  # do nothing
                    self.soc[time] = soc
                SOC_histrory[time] = soc
                print(time,output[time],self.soc[time])
        return output, SOC_histrory
    
    def getGridCost(self, output, import_price_value, export_price_value,request_status,import_vector,excess_vector,SOC_histrory):
        cost_arr_size = len(output)
        cost_array = np.zeros((cost_arr_size, 1))   # zero array of T rows, 1 column
        system_output = np.zeros((cost_arr_size, 1)) 
        
        
        print('system output')
        for time, output_power in enumerate(output):
            
            if request_status == 0:
                if output[time] > 0:    # Positive output power, selling/discharging
                    cost_array[time] = - export_price_value[time]*output[time] #sell cost is negative
                elif output[time] < 0:  # Negative output power, buying/charging
                    cost_array[time] = - import_price_value[time]*output[time] #buy cost is positive           
                elif output[time] == 0:  # No power output, do nothing 
                    cost_array[time] = 0         
                #print(cost_array[time])
                
            if request_status == 1:
                if output[time] > 0:    # Positive output power, discharging to the buildings
                    # if building demand is not met, some electricity needs to be bought from grid
                    system_output[time] = -(import_vector[time]-output[time])
                    cost_array[time] = import_price_value[time]*(import_vector[time]-output[time]) #buy cost is positive
                elif output[time] < 0:  # Negative output power, charging from the excess of the builidngs 
                    # if building excess is too much, some electricity needs to be sold to grid
                    system_output[time] = -(-excess_vector[time]-output[time])
                    cost_array[time] = export_price_value[time]*(-excess_vector[time]-output[time]) #sell cost is negative         
                elif output[time] == 0 and SOC_histrory[time] == self.capacity:  # No power output due to battery full 
                    system_output[time] = excess_vector[time] # Export all excess 
                    cost_array[time] = -export_price_value[time]*excess_vector[time]          
                else:  # No power output, do nothing 
                    system_output[time] = 0
                    cost_array[time] = 0  
                    
                #print(time,cost_array[time]/100)
                print(time, system_output[time])
                
                
                
        grid_cost = np.sum(cost_array) # in pence 
        grid_cost_GBP = grid_cost/100  # convert to pounds
        print('Grid cost: £ %3.3f' % grid_cost_GBP)
        return grid_cost_GBP
    
    def getUserCost(self, output, import_price_value, export_price_value, request_status):
        cost_arr_size = len(output)
        user_cost_array = np.zeros((cost_arr_size, 1))   # zero array of T rows, 1 column
        
        for time, output_power in enumerate(output):
            if request_status == 1:
                if output[time] > 0 and export_price_value[time] > 7.678:
                    user_cost_array[time] = (export_price_value[time]+7.678)*output[time]
                elif output[time] < 0:  
                    user_cost_array[time] = 0        
                elif output[time] == 0: 
                    user_cost_array[time] = 0         
                #print(user_cost_array[time]/100)
                
        user_cost = np.sum(user_cost_array) 
        user_cost_GBP = user_cost/100  
        print('User cost: £ %3.3f' % user_cost_GBP)       
        return user_cost_GBP
    
    


# In[40]:


class V2G_Charger(EV_Component): 
    def __init__(self, install_cost = 0):
        super().__init__()
        self.asset_type = 'EV Charger'
        self.install_cost = install_cost * 100  # p/kWh


# In[41]:


#######################
##   Main Programme  ##
#######################
dt = 60/60 # One-hour intervals 
request_status = 1 # Buildings require electricity status

max_buy_price = 4
min_sell_price = 7
energy_reserved = 5


# In[42]:


# Price 
price_profiles1 = price_profiles(request_status)
import_price_value, export_price_value = price_profiles1.getProfiles()


# In[ ]:





# In[43]:


# Building Profiles 
building_profiles1 = building_profiles(request_status)
import_vector1,excess_vector1 = building_profiles1.getProfiles()


# In[ ]:





# In[44]:


# Control Signals
signal = control_class(request_status)
signal1 = signal.signalGen(import_price_value, export_price_value, max_buy_price, min_sell_price,import_vector1,excess_vector1)


# In[45]:


# Battery
battery_capacity = 60  # kWh
battery_power = 10  # kW
battery_eff = 0.8
battery_cost = 0 
battery_site1 = EV_battery(battery_capacity,battery_power,battery_eff, dt, battery_cost,signal1)
output1,SOC_histrory1 = battery_site1.getOutput(signal1,request_status,import_vector1,excess_vector1,energy_reserved)


# In[46]:


grid_cost =  battery_site1.getGridCost(output1, import_price_value, export_price_value, request_status, import_vector1,excess_vector1,SOC_histrory1)


# In[47]:


user_cost =  battery_site1.getUserCost(output1, import_price_value, export_price_value, request_status)


# In[ ]:





# In[ ]:





# In[ ]:




