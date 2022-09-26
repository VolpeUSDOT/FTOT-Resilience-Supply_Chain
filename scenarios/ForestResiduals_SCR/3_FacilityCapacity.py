# -*- coding: utf-8 -*-
"""
Created on Nov 17 21:20:16 2020

Case Study: Forest residuals to jet fuel supplyc chain system in WA, OR, ID
Purpose: to generate available capacity matrix for all facilities with considering three types of events

@author: Jie Zhao
"""



# import modules used in this code:
import numpy as np
import pandas as pd
from scipy.stats import poisson
from scipy.stats import uniform
from scipy.stats import lognorm 
import random
import sys

# added by Mark
import os
os.chdir("C:\FTOT-SCR\scenarios\ForestResiduals_SCR\input_data")

# -------Constant parameters------------------------
# planning horizon in this example: 20 years
plan_horizon = 20 # unit: year
Nt = 20  # unit: year
# total scenario amount: here we consider 30 scenarios
Nscenario = 30

# Simulation region in OpenSHA
# min longitude = -110.0; max longitude =-126.0; min latitude = 41.0; max latitude = 49.0
min_lat = 41.0
max_lat = 49.0
min_lon = -110.0 
max_lon =-126.0


#----------------------Load information------------------------------ 
#Load senarios obtained from scenario_generation.py
earthquake_events = np.load("earthquake_events.npy")
#scenario_GFT = np.load("scenario_GFT.npy")
scenario_forest = np.load("scenario_forest.npy")
#load seismic catalog
seismic_catalog = np.load("seismic_catalog.npy")

# input the facility information from rmp/proc/dest CSV files
data_rmp = pd.read_csv("rmp.csv")
rmp = pd. DataFrame (data_rmp)
data_proc = pd.read_csv("proc.csv")
proc = pd. DataFrame (data_proc)
data_dest = pd.read_csv("dest.csv")
dest = pd. DataFrame (data_dest)

# input facility location information from rmp/proc/dest_XYcoordinate txt files
data_rmp_XY= pd.read_csv("rmp_XYcoordinate.txt")
rmp_XY = pd. DataFrame (data_rmp_XY)
data_proc_XY = pd.read_csv("proc_XYcoordinate.txt")
proc_XY = pd. DataFrame (data_proc_XY)
data_dest_XY = pd.read_csv("dest_XYcoordinate.txt")
dest_XY = pd. DataFrame (data_dest_XY)

N_RMP = int(len(rmp)) #raw marerial production 
N_PRO = int(len(proc)/3) # processor
N_DES = len(dest)# destination
N_facility = N_RMP + N_PRO + N_DES # all facilities
print(N_RMP)
print(N_PRO)
print(N_DES)

#-------------------------------GFT catalyst activity decrease---------------------------------------
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


#---------------------Fragility function (Longnormal distribution)---------------------
                  
# GFT fragility curve: row (DS1-4), column (mu and beta) 
# obtained from Table 8.18a, in HAZUS earthquake technique mannual
GFT_fragility = [[0.13,0.5],
                 [0.27,0.5],
                 [0.43,0.6],
                 [0.68,0.55]]      
# GFT damage ration = facility functionality for DS1-4
# obtained from Table 15.27, in HAZUS earthquake technique mannual
GFT_damage_ratio = [0.09,0.23,0.78,1]    

#--------------------Restoration function (Normal distribution)--------------------------

# GFT facility repair downtime
# obtained from Almufti and Willford (2013), unit: days

# Inspection time (Longnormal distribution): row (DS1-4), column (mu, beta)
inspection_time = [[5,0.54],
                   [5,0.54],
                   [5,0.54],
                   [5,0.54]]

# Engineering Mobilization and Review/Redesign (Longnormal distribution): row (DS1-4), column (mu, beta)
eng_time = [[6,0.4],
            [12,0.4],
            [12,0.4],
            [50,0.32]]

# Financing with insurance (Longnormal distribution): row (DS1-4), column (mu, beta)
fin_time = [[6,1.11],
            [6,1.11],
            [6,1.11],
            [6,1.11]]
# Contractor Mobilization (Longnormal distribution): row (DS1-4), column (mu, beta)
con_time = [[11,0.43],
            [11,0.43],
            [23,0.41],
            [23,0.41]]
 
# Permitting (Longnormal distribution): row (DS1-4), column (mu, beta)
per_time = [[1,0.86],
            [1,0.86],
            [8,0.32],
            [8,0.32]]
"""
# the total delay time for DS1-4 = max {sequence 1-3} 
GFT_delay_time = np.zeros(4) # total delay time for DS1-4
seq = np.zeros(3) 

for i in range(len(GFT_delay_time)):
    # sequence 1-3:
    seq[0] = inspection_time[i][] + fin_time[i]
    seq[1] = inspection_time[i] + eng_time[i] + per_time[i]
    seq[2] = inspection_time[i] + con_time[i]
    GFT_delay_time[i] = max(seq[:])
"""  
# Restoration cost for facility for DS1-4
# obtained from Table 15.3, in HAZUS earthquake technique mannual,unit: % of investment cost
repair_cost_ratio = [1.4,7.2,21.8,72.5]
GFT_investment = 433000000 # unit: $
GFT_repair_cost = np.zeros(4)
for i in range(len(GFT_repair_cost)):
    GFT_repair_cost[i] = (GFT_investment/100)*repair_cost_ratio[i]

