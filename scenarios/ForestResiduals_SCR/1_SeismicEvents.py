# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 09:02:28 2020

Case Study: Forest residuals to jet fuel supplyc chain system in WA, OR, ID
Purpose: generate seismic scenarios based on Importance Sampling 

Input: fault data ("FaultData.csv"); epicenter data ("point.txt")

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
# 7 parameters we need: event ID, fault's objetive ID, magnitude, epicenter lat, long, depth, hazard-consistent probability
Npara = 7

# Load earthquake_scenario array:
# earthquake_scenario = np.load("earthquake_scenario.npy")

# -------------------------------------Variables---------------------------
# earthquale catalog array: row (events); column (parameters)
seismic_catalog = np.zeros((Nearthquake, Npara))

# PDF of magnitude for this fault based on G-R distrubution:
def f_magnitude(fault_ID, m):
    b_value = float(fault.values[fault_ID][5])
    Mmax = float(fault.values[fault_ID][2])
    numerator = b_value * (math.log(10)) * (10**(-b_value*(m-Mmin)))
    denominator = 1-10**(-b_value*(Mmax-Mmin))
    f_magnitude = numerator/(denominator+0.01)
    
    return f_magnitude
# print(f_magnitude(41, 6.5)); for test

# Sampling Distribution
def g_magnitude(fault_ID):
    Mmax = float(fault.values[fault_ID][2])
    # partitions for sampling distribution: 
    if 5.0 <= Mmax < 6.5:
        Nm = int ((Mmax-5)/0.3) +1
    elif 6.5 <= Mmax < 7.25:
        Nm = int ((Mmax-6.5)/0.15) +1 +5
    elif Mmax>= 7.25:
        Nm = int ((Mmax-7.25)/0.05) +1 +5 +5
    # Sampling distribution: g_magnitude
    g_magnitude = 1/float(Nm) 
    return g_magnitude


# Magnitude partition in sampling distribution
def magnitude_partition(fault_ID):
    magnitude_partition = []
    Mmax = float(fault.values[fault_ID][2])
    # partitions for sampling distribution: 
    if 5.0 <= Mmax < 6.5:
        magnitude_partition = np.arange(5.0,Mmax,0.3)
        magnitude_partition = np.append(magnitude_partition, Mmax)
    elif 6.5 <= Mmax < 7.25:
        magnitude_partition = np.arange(5,6.5,0.3)
        magnitude_partition = np.append (magnitude_partition, np.arange(6.5,Mmax,0.15))
        magnitude_partition = np.append(magnitude_partition, Mmax)
    else:
        magnitude_partition = np.arange (5,6.5,0.3)
        magnitude_partition = np.append (magnitude_partition, np.arange(6.5,7.25,0.15))
        magnitude_partition = np.append (magnitude_partition, np.arange(7.25,Mmax,0.05))
        magnitude_partition = np.append(magnitude_partition, Mmax)
    return magnitude_partition


# IS_weight:
def IS_weight(fault_ID):
    IS_weight = np.zeros((len(magnitude_partition(fault_ID))-1))
    for i in range(len(IS_weight)):
        m_lower = magnitude_partition(fault_ID)[i]
        m_upper = magnitude_partition(fault_ID)[i+1]
        IS_weight_numerator = integrate.quad(lambda m: f_magnitude(fault_ID,m), m_lower, m_upper)
        IS_weight_denominator = g_magnitude(fault_ID)
        IS_weight[i] = IS_weight_numerator[0]/IS_weight_denominator 
    # Normalized:
    IS_weight = IS_weight/(sum(IS_weight[:]))
        
    return IS_weight

#print(IS_weight(56))# for test
 
#CDF of IS weight
def IS_CDF(fault_ID):
    IS_CDF = np.zeros(len(IS_weight(fault_ID)))
    #size = len(Prob)
    for l in range(len(IS_CDF)):
        if l == 0:
            IS_CDF[l] = IS_weight(fault_ID)[0]
        else:
            IS_CDF[l] = IS_weight(fault_ID)[l] + IS_CDF[l-1]    
    return IS_CDF 
#print(fault.values[1][4])
    
