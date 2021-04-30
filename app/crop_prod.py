import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from numpy import array
from tensorflow.keras.models import load_model
from sklearn.metrics import confusion_matrix
import datetime
import calendar

def get_train():
    data = pd.read_csv("static/Crop Prod/train.csv",usecols = ['Avg Month Temp'])
    df=data.values
    X=df
    data = pd.read_csv("static/Crop Prod/train.csv",usecols = ['Ratio'])
    df=data.values
    y=df
    # print("Y NEW SHAPE :",y.shape)
    X = np.reshape(X, (X.shape[0], 1, X.shape[1]))
    y = np.reshape(y, (y.shape[0]))
    # print("Y NEW CHANGED SHAPE :",y.shape)
    # print("X NEW :",X)
    # print("Y NEW :",y)
    return X, y
def get_test():
    data = pd.read_csv("static/Crop Prod/test.csv",usecols = ['Avg Month Temp'])
    df=data.values
    X=df
    data = pd.read_csv("static/Crop Prod/test.csv",usecols = ['Ratio'])
    df=data.values
    y=df
    # print("Y NEW SHAPE :",y.shape)
    X = np.reshape(X, (X.shape[0], 1, X.shape[1]))
    y = np.reshape(y, (y.shape[0]))
    # print("Y NEW CHANGED SHAPE :",y.shape)
    # print("X NEW :",X)
    # print("Y NEW :",y)
    return X, y



now = datetime.datetime.now()
year=now.year
month=now.month
day=now.day
one=year%10
print(one)
year=year/10
two=int(year%10)
print(two)
yr=two*10+one
print("Day ",day,"Month ",month,"Year ",yr)
monthname=calendar.month_name[(month+1)%12]
print("https://www.accuweather.com/en/in/ratnagiri/189289/"+str(monthname.lower())+"-weather/189289?monyr="+str((month+1)%12)+"/"+str(day)+"/"+str(yr)+"&view=table")
model = load_model('static/Crop Prod/lstm_model.h5')

def get_estimate_yield(temp,area):
    X,ytrain=get_train()
    X,ytest = get_test()
    weather=float(temp)
    area=float(area)
    
    X=np.array([[[weather]]],np.float32)
    ytest = model.predict(X, verbose=0)

    yvalue=ytest[0]
    ratio=yvalue[0]
    
    possible_prod=area*ratio

    if possible_prod>100000:
        value=True
    else:
        value=False
    
    if value==True:
        st="This Crop Seems Good Enough to Get Profit"
    else:
        st="This Crop doesn't seem to have a Good Profit"

    possible_prod=round(possible_prod,2)

    
    return possible_prod,st

    
    