# -----------------List of facility ID-------------------------- 
facility_ID = np.zeros(N_facility)
for i in range(N_facility):
    if 0<= i < N_RMP:
        temp_id = rmp.values[i][0]
        facility_ID[i] = int(''.join(filter(str.isdigit, temp_id)))
    elif  N_RMP<= i < N_RMP + N_DES:
        temp_id = dest.values[i-N_RMP][0]
        facility_ID[i] = int(''.join(filter(str.isdigit, temp_id)))
    else:
        num = int((i-N_RMP - N_DES)*3)
        temp_id = proc.values[num][0]
        facility_ID[i] = int(''.join(filter(str.isdigit, temp_id)))
print("Start location of facility")
#-------------Location of facilities--------------------------------------
# location of facilities corresponding to ground motion output: row(bridge_ID), 
# column(4 corner point of bridge location area)
facility_loc = np.zeros((N_facility,7))
# take an example:
# ground motion for earthquake 745
data_GM_745_PGA = pd.read_csv("s1_745_PGA.txt")
data_pga_745 = pd.DataFrame (data_GM_745_PGA)
pga_745 = np.zeros((len(data_pga_745),3))
for i in range (len(pga_745)):
    df = data_pga_745.iloc[i]
    df = pd.Series(df)
    pga_745[i,:] = df.str.split(expand=True)
    
lat_array = pga_745[:,0]
lon_array = pga_745[:,1]
for i in range(len(facility_loc)):
    # 1st column: facility ID
    facility_loc [i][0] = facility_ID[i]
    # 2nd and 3rd columns: facility coordinate (lat and long)
    if 0<= i < N_RMP:
        facility_loc [i][1] = rmp_XY.values[i][5]
        facility_loc [i][2] = rmp_XY.values[i][4]
    elif  N_RMP<= i < N_RMP + N_DES:
        facility_loc [i][1] = dest_XY.values[i-N_RMP][5]
        facility_loc [i][2] = dest_XY.values[i-N_RMP][4]
    else:
        facility_loc [i][1] = proc_XY.values[i-N_RMP-N_DES][6]
        facility_loc [i][2] = proc_XY.values[i-N_RMP-N_DES][5]
    # location boundary for each facility
    # upper part of the area
    boolArr_1 = lat_array  >= facility_loc [i][1]
    newArr_1 = lon_array[boolArr_1]  
    temp_num_min = (int(facility_loc [i][2]*10))
    num_min = (temp_num_min*0.1) - 0.1
    num_loc = (-110 - num_min)/0.1
    # lower part of the area
    boolArr_2 = lat_array  >= facility_loc [i][1]-0.1
    newArr_2 = lon_array[boolArr_2]
    temp_num_min = (int(facility_loc [i][2]*10))
    num_min = (temp_num_min*0.1) - 0.1
    num_loc = (min_lon - num_min)/0.1
    # upper left point:
    facility_loc [i][3] = len(lat_array) - len(newArr_1) -num_loc-1
    # upper right point:
    facility_loc [i][4] = len(lat_array) - len(newArr_1)-num_loc
    # lower left point:
    facility_loc [i][5] = len(lat_array) - len(newArr_2) -num_loc-1
    # lower right point:
    facility_loc [i][6] = len(lat_array) - len(newArr_2) -num_loc
# Finally, the facility ground motion parameter = average of these four points    
print("Saving facility_loc.npy")
np.save("facility_loc.npy", facility_loc) 

print("Finish location of facility")

print("Start ground motion generation")
#---------------------Ground motion information from OpenSHA---------------------
# Scenario 1:
# ground motion (PGA) for earthquake 745
data_GM_745_PGA = pd.read_csv("s1_745_PGA.txt")
data_pga_745 = pd.DataFrame (data_GM_745_PGA)
pga_745 = np.zeros((len(data_pga_745),3))
for i in range (len(pga_745)):
    df = data_pga_745.iloc[i]
    df = pd.Series(df)
    pga_745[i,:] = df.str.split(expand=True)
 
# Scenario 2:
# ground motion (PGA) for earthquake 241
data_GM_241_PGA = pd.read_csv("s2_241_PGA.txt")
data_pga_241 = pd.DataFrame (data_GM_241_PGA)
pga_241= np.zeros((len(data_pga_241),3))
for i in range (len(pga_241)):
    df = data_pga_241.iloc[i]
    df = pd.Series(df)
    pga_241[i,:] = df.str.split(expand=True)
    

# ground motion (PGA) for earthquake 990
data_GM_990_PGA = pd.read_csv("s2_990_PGA.txt")
data_pga_990 = pd.DataFrame (data_GM_990_PGA)
pga_990= np.zeros((len(data_pga_990),3))
for i in range (len(pga_990)):
    df = data_pga_990.iloc[i]
    df = pd.Series(df)
    pga_990[i,:] = df.str.split(expand=True)
        
# Scenario3&4: no earthquake
    
# Scenario 5:
# ground motion (PGA) for earthquake 881
data_GM_881_PGA = pd.read_csv("s5_881_PGA.txt")
data_pga_881 = pd.DataFrame (data_GM_881_PGA)
pga_881= np.zeros((len(data_pga_881),3))
for i in range (len(pga_881)):
    df = data_pga_881.iloc[i]
    df = pd.Series(df)
    pga_881[i,:] = df.str.split(expand=True)
    
