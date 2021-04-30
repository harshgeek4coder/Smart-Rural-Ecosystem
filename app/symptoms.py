import pandas as pd
data_sever='app/static/Medical/Symptom_severity.csv'
data_precaution='app/static/Medical/symptom_precaution.csv'
data_desc='app/static/Medical/symptom_Description.csv'
df_prec=pd.read_csv(data_precaution)
df_prec.columns=['Disease','Precaution1','Precaution2','Precaution3','Precaution4']

descr=pd.read_csv(data_desc)
descr.columns=['Disease','Description']


def get_precautions(disease):
    data=df_prec[df_prec['Disease']==disease]
    prec1=data['Precaution1'].values[0]
    prec2=data['Precaution2'].values[0]
    prec3=data['Precaution3'].values[0]
    prec4=data['Precaution4'].values[0]
    
    return prec1,prec2,prec3,prec4

def get_description(disease):
    data=descr[descr['Disease']==disease]
    
    des=data['Description'].values[0]   
    
    return des
    