"""
#================Test=================================================
test_list= epicenter.loc[epicenter['fault_id'] == 871]
va = len(test_list)
print(va)
test_selected = int(random.uniform(1, va))
test_X = test_list.values[test_selected][25]
test_Y = test_list.values[test_selected][26]
print(test_X,test_Y)

"""
"""
# =======================================Unused part========================
# ------------------------------------Process--------------------------------
# Generate the earthquake parameters
for k in range(Ns):
    for j in range(Nt):
        for i in range(Nf):
            # a random number, R_random, between 0 and 1 is generated from a uniform distribution
            # annual probability of occurrence, modeled as a Poisson model
            # if the R_random is less than the annual probability of occurrence, earthquake occurrence
            # if earthquake occurrence:
            if earthquake_scenario[i][j][k] == 1:
                # if fault doesn't have a- & b- value, give a maximum magnitude
                if fault.values[i][4] == 0:
                    magnitude[i][j][k] = fault.values[i][2]
                #if not, magnitude is determined by a random number, K_random, and IS weight
                else:
                    # 1. generate a random number
                    K_random = random.random()
                    # 2. CDF of IS weight:
                    # IS_CDF = IS_CDF(i)
                    # generate magnitude based on IS weight:
                    selected = np.nonzero(IS_CDF(i)>K_random)
                    lower_magnitude = float(magnitude_partition(i)[len(IS_CDF(i))-len(selected[0])])
                    upper_magnitude = float(magnitude_partition(i)[len(IS_CDF(i))-len(selected[0])+1])
                    # generate earthquake magnitude between lower-and upper bounder with 0.01 interval
                    magnitude[i][j][k] = random.uniform(lower_magnitude, upper_magnitude)
                    # Hazard-Consistent Probability:
                    P_occurrence = 1 - math.exp(-float(fault.values[i,3]))
                    Hazard_Prob[i][j][k] = IS_weight(i)[len(IS_CDF(i))-len(selected[0])]*P_occurrence

           
#print(HCP)

#=============================================================================================
                
"""
# Generate earthquake catalogs: 25 magnitude for each faults
for i in range(Nearthquake):
    # logging
    if i < 10 :
        print("Generating data for earthquake #" + str(i) + " of " + str(Nearthquake) + "...")
    elif i == 10 :
        print("Generating data for earthquake #" + str(i) + " of " + str(Nearthquake) + "...")
        print("Now logging every 50 earthquakes...")
    elif i > 10 :
        if i % 50 == 0 :
            print("Generating data for earthquake #" + str(i) + " of " + str(Nearthquake) + "...")

    seismic_catalog[i][0] = i+1
    # fault ID
    if i < 25*4:
        seismic_catalog[i][1] = int (i/25) +1
    elif i == 25*4:
        seismic_catalog[i][1] = 5
    elif 25*4 < i <= (14-1-1)*25:
        seismic_catalog[i][1] = int ((i+24)/25) +1
    elif i == (14-1-1)*25+1:
        seismic_catalog[i][1] = 14 
    elif (14-1-1)*25+1 < i <= (16-1-2)*25+1:
        seismic_catalog[i][1] = int ((i+24+24)/25) +1
    elif i == (16-1-2)*25+2:
        seismic_catalog[i][1] = 16
    elif (16-1-2)*25+2 < i <= (23-1-3)*25+2:
        seismic_catalog[i][1] = int ((i+24*3)/25) +1
    elif i == (23-1-3)*25+3:
        seismic_catalog[i][1] = 23
    elif (23-1-3)*25+3 < i <= (25-1-4)*25+3:
        seismic_catalog[i][1] = 24
    elif i == (25-1-4)*25+4:
        seismic_catalog[i][1] = 25
    elif (25-1-4)*25+4 < i <= (29-1-5)*25+4:
        seismic_catalog[i][1] = int ((i+24*5)/25) +1
    elif i == (29-1-5)*25+5:
        seismic_catalog[i][1] = 29
    elif (29-1-5)*25+5 < i <= (32-1-6)*25+5:
        seismic_catalog[i][1] = int ((i+24*6)/25) +1
    elif i == (32-1-6)*25+6:
        seismic_catalog[i][1] = 32
    elif (32-1-6)*25+6 < i <= (37-1-7)*25+6:
        seismic_catalog[i][1] = int ((i+24*7)/25) + 1
    elif i == (37-1-7)*25+7:
        seismic_catalog[i][1] = 37
    elif (37-1-7)*25+7 < i <= (44-1-8)*25+7:
        seismic_catalog[i][1] = int ((i+24*8)/25) +1
    elif i == (44-1-8)*25+8:
        seismic_catalog[i][1] = 44
    elif (44-1-8)*25+8 < i:
        seismic_catalog[i][1] = int ((i+24*9)/25) +1

     
    fault_id = int(seismic_catalog[i][1])-1
    # if fault doesn't have a- & b- value, give a maximum magnitude
    if fault.values[fault_id][4] == 0:
        seismic_catalog[i][2] = fault.values[fault_id][2]
        seismic_catalog[i][6] = fault.values[fault_id][3]
    #if not, magnitude is determined by a random number, K_random, and IS weight
    else:
        # a random number, R_random, between 0 and 1 is generated from a uniform distribution
        # annual probability of occurrence, modeled as a Poisson model
        # if the R_random is less than the annual probability of occurrence, earthquake occurrence
    
        # 1. generate a random number
        K_random = random.random()
        # 2. CDF of IS weight:
        # IS_CDF = IS_CDF(i)
        # generate magnitude based on IS weight:
        selected = np.nonzero(IS_CDF(fault_id)>K_random)
        lower_magnitude = float(magnitude_partition(fault_id)[len(IS_CDF(fault_id))-len(selected[0])])
        upper_magnitude = float(magnitude_partition(fault_id)[len(IS_CDF(fault_id))-len(selected[0])+1])
        # generate earthquake magnitude between lower-and upper bounder with 0.01 interval
        seismic_catalog[i][2] = random.uniform(lower_magnitude, upper_magnitude)
        # Hazard-Consistent Probability:
        P_occurrence = 1 - math.exp(-float(fault.values[fault_id,3]))
        seismic_catalog[i][6] = IS_weight(fault_id)[len(IS_CDF(fault_id))-len(selected[0])]*P_occurrence     

    # Depth:
    max_depth = fault.values[fault_id][6]*math.sin(fault.values[fault_id][7])
    if 6.5 <= seismic_catalog[i][2] <= 6.75:
        random_num = random.random()
        if random_num < 0.33:
            seismic_catalog[i][5] = 0
        elif 0.33 <= random_num < 0.67:
            seismic_catalog[i][5] = 2
        else:
            seismic_catalog[i][5] = 4
    elif 6.75 < seismic_catalog[i][2] <= 7:
        random_num = random.random()
        if random_num < 0.5:
            seismic_catalog[i][5] = 0
        else:
            seismic_catalog[i][5] = 2
    elif seismic_catalog[i][2] > 7:
        seismic_catalog[i][5] = 0
    elif seismic_catalog[i][2] < 6.5:
        seismic_catalog[i][5] = random.uniform(4, max_depth)
        seismic_catalog[i][5] = round(seismic_catalog[i][5], 1) 
    # Epicenter:
    if fault.values[fault_id][8] != 0:
        if fault_id == 26-1:# Pine Valley graben fault system, Brownlee sec
            # reference: https://earthquake.usgs.gov/scenarios/eventpage/bssc2014809a_m6p56_se/executive
            seismic_catalog[i][3] = -116.965
            seismic_catalog[i][4] = 44.844
        elif fault_id == 27-1:# Pine Valley graben fault system, Halfway-Pose
            # reference: https://earthquake.usgs.gov/scenarios/eventpage/bssc2014809b_m6p91_se/executive
            seismic_catalog[i][3] = -116.985
            seismic_catalog[i][4] = 44.897
        else: 
            temp_data = epicenter.loc[epicenter['fault_id'] == fault.values[fault_id][8]]
            total_number = len(temp_data)
            selected = int(random.uniform(1, total_number))
            seismic_catalog[i][3] = temp_data.values[selected][25]
            seismic_catalog[i][4] = temp_data.values[selected][26]
    elif fault_id == 50-1:#Mill Creek Thrust fault 
        # reference: https://earthquake.usgs.gov/scenarios/eventpage/bssc2014566_m7p11_se/executive 
        seismic_catalog[i][3] = -120.633
        seismic_catalog[i][4] = 46.245
    elif fault_id == 23-1:# Mount Hood fault
        # reference: https://earthquake.usgs.gov/scenarios/eventpage/bssc2014865_m6p29_se/executive
        seismic_catalog[i][3] = -121.838
        seismic_catalog[i][4] = 45.428
    elif fault_id == 29-1:# Sandy River fault zone
        # reference: https://earthquake.usgs.gov/scenarios/eventpage/bssc2014or4_m6p5_se/executive 
        seismic_catalog[i][3] = -122.308
        seismic_catalog[i][4] = 45.493
    elif fault_id == 41-1:# Wecoma fault
        # reference: https://earthquake.usgs.gov/scenarios/eventpage/bssc2014799_m7p34_se/executive
        seismic_catalog[i][3] = -125.146
        seismic_catalog[i][4] = 45.045
        
        


print("Saving earthquake data as seismic_catalog.npy")
np.save("seismic_catalog.npy", seismic_catalog)   


#print(fault.values[25][8])