# Scenario 7:
# ground motion (PGA) for earthquake 853
data_GM_853_PGA = pd.read_csv("s7_853_PGA.txt")
data_pga_853 = pd.DataFrame (data_GM_853_PGA)
pga_853= np.zeros((len(data_pga_853),3))
for i in range (len(pga_853)):
    df = data_pga_853.iloc[i]
    df = pd.Series(df)
    pga_853[i,:] = df.str.split(expand=True)
    

# Scenario 8:
# ground motion (PGA) for earthquake 193
data_GM_193_PGA = pd.read_csv("s8_193_PGA.txt")
data_pga_193 = pd.DataFrame (data_GM_193_PGA)
pga_193= np.zeros((len(data_pga_193),3))
for i in range (len(pga_193)):
    df = data_pga_193.iloc[i]
    df = pd.Series(df)
    pga_193[i,:] = df.str.split(expand=True)       

# ground motion (PGA) for earthquake 814
data_GM_814_PGA = pd.read_csv("s8_814_PGA.txt")
data_pga_814 = pd.DataFrame (data_GM_814_PGA)
pga_814= np.zeros((len(data_pga_814),3))
for i in range (len(pga_814)):
    df = data_pga_814.iloc[i]
    df = pd.Series(df)
    pga_814[i,:] = df.str.split(expand=True)     
     
    
# Scenario 9:

# ground motion (PGA) for earthquake 1166
data_GM_1166_PGA = pd.read_csv("s9_1166_PGA.txt")
data_pga_1166 = pd.DataFrame (data_GM_1166_PGA)
pga_1166= np.zeros((len(data_pga_1166),3))
for i in range (len(pga_1166)):
    df = data_pga_1166.iloc[i]
    df = pd.Series(df)
    pga_1166[i,:] = df.str.split(expand=True)    

# ground motion (PGA) for earthquake 644
data_GM_644_PGA = pd.read_csv("s9_644_PGA.txt")
data_pga_644 = pd.DataFrame (data_GM_644_PGA)
pga_644= np.zeros((len(data_pga_644),3))
for i in range (len(pga_644)):
    df = data_pga_644.iloc[i]
    df = pd.Series(df)
    pga_644[i,:] = df.str.split(expand=True)       

# ground motion (PGA) for earthquake 818
data_GM_818_PGA = pd.read_csv("s9_818_PGA.txt")
data_pga_818 = pd.DataFrame (data_GM_818_PGA)
pga_818= np.zeros((len(data_pga_818),3))
for i in range (len(pga_818)):
    df = data_pga_818.iloc[i]
    df = pd.Series(df)
    pga_818[i,:] = df.str.split(expand=True)     
    
# Scenario 10:  
# ground motion (PGA) for earthquake 25
data_GM_25_PGA = pd.read_csv("s10_25_PGA.txt")
data_pga_25 = pd.DataFrame (data_GM_25_PGA)
pga_25= np.zeros((len(data_pga_25),3))
for i in range (len(pga_25)):
    df = data_pga_25.iloc[i]
    df = pd.Series(df)
    pga_25[i,:] = df.str.split(expand=True)      

# ground motion (PGA) for earthquake 824
data_GM_824_PGA = pd.read_csv("s10_824_PGA.txt")
data_pga_824 = pd.DataFrame (data_GM_824_PGA)
pga_824= np.zeros((len(data_pga_824),3))
for i in range (len(pga_824)):
    df = data_pga_824.iloc[i]
    df = pd.Series(df)
    pga_824[i,:] = df.str.split(expand=True)

# ground motion (PGA) for earthquake 238
data_GM_238_PGA = pd.read_csv("s12_238_PGA.txt")
data_pga_238 = pd.DataFrame (data_GM_238_PGA)
pga_238= np.zeros((len(data_pga_238),3))
for i in range (len(pga_238)):
    df = data_pga_238.iloc[i]
    df = pd.Series(df)
    pga_238[i,:] = df.str.split(expand=True)

# ground motion (PGA) for earthquake 893
data_GM_893_PGA = pd.read_csv("s13_893_PGA.txt")
data_pga_893 = pd.DataFrame (data_GM_893_PGA)
pga_893= np.zeros((len(data_pga_893),3))
for i in range (len(pga_893)):
    df = data_pga_893.iloc[i]
    df = pd.Series(df)
    pga_893[i,:] = df.str.split(expand=True) 

# ground motion (PGA) for earthquake 812
data_GM_812_PGA = pd.read_csv("s14_812_PGA.txt")
data_pga_812 = pd.DataFrame (data_GM_812_PGA)
pga_812= np.zeros((len(data_pga_812),3))
for i in range (len(pga_812)):
    df = data_pga_812.iloc[i]
    df = pd.Series(df)
    pga_812[i,:] = df.str.split(expand=True)    
    
 # Scenario 15:  
# ground motion (PGA) for earthquake 173
data_GM_173_PGA = pd.read_csv("s15_173_PGA.txt")
data_pga_173 = pd.DataFrame (data_GM_173_PGA)
pga_173= np.zeros((len(data_pga_173),3))
for i in range (len(pga_173)):
    df = data_pga_173.iloc[i]
    df = pd.Series(df)
    pga_173[i,:] = df.str.split(expand=True)    

