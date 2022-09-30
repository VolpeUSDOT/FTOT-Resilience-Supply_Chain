# -*- coding: utf-8 -*-
"""
Created on Nov 14 00:21:23 2020

Purpose: generate scenarios for risk fators
Case Study: Forest residuals to jet fuel supplyc chain system in WA, OR, ID
Input: seismic catalog ("seismic_catalog.npy"); 

@author: Jie Zhao
"""

import numpy as np
import random
import math
import pandas as pd
import scipy.integrate as integrate

# added by Mark
import os
os.chdir("C:\FTOT-SCR\scenarios\ForestResiduals_SCR\input_data")

# read CSV files to obtain fault data
data_fault = pd.read_csv("FaultData.csv")
fault = pd. DataFrame (data_fault)
data_point = pd.read_csv("point.txt")
epicenter = pd. DataFrame (data_point)

# Total number of scenarios
Nscenario = 30
# Planning Horizon
Nt = 20
# Fault
Nf = 69
Mmin = 5.0
# generate 25 magnitudes for each fault, 
# Since eight faults that have not a- and b- value of Gutenberg–Richter distribution, 
# only the maximum magnitude is assigned for these faults/fault segments. 
# In this case,totally 25*60 + 9 =1509  earthquakes in the seismic catalog
Nearthquake = 1509
#======================Cumulative negative effect==========================
# catalyst replacement cost (in 2007 dollars):
Replacement_cost = 7257000 
# catalyst activity parameters: ass, kd
ass = [0.35,0.061,0.15,0.32,0.42,0.40,0.30,0.34,0.83,0.47]
ass_std = np.std(ass)
ass_mean = np.mean(ass)

kd_mean = 0.11
kd_std = 0.05
# catalyst activity function: a
def a(time, ass_para, kd_para):
    temp_value1 = 1/(1-ass_para)
    temp_value2 = kd_para*time + temp_value1
    a = 1/temp_value2 + ass_para   
    return a
# Threshold (catalyst activity rate) for change the catalyst
threshold = a(3,ass_mean, kd_mean)
#=====================Opportunity===========================================
# Assumptions: (a) Forest residuals to harvest ratio is constant value in planning horizon (2020-2040)
# (b) 83.3% of residuals are from softwood, and 16.7% from hardwood (PoS, 2019).
# 4 wood harvest policy scenarios: Base, Reduction in nonindustrial private forest area, Sequestered carbon in plantations,
# and Restoration thinning public land (Haynes et al. 2007)
# Reference: Richard W. Haynes, Darius M. Adams, Ralph J. Alig, Peter J. Ince, John R. Mills, and Xiaoping Zhou. (2007). 
#            The 2005 RPA Timber Assessment Update The 2005 RPA Timber Assessment Update.    
#            https://www.fs.fed.us/pnw/pubs/pnw_gtr699.pdf 


# The feedstock amount increase rate for 4 scenarios:
feedstock_rate = [[0.00181,0.00475],
                  [0.00178,0.00471],
                  [0.00186,0.00472],
                  [0.00215,0.00435]]

# ======================Sudden event==============================
seismic_catalog = np.load("seismic_catalog.npy")
total_prob = sum(seismic_catalog[:,6])

#====================Scenario generation===================================
# output arrays:
# row (50 scenarios), column (planning horizon), element is the remain rate of GFT conversion rate
earthquake_events = np.zeros((Nscenario,Nt))
# scenario_GFT: row (50 scenarios), column (planning horizon), element is the remain rate of GFT conversion rate
scenario_GFT = np.zeros((Nscenario, Nt))
temp_rate = np.zeros((Nscenario, Nt))# remain rate of GFT
CatalystReplace_cost = np.zeros((Nscenario, Nt)) #Catalyst replace cost 
# scenario_forest: row (50 scenarios), column (planning horizon), element is the increase rate of forest residuals
scenario_forest = np.zeros((Nscenario, Nt))
Policy = np.zeros((Nscenario, 1))# Policy scenario: 1-4
Year = np.zeros((Nscenario, 1))# Policy scenario occurrence year: 1-20

