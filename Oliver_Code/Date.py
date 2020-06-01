import pandas as pd
import numpy as np
from datetime import datetime
import datetime as dt



# creates the day in the year based on the date
def getdaywanted(datewanted):

#     from datetime import datetime
#     import datetime as dt

    datestring = datewanted
    date = datetime.strptime(datestring, '%m/%d/%Y')
    year = date.year
    month = date.month
    day = date.day
    daywanted = (dt.date(year, month, day) - dt.date(year,1,1)).days + 1
    return daywanted

# creates the date based on the day in the year
def getdatewanted(n, year):
    
#     dt = datetime.datetime(2019,1,1)
    
    deltat = datetime(year,1,1)
    
    dtdelta = dt.timedelta(days=(n-1))
    
    hello = deltat + dtdelta
    
    string = hello.strftime("%m/%d/%Y")
    
    return string


def createdate(n):
    
    dt = datetime.datetime(2019,1,1)
    
    dtdelta = datetime.timedelta(days=(n-1))
    
    hello = dt + dtdelta
    
    string = hello.strftime("%m/%d/%Y")
    
    return string


def getweekday(datewanted):
    
    month, day, year = (int(x) for x in datewanted.split('/'))
    ans = dt.date(year, month, day)
    
    return ans.weekday()

def getmonth(datewanted):
    
    month, day, year = (int(x) for x in datewanted.split('/'))
    ans = dt.date(year, month, day)
    
    return month