# ground motion (PGA) for earthquake 120
data_GM_120_PGA = pd.read_csv("s15_120_PGA.txt")
data_pga_120 = pd.DataFrame (data_GM_120_PGA)
pga_120= np.zeros((len(data_pga_120),3))
for i in range (len(pga_120)):
    df = data_pga_120.iloc[i]
    df = pd.Series(df)
    pga_120[i,:] = df.str.split(expand=True)      

# ground motion (PGA) for earthquake 243
data_GM_243_PGA = pd.read_csv("s15_243_PGA.txt")
data_pga_243 = pd.DataFrame (data_GM_243_PGA)
pga_243= np.zeros((len(data_pga_243),3))
for i in range (len(pga_243)):
    df = data_pga_243.iloc[i]
    df = pd.Series(df)
    pga_243[i,:] = df.str.split(expand=True)    
    
    
   # Scenario 16:  
# ground motion (PGA) for earthquake 190
data_GM_190_PGA = pd.read_csv("s16_190_PGA.txt")
data_pga_190 = pd.DataFrame (data_GM_190_PGA)
pga_190= np.zeros((len(data_pga_190),3))
for i in range (len(pga_190)):
    df = data_pga_190.iloc[i]
    df = pd.Series(df)
    pga_190[i,:] = df.str.split(expand=True)  

# ground motion (PGA) for earthquake 117
data_GM_117_PGA = pd.read_csv("s16_117_PGA.txt")
data_pga_117 = pd.DataFrame (data_GM_117_PGA)
pga_117= np.zeros((len(data_pga_117),3))
for i in range (len(pga_117)):
    df = data_pga_117.iloc[i]
    df = pd.Series(df)
    pga_117[i,:] = df.str.split(expand=True)       

# ground motion (PGA) for earthquake 884
data_GM_884_PGA = pd.read_csv("s16_884_PGA.txt")
data_pga_884 = pd.DataFrame (data_GM_884_PGA)
pga_884= np.zeros((len(data_pga_884),3))
for i in range (len(pga_884)):
    df = data_pga_884.iloc[i]
    df = pd.Series(df)
    pga_884[i,:] = df.str.split(expand=True) 
    
 # Scenario 17:  
# ground motion (PGA) for earthquake 121
data_GM_121_PGA = pd.read_csv("s17_121_PGA.txt")
data_pga_121 = pd.DataFrame (data_GM_121_PGA)
pga_121= np.zeros((len(data_pga_121),3))
for i in range (len(pga_121)):
    df = data_pga_121.iloc[i]
    df = pd.Series(df)
    pga_121[i,:] = df.str.split(expand=True)    
    
   # Scenario 18:  
# ground motion (PGA) for earthquake 992
data_GM_992_PGA = pd.read_csv("s18_992_PGA.txt")
data_pga_992 = pd.DataFrame (data_GM_992_PGA)
pga_992= np.zeros((len(data_pga_992),3))
for i in range (len(pga_992)):
    df = data_pga_992.iloc[i]
    df = pd.Series(df)
    pga_992[i,:] = df.str.split(expand=True)    

# ground motion (PGA) for earthquake 235
data_GM_235_PGA = pd.read_csv("s18_235_PGA.txt")
data_pga_235 = pd.DataFrame (data_GM_235_PGA)
pga_235= np.zeros((len(data_pga_235),3))
for i in range (len(pga_235)):
    df = data_pga_235.iloc[i]
    df = pd.Series(df)
    pga_235[i,:] = df.str.split(expand=True)   

# ground motion (PGA) for earthquake 109
data_GM_109_PGA = pd.read_csv("s18_109_PGA.txt")
data_pga_109 = pd.DataFrame (data_GM_109_PGA)
pga_109= np.zeros((len(data_pga_109),3))
for i in range (len(pga_109)):
    df = data_pga_109.iloc[i]
    df = pd.Series(df)
    pga_109[i,:] = df.str.split(expand=True)     

# ground motion (PGA) for earthquake 1009
data_GM_1009_PGA = pd.read_csv("s18_1009_PGA.txt")
data_pga_1009 = pd.DataFrame (data_GM_1009_PGA)
pga_1009= np.zeros((len(data_pga_1009),3))
for i in range (len(pga_1009)):
    df = data_pga_1009.iloc[i]
    df = pd.Series(df)
    pga_1009[i,:] = df.str.split(expand=True)     
    
    
 # Scenario 20:  
# ground motion (PGA) for earthquake 1406
data_GM_1406_PGA = pd.read_csv("s20_1406_PGA.txt")
data_pga_1406 = pd.DataFrame (data_GM_1406_PGA)
pga_1406= np.zeros((len(data_pga_1406),3))
for i in range (len(pga_1406)):
    df = data_pga_1406.iloc[i]
    df = pd.Series(df)
    pga_1406[i,:] = df.str.split(expand=True)        
    
 # Scenario 22:  
# ground motion (PGA) for earthquake 227
data_GM_227_PGA = pd.read_csv("s22_227_PGA.txt")
data_pga_227 = pd.DataFrame (data_GM_227_PGA)
pga_227= np.zeros((len(data_pga_227),3))
for i in range (len(pga_227)):
    df = data_pga_227.iloc[i]
    df = pd.Series(df)
    pga_227[i,:] = df.str.split(expand=True)  