#---------------------earthquake scenario----------------------------------------
# whether earthquake occur at each year and scenario by Poisson Distribution
for i in range(Nscenario):
    earthquake_events[i,:] = np.random.poisson(total_prob, Nt)

seismic_prob_cdf = np.zeros(Nearthquake)
print(earthquake_events)
# CDF of seismic events in seismic catalog
for i in range(Nearthquake):
    if i ==0:
       seismic_prob_cdf[i]=seismic_catalog[i][6]
    else:
       seismic_prob_cdf[i]=seismic_catalog[i][6] + seismic_prob_cdf[i-1]

# select seismic events for the earthquake_events not equal to 0 based on CDF 
for i in range(Nscenario):
    for j in range(Nt):
        if int(earthquake_events[i][j]) != 0:
            Rrandom = random.random()
            RR = Rrandom*total_prob
            boolArr = seismic_prob_cdf > RR
            newArr = seismic_catalog[boolArr,:]
            selected_index = newArr[0][0]
            earthquake_events[i][j] = selected_index

print("Saving earthquake_events.npy")
np.save("earthquake_events.npy", earthquake_events) 

#---------------------GFT scenario-------------------------------------------
for i in range(Nscenario):  
    capacity_GFT = 1
    for j in range(Nt):
        ass_value = np.random.normal(ass_mean, ass_std, 1)
        kd_value = np.random.normal(kd_mean, kd_std, 1)
        year = 0
        if j == 0:
            scenario_GFT [i][j] = 1
            temp_rate[i][j] = 1
        else:
            if scenario_GFT [i][j-1] >= threshold: 
                year = year + 1
                temp_rate[i][j] = a(year,ass_value, kd_value)
                scenario_GFT [i][j] =capacity_GFT* temp_rate[i][j]
            else: 
                year = 0 
                scenario_GFT [i][j] = 1
                capacity_GFT = 1
                CatalystReplace_cost[i][j] = float(Replacement_cost)

print("Saving scenario_GFT.npy")           
np.save("scenario_GFT.npy", scenario_GFT) # this will be re-generated in FacilityCapacity.py

#------------------------Forest residuals scenarios------------------------------
for i in range(Nscenario):
    # Select the policy scenario
    Policy[i] = int(random.randint(1, 4))
    # Select the occurrence time of Policy
    Year[i]= random.randint(1, 20)
    if Policy[i] == 1:
        capacity_forest = 1
        for j in range(Nt):
            if j<=9: #2020-2030
                capacity_forest = (feedstock_rate[0][0] +1)*capacity_forest
                scenario_forest [i][j] = capacity_forest
            else:
                capacity_forest = (feedstock_rate[0][1] +1)*capacity_forest
                scenario_forest [i][j] = capacity_forest
    else:
        capacity_forest = 1
        for j in range(Nt):
            index = int(Policy[i])
            if j<=9: #2020-2030
                if j<=Year[i]:
                    capacity_forest = (feedstock_rate[0][0] +1)*capacity_forest 
                    scenario_forest [i][j] = capacity_forest
                else:
                    capacity_forest = (feedstock_rate[index-1][0] +1)*capacity_forest
                    scenario_forest [i][j] = capacity_forest
            else:
                if j<=Year[i]:
                    capacity_forest = (feedstock_rate[0][1] +1)*capacity_forest 
                    scenario_forest [i][j] = capacity_forest
                else:
                    capacity_forest = (feedstock_rate[index-1][1] +1)*capacity_forest 
                    scenario_forest [i][j] = capacity_forest

print("Saving scenario_forest.npy")           
np.save("scenario_forest.npy", scenario_forest)                


#====================Unused part=======================================
#---------------------earthquake scenario----------------------------------------
# scenario_earthquake: row (50 scenarios), 1st column (occurrence or not), 2nd column (occurrence year)
scenario_earthquake = np.zeros((Nscenario, 2))
# whether these scenarios occur earthquake
earthquake_50 = np.random.poisson(total_prob, 50)
for i in range (Nscenario):
    scenario_earthquake[i][0] = earthquake_50[i]
    if scenario_earthquake[i][0] == 1:
        scenario_earthquake[i][1] = random.randint(1, 20)
np.save("scenario_earthquake.npy", scenario_earthquake) 


