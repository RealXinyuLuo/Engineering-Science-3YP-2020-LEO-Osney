import numpy as np


request_status = 0
net_price = [0,3,-1,-1,-1]

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

if __name__ == "__main__": 
    print ("Executed when invoked directly")
else: 
    print ("Executed when imported")