# ground motion (PGA) for earthquake 182
data_GM_182_PGA = pd.read_csv("s22_182_PGA.txt")
data_pga_182 = pd.DataFrame (data_GM_182_PGA)
pga_182= np.zeros((len(data_pga_182),3))
for i in range (len(pga_182)):
    df = data_pga_182.iloc[i]
    df = pd.Series(df)
    pga_182[i,:] = df.str.split(expand=True)         
    
 # Scenario 23:  
# ground motion (PGA) for earthquake 32
data_GM_32_PGA = pd.read_csv("s23_32_PGA.txt")
data_pga_32 = pd.DataFrame (data_GM_32_PGA)
pga_32= np.zeros((len(data_pga_32),3))
for i in range (len(pga_32)):
    df = data_pga_32.iloc[i]
    df = pd.Series(df)
    pga_32[i,:] = df.str.split(expand=True)  

# ground motion (PGA) for earthquake 236
data_GM_236_PGA = pd.read_csv("s23_236_PGA.txt")
data_pga_236 = pd.DataFrame (data_GM_236_PGA)
pga_236= np.zeros((len(data_pga_236),3))
for i in range (len(pga_236)):
    df = data_pga_236.iloc[i]
    df = pd.Series(df)
    pga_236[i,:] = df.str.split(expand=True)   

# ground motion (PGA) for earthquake 845
data_GM_845_PGA = pd.read_csv("s23_845_PGA.txt")
data_pga_845 = pd.DataFrame (data_GM_845_PGA)
pga_845 = np.zeros((len(data_pga_845),3))
for i in range (len(pga_845)):
    df = data_pga_845.iloc[i]
    df = pd.Series(df)
    pga_845[i,:] = df.str.split(expand=True)        
    
# Scenario 24:

# ground motion (PGA) for earthquake 107
data_GM_107_PGA = pd.read_csv("s24_107_PGA.txt")
data_pga_107 = pd.DataFrame (data_GM_107_PGA)
pga_107= np.zeros((len(data_pga_107),3))
for i in range (len(pga_107)):
    df = data_pga_107.iloc[i]
    df = pd.Series(df)
    pga_107[i,:] = df.str.split(expand=True)    

# ground motion (PGA) for earthquake 30
data_GM_30_PGA = pd.read_csv("s24_30_PGA.txt")
data_pga_30 = pd.DataFrame (data_GM_30_PGA)
pga_30 = np.zeros((len(data_pga_30),3))
for i in range (len(pga_30)):
    df = data_pga_30.iloc[i]
    df = pd.Series(df)
    pga_30[i,:] = df.str.split(expand=True)    

# ground motion (PGA) for earthquake 642
data_GM_642_PGA = pd.read_csv("s25_642_PGA.txt")
data_pga_642 = pd.DataFrame (data_GM_642_PGA)
pga_642= np.zeros((len(data_pga_642),3))
for i in range (len(pga_642)):
    df = data_pga_642.iloc[i]
    df = pd.Series(df)
    pga_642[i,:] = df.str.split(expand=True)   
    
# Scenario 26:

# ground motion (PGA) for earthquake 635
data_GM_635_PGA = pd.read_csv("s26_635_PGA.txt")
data_pga_635 = pd.DataFrame (data_GM_635_PGA)
pga_635= np.zeros((len(data_pga_635),3))
for i in range (len(pga_635)):
    df = data_pga_635.iloc[i]
    df = pd.Series(df)
    pga_635[i,:] = df.str.split(expand=True)  
    
# Scenario 27:

# ground motion (PGA) for earthquake 871
data_GM_871_PGA = pd.read_csv("s27_871_PGA.txt")
data_pga_871 = pd.DataFrame (data_GM_871_PGA)
pga_871= np.zeros((len(data_pga_871),3))
for i in range (len(pga_871)):
    df = data_pga_871.iloc[i]
    df = pd.Series(df)
    pga_871[i,:] = df.str.split(expand=True)      
    
# Scenario 28:

# ground motion (PGA) for earthquake 649
data_GM_649_PGA = pd.read_csv("s28_649_PGA.txt")
data_pga_649 = pd.DataFrame (data_GM_649_PGA)
pga_649= np.zeros((len(data_pga_649),3))
for i in range (len(pga_649)):
    df = data_pga_649.iloc[i]
    df = pd.Series(df)
    pga_649[i,:] = df.str.split(expand=True)  

# ground motion (PGA) for earthquake 168
data_GM_168_PGA = pd.read_csv("s28_168_PGA.txt")
data_pga_168 = pd.DataFrame (data_GM_168_PGA)
pga_168= np.zeros((len(data_pga_168),3))
for i in range (len(pga_168)):
    df = data_pga_168.iloc[i]
    df = pd.Series(df)
    pga_168[i,:] = df.str.split(expand=True)         
    

# ground motion (PGA) for earthquake 111
data_GM_111_PGA = pd.read_csv("s28_111_PGA.txt")
data_pga_111 = pd.DataFrame (data_GM_111_PGA)
pga_111= np.zeros((len(data_pga_111),3))
for i in range (len(pga_111)):
    df = data_pga_111.iloc[i]
    df = pd.Series(df)
    pga_111[i,:] = df.str.split(expand=True)         
       
# Scenario 29:
# ground motion (PGA) for earthquake 813
data_GM_813_PGA = pd.read_csv("s29_813_PGA.txt")
data_pga_813 = pd.DataFrame (data_GM_813_PGA)
pga_813= np.zeros((len(data_pga_813),3))
for i in range (len(pga_813)):
    df = data_pga_813.iloc[i]
    df = pd.Series(df)
    pga_813[i,:] = df.str.split(expand=True)   
    
