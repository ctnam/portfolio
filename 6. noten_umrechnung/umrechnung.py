# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 09:24:34 2025

@author: namtc
"""
# Case: DE-to-Polen –-> anerkennung_umrechnungstabelle.pdf Columns 1,3,5,8,10
import pandas as pd
data = pd.read_csv("C:/Users/namtc/Downloads/Online Application zum_Job/noten_umrechnung/gradeconversionchart_converted.csv")
#"gradeconversionchart_converted.csv" converted from "gradeconversionchart.csv"
#_converted indem: numerical values of grade multiplying 10 (*10)
corr_matrix = data.corr()
import seaborn as sns
sns.clustermap(corr_matrix)


de = data[['de']]
polen = data[['polen']]
from sklearn import linear_model #Linear regression
model = linear_model.LinearRegression() #Linear regression
model.fit(de,polen) #Linear regression fitting

import numpy as np
x=np.arange(15,16) #Input for the prediction is x=15 (originally need predict 1.5)
x=x.reshape(-1,1)  #Reshape to anpassung
result=model.predict(x) #Here is the final outcome result y towards x