print("Finish ground motion generation")
#---------------------Variables for output-------------------------
#Catalyst replace cost 
CatalystReplace_cost = np.zeros((N_facility, plan_horizon+1,Nscenario)) #Catalyst replace cost 
# capacitry matrix for facility with only considering 2 risk factors
# row (facility), 
# column (ID,1st year, 2nd year,..., 20th year)
# 3-dimension (scenario)
facility_cap_noEarthquake = np.zeros((N_facility, plan_horizon+1,Nscenario))
# capacitry matrix for facility with considering 3 risk factors
# row (facility), 
# column (ID,1st year, 2nd year,..., 20th year)
# 3-dimension (scenario)
facility_cap = np.ones((N_facility, plan_horizon+1,Nscenario))
# Damage state for faclity
# row (facility), 
# column (ID,1st year, 2nd year,..., 20th year)
# 3-dimension (scenario)
facility_DS = np.zeros((N_facility, plan_horizon+1,Nscenario))    


#------------------Facility capacity loop for no earthquake condition-----------------------------------------
for k in range(Nscenario):
    # For RMPs, wood harvest increase will cause the increase of feedstock amount
    for j in range(plan_horizon):
        for i in range(N_facility):
            facility_cap_noEarthquake [i][0][k] = facility_ID[i] # the 1st column is the facility ID     
            if 0<= i < N_RMP:# facility = raw material production
                facility_cap_noEarthquake [i][j+1][k] = scenario_forest[k][j]   



# Catalyst replacement cost and facility capacity
# For proc，deactivity of catalyst causes decrease of facility capacity (converion rate)               
for k in range(Nscenario):  
    for i in range(N_facility):
        if N_RMP + N_DES <= i <N_facility:
            capacity_GFT = 1
            ass_value = np.random.normal(ass_mean, ass_std, 1)
            kd_value = np.random.normal(kd_mean, kd_std, 1)
            year = 0
            for j in range(plan_horizon):
                if facility_cap_noEarthquake [i][j][k] >= threshold: 
                    year = year + 1
                    temp_rate = a(year,ass_value, kd_value)
                    facility_cap_noEarthquake [i][j+1][k] =capacity_GFT* temp_rate
                else: 
                    year = 0 
                    ass_value = np.random.normal(ass_mean, ass_std, 1)
                    kd_value = np.random.normal(kd_mean, kd_std, 1)
                    facility_cap_noEarthquake [i][j+1][k] = 1
                    capacity_GFT = 1
                    CatalystReplace_cost[i][j+1][k] = (Replacement_cost)*((1.003)**(j+13))# Considering inflation rate = 1.003/year


"""
facility_cap_noEarthquake1  = np.load("facility_cap_noEarthquake.npy")
    

for k in range (Nscenario):
    for i in range(N_facility):
        for j in range(plan_horizon+1):
            facility_cap_noEarthquake[i][j][k] = facility_cap_noEarthquake1[i][j][k]
"""
#------------------Facility capacity loop for earthquake occurrence condition-----------------------------------------
index = 1
for k in range(Nscenario):
    sys.stdout.write("scenario {} ;".format(k)); sys.stdout.flush();  # print a small progress bar
    # for scenario 1 (event 745 occurs at year 16):
    if k == 0:
        for i in range(N_RMP + N_DES, N_facility):#only consider the damage for GFT facility
            facility_cap [i][0][k] = facility_ID[i]# the 1st column is the bridge ID    
            for j in range(plan_horizon):
                if earthquake_events[k][j] != 0:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_745[facility_loc_upperleft][2]+pga_745[facility_loc_upperright][2]
                    +pga_745[facility_loc_upperleft][2]+pga_745[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
                 
    elif k == 1:
        for i in range(N_RMP + N_DES, N_facility):
            for j in range(plan_horizon):
                if j==4:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_241[facility_loc_upperleft][2]+pga_241[facility_loc_upperright][2]
                    +pga_241[facility_loc_upperleft][2]+pga_241[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
                        
                elif j == 17:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_990[facility_loc_upperleft][2]+pga_990[facility_loc_upperright][2]
                    +pga_990[facility_loc_upperleft][2]+pga_990[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
                    
    elif k == 4:
        for i in range(N_RMP + N_DES, N_facility):  
            for j in range(plan_horizon):
                if j== 15:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_881[facility_loc_upperleft][2]+pga_881[facility_loc_upperright][2]
                    +pga_881[facility_loc_upperleft][2]+pga_881[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]   
    elif k == 6:
        for i in range(N_RMP + N_DES, N_facility):   
            for j in range(plan_horizon):
                if j== 19:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_853[facility_loc_upperleft][2]+pga_853[facility_loc_upperright][2]
                    +pga_853[facility_loc_upperleft][2]+pga_853[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
    elif k == 7:
        for i in range(N_RMP + N_DES, N_facility):  
            for j in range(plan_horizon):
                if j==1:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_193[facility_loc_upperleft][2]+pga_193[facility_loc_upperright][2]
                    +pga_193[facility_loc_upperleft][2]+pga_193[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
                elif j == 12:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_814[facility_loc_upperleft][2]+pga_814[facility_loc_upperright][2]
                    +pga_814[facility_loc_upperleft][2]+pga_814[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]               
         
    elif k == 8:
        for i in range(N_RMP + N_DES, N_facility): 
            for j in range(plan_horizon):
                if j==5:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_1166[facility_loc_upperleft][2]+pga_1166[facility_loc_upperright][2]
                    +pga_1166[facility_loc_upperleft][2]+pga_1166[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
                        
                elif j == 6:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_644[facility_loc_upperleft][2]+pga_644[facility_loc_upperright][2]
                    +pga_644[facility_loc_upperleft][2]+pga_644[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]                  
                elif j==19:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_818[facility_loc_upperleft][2]+pga_818[facility_loc_upperright][2]
                    +pga_818[facility_loc_upperleft][2]+pga_818[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]                  
                        
    elif k == 9:
        for i in range(N_RMP + N_DES, N_facility):  
            for j in range(plan_horizon):
                if j==3:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_25[facility_loc_upperleft][2]+pga_25[facility_loc_upperright][2]
                    +pga_25[facility_loc_upperleft][2]+pga_25[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
                elif j == 17:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_824[facility_loc_upperleft][2]+pga_824[facility_loc_upperright][2]
                    +pga_824[facility_loc_upperleft][2]+pga_824[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
                        
                              
    elif k == 11:
        for i in range(N_RMP + N_DES, N_facility):  
            for j in range(plan_horizon):
                if j==9:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_238[facility_loc_upperleft][2]+pga_238[facility_loc_upperright][2]
                    +pga_238[facility_loc_upperleft][2]+pga_238[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]                     
                        
    elif k == 12:
        for i in range(N_RMP + N_DES, N_facility):   
            for j in range(plan_horizon):
                if j==3:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_893[facility_loc_upperleft][2]+pga_893[facility_loc_upperright][2]
                    +pga_893[facility_loc_upperleft][2]+pga_893[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
                        
    elif k == 13:
        for i in range(N_RMP + N_DES, N_facility):   
            for j in range(plan_horizon):
                if j==3:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_812[facility_loc_upperleft][2]+pga_812[facility_loc_upperright][2]
                    +pga_812[facility_loc_upperleft][2]+pga_812[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]                      
                        
    elif k == 14:
        for i in range(N_RMP + N_DES, N_facility): 
            for j in range(plan_horizon):
                if j==5:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_173[facility_loc_upperleft][2]+pga_173[facility_loc_upperright][2]
                    +pga_173[facility_loc_upperleft][2]+pga_173[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
                        
                elif j == 6:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_120[facility_loc_upperleft][2]+pga_120[facility_loc_upperright][2]
                    +pga_120[facility_loc_upperleft][2]+pga_120[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]           
                elif j==7:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_243[facility_loc_upperleft][2]+pga_243[facility_loc_upperright][2]
                    +pga_243[facility_loc_upperleft][2]+pga_243[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]                  
                        
    elif k == 15:
        for i in range(N_RMP + N_DES, N_facility):   
            for j in range(plan_horizon):
                if j== 2:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_190[facility_loc_upperleft][2]+pga_190[facility_loc_upperright][2]
                    +pga_190[facility_loc_upperleft][2]+pga_190[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
                elif j == 6:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_117[facility_loc_upperleft][2]+pga_117[facility_loc_upperright][2]
                    +pga_117[facility_loc_upperleft][2]+pga_117[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]           
                        
                elif j==8:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_884[facility_loc_upperleft][2]+pga_884[facility_loc_upperright][2]
                    +pga_884[facility_loc_upperleft][2]+pga_884[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]             
                        
    elif k == 16:
        for i in range(N_RMP + N_DES, N_facility):   
            for j in range(plan_horizon):
                if j==4:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_121[facility_loc_upperleft][2]+pga_121[facility_loc_upperright][2]
                    +pga_121[facility_loc_upperleft][2]+pga_121[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]                       
                        
    elif k == 17:
        for i in range(N_RMP + N_DES, N_facility):  
            for j in range(plan_horizon):
                if j== 0:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_992[facility_loc_upperleft][2]+pga_992[facility_loc_upperright][2]
                    +pga_992[facility_loc_upperleft][2]+pga_992[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
                        
                elif j == 4:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_235[facility_loc_upperleft][2]+pga_235[facility_loc_upperright][2]
                    +pga_235[facility_loc_upperleft][2]+pga_235[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]             
                elif j==15:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_109[facility_loc_upperleft][2]+pga_109[facility_loc_upperright][2]
                    +pga_109[facility_loc_upperleft][2]+pga_109[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]                      
                elif j==17:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_1009[facility_loc_upperleft][2]+pga_1009[facility_loc_upperright][2]
                    +pga_1009[facility_loc_upperleft][2]+pga_1009[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]                       
                        
                        
    elif k == 19:
        for i in range(N_RMP + N_DES, N_facility):   
            for j in range(plan_horizon):
                if j== 10:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_1406[facility_loc_upperleft][2]+pga_1406[facility_loc_upperright][2]
                    +pga_1406[facility_loc_upperleft][2]+pga_1406[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]                       
                        
    elif k == 21:
        for i in range(N_RMP + N_DES, N_facility):   
            for j in range(plan_horizon):
                if j== 10:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_227[facility_loc_upperleft][2]+pga_227[facility_loc_upperright][2]
                    +pga_227[facility_loc_upperleft][2]+pga_227[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
                elif j == 15:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_182[facility_loc_upperleft][2]+pga_182[facility_loc_upperright][2]
                    +pga_182[facility_loc_upperleft][2]+pga_182[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]                                               
    elif k == 22:
        for i in range(N_RMP + N_DES, N_facility):   
            for j in range(plan_horizon):
                if j== 4:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_32[facility_loc_upperleft][2]+pga_32[facility_loc_upperright][2]
                    +pga_32[facility_loc_upperleft][2]+pga_32[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
                elif j == 6:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_236[facility_loc_upperleft][2]+pga_236[facility_loc_upperright][2]
                    +pga_236[facility_loc_upperleft][2]+pga_236[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
                  
                elif j==18:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_845[facility_loc_upperleft][2]+pga_845[facility_loc_upperright][2]
                    +pga_845[facility_loc_upperleft][2]+pga_845[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]                        
    elif k == 23:
        for i in range(N_RMP + N_DES, N_facility):  
            for j in range(plan_horizon):
                if j== 6:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_107[facility_loc_upperleft][2]+pga_107[facility_loc_upperright][2]
                    +pga_107[facility_loc_upperleft][2]+pga_107[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
                elif j == 17:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_30[facility_loc_upperleft][2]+pga_30[facility_loc_upperright][2]
                    +pga_30[facility_loc_upperleft][2]+pga_30[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]                                    
                        
    elif k == 24:
        for i in range(N_RMP + N_DES, N_facility):   
            for j in range(plan_horizon):
                if j== 9:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_642[facility_loc_upperleft][2]+pga_642[facility_loc_upperright][2]
                    +pga_642[facility_loc_upperleft][2]+pga_642[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]                       
                        
    elif k == 25:
        for i in range(N_RMP + N_DES, N_facility):  
            for j in range(plan_horizon):
                if j == 8:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_635[facility_loc_upperleft][2]+pga_635[facility_loc_upperright][2]
                    +pga_635[facility_loc_upperleft][2]+pga_635[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]    
                        
    elif k == 26:
        for i in range(N_RMP + N_DES, N_facility):  
            for j in range(plan_horizon):
                if j== 14:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_871[facility_loc_upperleft][2]+pga_871[facility_loc_upperright][2]
                    +pga_871[facility_loc_upperleft][2]+pga_871[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]              
                        
    elif k == 27:
        for i in range(N_RMP + N_DES, N_facility):  
            for j in range(plan_horizon):
                if j== 5:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_649[facility_loc_upperleft][2]+pga_649[facility_loc_upperright][2]
                    +pga_649[facility_loc_upperleft][2]+pga_649[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
                elif j == 13:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_168[facility_loc_upperleft][2]+pga_168[facility_loc_upperright][2]
                    +pga_168[facility_loc_upperleft][2]+pga_168[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]           
                elif j==15:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_111[facility_loc_upperleft][2]+pga_111[facility_loc_upperright][2]
                    +pga_111[facility_loc_upperleft][2]+pga_111[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]
    elif k == 28:
        for i in range(N_RMP + N_DES, N_facility):   
            for j in range(plan_horizon):
                if j== 17:
                    facility_loc_upperleft = int(facility_loc[i][3])
                    facility_loc_upperright = int(facility_loc[i][4])
                    facility_loc_lowerleft = int(facility_loc[i][5])
                    facility_loc_lowerright = int(facility_loc[i][6])
                    temp_sa1 = (pga_813[facility_loc_upperleft][2]+pga_813[facility_loc_upperright][2]
                    +pga_813[facility_loc_upperleft][2]+pga_813[facility_loc_upperright][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_mu_DS1 = GFT_fragility[0][0]
                    temp_beta_DS1 = GFT_fragility[0][1]
                    temp_mu_DS2 = GFT_fragility[1][0]
                    temp_beta_DS2 = GFT_fragility[1][1]
                    temp_mu_DS3 = GFT_fragility[2][0]
                    temp_beta_DS3 = GFT_fragility[2][1]
                    temp_mu_DS4 = GFT_fragility[3][0]
                    temp_beta_DS4 = GFT_fragility[3][1]
                    cdf_DS1 = lognorm.cdf(temp_sa, temp_beta_DS1, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, temp_beta_DS2, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, temp_beta_DS3, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, temp_beta_DS4, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        facility_DS[i][j+1][k] = 0
                        facility_cap[i][j+1][k] = facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        facility_DS[i][j+1][k] = 1
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[0])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        facility_DS[i][j+1][k] = 2
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[1])*facility_cap_noEarthquake [i][j+1][k]
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        facility_DS[i][j+1][k] = 3
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[2])*facility_cap_noEarthquake [i][j+1][k]
                    else:
                        facility_DS[i][j+1][k] = 4
                        facility_cap[i][j+1][k] = (1-GFT_damage_ratio[3])*facility_cap_noEarthquake [i][j+1][k]                      
                        






print("Saving facility_cap.npy")
np.save("facility_cap.npy", facility_cap) 
print("Saving facility_DS.npy")                   
np.save("facility_DS.npy", facility_DS)
print("Saving facility_cap_noEarthquake.npy")   
np.save("facility_cap_noEarthquake.npy", facility_cap_noEarthquake)
print("Saving CatalystReplace_cost.npy")
np.save("CatalystReplace_cost.npy", CatalystReplace_cost)  


