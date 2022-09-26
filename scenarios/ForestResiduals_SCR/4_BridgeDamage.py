
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 2020

@author: Jie Zhao
"""
import numpy as np
import pandas as pd
from scipy.stats import lognorm  
import random

# added by Mark
import os
os.chdir("C:\FTOT-SCR\scenarios\ForestResiduals_SCR\input_data")

# Total number of scenarios
Nscenario = 30
# Planning Horizon
plan_horizon = 20 # unit: year
# Simulation region in OpenSHA
# min longitude = -110.0; max longitude =-126.0; min latitude = 41.0; max latitude = 49.0
min_lat = 41.0
max_lat = 49.0
min_lon = -110.0 
max_lon =-126.0
# ---------------------Load bridge and edge TXT files--------------------
data_bridge = pd.read_csv("HighwayBridge_3state.txt")
bridge = pd. DataFrame (data_bridge)
N_bridge = len(bridge) # Tatal amount of bridges
data_edge = pd.read_csv("MiddlePoint_Road.txt")
edge = pd. DataFrame (data_edge) 

# load seismic information 
seismic_catalog = np.load("seismic_catalog.npy")
earthquake_events = np.load("earthquake_events.npy")
# Bridge location 
# bridge_loc = np.load("bridge_loc.npy")


#-----------------------Fragility function (Longnormal distribution)--------------------------
# Bridge fragility curve for 28 bridge types, row (bridgr type), column(Mu for DS1, DS2, DS3, DS4)
# obtained from Table 87.7, in HAZUS earthquake technique mannual
bridge_fragility_mu = [[0.4,0.5,0.7,0.9],
                    [0.6,0.9,1.1,1.7],
                    [0.8,1,1.2,1.7],
                    [0.8,1,1.2,1.7],
                    [0.25,0.35,0.45,0.7],
                    [0.3,0.5,0.6,0.9],
                    [0.5,0.8,1.1,1.7],
                    [0.35,0.45,0.55,0.80],
                    [0.6,0.9,1.3,1.6],
                    [0.6,0.9,1.1,1.5],
                    [0.9,0.9,1.1,1.5],
                    [0.25,0.35,0.45,0.7],
                    [0.3,0.5,0.6,0.9],
                    [0.5,0.8,1.1,1.7],
                    [0.75,0.75,0.75,1.1],
                    [0.9,0.9,1.1,1.5],
                    [0.25,0.35,0.45,0.7],
                    [0.3,0.5,0.6,0.9],
                    [0.5,0.8,1.1,1.7],
                    [0.35,0.45,0.55,0.8],
                    [0.6,0.9,1.6,1.6],
                    [0.6,0.9,1.1,1.5],
                    [0.9,0.9,1.1,1.5],
                    [0.25,0.35,0.45,0.7],
                    [0.3,0.5,0.6,0.9],
                    [0.75,0.75,0.75,1.1],
                    [0.75,0.75,0.75,1.1],
                    [0.8,1.0,1.2,1.7]]
bridge_fragility_beta = 0.6
                    
   

# ------------------------Restoration function (Normal distribution)----------------
# bridge continuous restoration functions, row(DS1-4), column (mu and std)
# obtained from Table 7.7, in HAZUS earthquake technique mannual,unit: days
bridge_repair_time = [[0.6,0.6],
                        [2.5,2.7],
                        [75,42],
                        [230,110]]                  
                  
# bridge repair downtime for DS1-4, 
# obtained from Hashemi et al.(2019), unit: days
bridge_repair_downtime = [20,60,60,100]

#----------------Bridge location------------------------------------------
# Find the bridge location corresponding to ground motion output: row(bridge_ID), 
# column(4 corner point of bridge location area)
bridge_loc = np.zeros((N_bridge,7))
# take an example:
# ground motion for earthquake 745
data_GM_745_SA = pd.read_csv("s1_745_SA.txt")
sa_745 = pd.DataFrame (data_GM_745_SA)
data = np.zeros((len(sa_745),3))
for i in range (len(sa_745)):
    df = sa_745.iloc[i]
    df = pd.Series(df)
    data[i,:] = df.str.split(expand=True)

lat_array = data[:,0]
lon_array = data[:,1]
for i in range(len(bridge_loc)):
    bridge_loc [i][0] = bridge.values[i][0]
    bridge_loc [i][1] = bridge.values[i][23]
    bridge_loc [i][2] = bridge.values[i][24]
    # upper part of the area
    boolArr_1 = lat_array  >= bridge_loc [i][1]
    newArr_1 = lon_array[boolArr_1]  
    temp_num_min = (int(bridge_loc [i][2]*10))
    num_min = (temp_num_min*0.1) - 0.1
    num_loc = (-110 - num_min)/0.1
    # lower part of the area
    boolArr_2 = lat_array  >= bridge_loc [i][1]-1
    newArr_2 = lon_array[boolArr_2]
    temp_num_min = (int(bridge_loc [i][2]*10))
    num_min = (temp_num_min*0.1) - 0.1
    num_loc = (min_lon - num_min)/0.1
    # upper left point:
    bridge_loc [i][3] = len(lat_array) - len(newArr_1) -num_loc-1
    # upper right point:
    bridge_loc [i][4] = len(lat_array) - len(newArr_1)-num_loc
    # lower left point:
    bridge_loc [i][5] = len(lat_array) - len(newArr_2) -num_loc-1
    # lower right point:
    bridge_loc [i][6] = len(lat_array) - len(newArr_2) -num_loc
# Finally, the bridge ground motion parameter = average of these four points    

#np.save("bridge_loc.npy", bridge_loc)   

#---------------------Ground motion information from OpenSHA---------------------
# Scenario 1:
# ground motion (Sa) for earthquake 745
data_GM_745_SA = pd.read_csv("s1_745_SA.txt")
data_sa_745 = pd.DataFrame (data_GM_745_SA)
sa_745 = np.zeros((len(data_sa_745),3))
for i in range (len(sa_745)):
    df = data_sa_745.iloc[i]
    df = pd.Series(df)
    sa_745[i,:] = df.str.split(expand=True)

# Scenario 2:
# ground motion (Sa) for earthquake 241
data_GM_241_SA = pd.read_csv("s2_241_SA.txt")
data_sa_241 = pd.DataFrame (data_GM_241_SA)
sa_241 = np.zeros((len(data_sa_241),3))
for i in range (len(sa_241)):
    df = data_sa_241.iloc[i]
    df = pd.Series(df)
    sa_241[i,:] = df.str.split(expand=True)
    
# ground motion (Sa) for earthquake 990
data_GM_990_SA = pd.read_csv("s2_990_SA.txt")
data_sa_990 = pd.DataFrame (data_GM_990_SA)
sa_990 = np.zeros((len(data_sa_990),3))
for i in range (len(sa_990)):
    df = data_sa_990.iloc[i]
    df = pd.Series(df)
    sa_990[i,:] = df.str.split(expand=True)
        
# Scenario3&4: no earthquake
    
# Scenario 5:
# ground motion (Sa) for earthquake 881
data_GM_881_SA = pd.read_csv("s5_881_SA.txt")
data_sa_881 = pd.DataFrame (data_GM_881_SA)
sa_881 = np.zeros((len(data_sa_881),3))
for i in range (len(sa_881)):
    df = data_sa_881.iloc[i]
    df = pd.Series(df)
    sa_881[i,:] = df.str.split(expand=True)

# Scenario 7:
# ground motion (Sa) for earthquake 853
data_GM_853_SA = pd.read_csv("s7_853_SA.txt")
data_sa_853 = pd.DataFrame (data_GM_853_SA)
sa_853 = np.zeros((len(data_sa_853),3))
for i in range (len(sa_853)):
    df = data_sa_853.iloc[i]
    df = pd.Series(df)
    sa_853[i,:] = df.str.split(expand=True)
    
# Scenario 8:
# ground motion (Sa) for earthquake 193
data_GM_193_SA = pd.read_csv("s8_193_SA.txt")
data_sa_193 = pd.DataFrame (data_GM_193_SA)
sa_193 = np.zeros((len(data_sa_193),3))
for i in range (len(sa_193)):
    df = data_sa_193.iloc[i]
    df = pd.Series(df)
    sa_193[i,:] = df.str.split(expand=True)

# ground motion (Sa) for earthquake 814
data_GM_814_SA = pd.read_csv("s8_814_SA.txt")
data_sa_814 = pd.DataFrame (data_GM_814_SA)
sa_814 = np.zeros((len(data_sa_814),3))
for i in range (len(sa_814)):
    df = data_sa_814.iloc[i]
    df = pd.Series(df)
    sa_814[i,:] = df.str.split(expand=True)
   
# Scenario 9:
# ground motion (Sa) for earthquake 1166
data_GM_1166_SA = pd.read_csv("s9_1166_SA.txt")
data_sa_1166 = pd.DataFrame (data_GM_1166_SA)
sa_1166 = np.zeros((len(data_sa_1166),3))
for i in range (len(sa_1166)):
    df = data_sa_1166.iloc[i]
    df = pd.Series(df)
    sa_1166[i,:] = df.str.split(expand=True)
 
# ground motion (Sa) for earthquake 644
data_GM_644_SA = pd.read_csv("s9_644_SA.txt")
data_sa_644 = pd.DataFrame (data_GM_644_SA)
sa_644 = np.zeros((len(data_sa_644),3))
for i in range (len(sa_644)):
    df = data_sa_644.iloc[i]
    df = pd.Series(df)
    sa_644[i,:] = df.str.split(expand=True)
   
# ground motion (Sa) for earthquake 818
data_GM_818_SA = pd.read_csv("s9_818_SA.txt")
data_sa_818 = pd.DataFrame (data_GM_818_SA)
sa_818 = np.zeros((len(data_sa_818),3))
for i in range (len(sa_818)):
    df = data_sa_818.iloc[i]
    df = pd.Series(df)
    sa_818[i,:] = df.str.split(expand=True)
    
# Scenario 10:  
# ground motion (Sa) for earthquake 25
data_GM_25_SA = pd.read_csv("s10_25_SA.txt")
data_sa_25 = pd.DataFrame (data_GM_25_SA)
sa_25 = np.zeros((len(data_sa_25),3))
for i in range (len(sa_25)):
    df = data_sa_25.iloc[i]
    df = pd.Series(df)
    sa_25[i,:] = df.str.split(expand=True)
   
# ground motion (Sa) for earthquake 824
data_GM_824_SA = pd.read_csv("s10_824_SA.txt")
data_sa_824 = pd.DataFrame (data_GM_824_SA)
sa_824 = np.zeros((len(data_sa_824),3))
for i in range (len(sa_824)):
    df = data_sa_824.iloc[i]
    df = pd.Series(df)
    sa_824[i,:] = df.str.split(expand=True)
   
# Scenario 12:  
# ground motion (Sa) for earthquake 238
data_GM_238_SA = pd.read_csv("s12_238_SA.txt")
data_sa_238 = pd.DataFrame (data_GM_238_SA)
sa_238 = np.zeros((len(data_sa_238),3))
for i in range (len(sa_238)):
    df = data_sa_238.iloc[i]
    df = pd.Series(df)
    sa_238[i,:] = df.str.split(expand=True)  
       
# Scenario 13:  
# ground motion (Sa) for earthquake 893
data_GM_893_SA = pd.read_csv("s13_893_SA.txt")
data_sa_893 = pd.DataFrame (data_GM_893_SA)
sa_893 = np.zeros((len(data_sa_893),3))
for i in range (len(sa_893)):
    df = data_sa_893.iloc[i]
    df = pd.Series(df)
    sa_893[i,:] = df.str.split(expand=True)
          
 # Scenario 14:  
# ground motion (Sa) for earthquake 812
data_GM_812_SA = pd.read_csv("s14_812_SA.txt")
data_sa_812 = pd.DataFrame (data_GM_812_SA)
sa_812 = np.zeros((len(data_sa_812),3))
for i in range (len(sa_812)):
    df = data_sa_812.iloc[i]
    df = pd.Series(df)
    sa_812[i,:] = df.str.split(expand=True)
    
 # Scenario 15:  
# ground motion (Sa) for earthquake 173
data_GM_173_SA = pd.read_csv("s15_173_SA.txt")
data_sa_173 = pd.DataFrame (data_GM_173_SA)
sa_173 = np.zeros((len(data_sa_173),3))
for i in range (len(sa_173)):
    df = data_sa_173.iloc[i]
    df = pd.Series(df)
    sa_173[i,:] = df.str.split(expand=True)
     
# ground motion (Sa) for earthquake 120
data_GM_120_SA = pd.read_csv("s15_120_SA.txt")
data_sa_120 = pd.DataFrame (data_GM_120_SA)
sa_120 = np.zeros((len(data_sa_120),3))
for i in range (len(sa_120)):
    df = data_sa_120.iloc[i]
    df = pd.Series(df)
    sa_120[i,:] = df.str.split(expand=True)    
 
# ground motion (Sa) for earthquake 243
data_GM_243_SA = pd.read_csv("s15_243_SA.txt")
data_sa_243 = pd.DataFrame (data_GM_243_SA)
sa_243 = np.zeros((len(data_sa_243),3))
for i in range (len(sa_243)):
    df = data_sa_243.iloc[i]
    df = pd.Series(df)
    sa_243[i,:] = df.str.split(expand=True)
   
   # Scenario 16:  
# ground motion (Sa) for earthquake 190
data_GM_190_SA = pd.read_csv("s16_190_SA.txt")
data_sa_190 = pd.DataFrame (data_GM_190_SA)
sa_190 = np.zeros((len(data_sa_190),3))
for i in range (len(sa_190)):
    df = data_sa_190.iloc[i]
    df = pd.Series(df)
    sa_190[i,:] = df.str.split(expand=True)
    
# ground motion (Sa) for earthquake 117
data_GM_117_SA = pd.read_csv("s16_117_SA.txt")
data_sa_117 = pd.DataFrame (data_GM_117_SA)
sa_117 = np.zeros((len(data_sa_117),3))
for i in range (len(sa_117)):
    df = data_sa_117.iloc[i]
    df = pd.Series(df)
    sa_117[i,:] = df.str.split(expand=True)

# ground motion (Sa) for earthquake 884
data_GM_884_SA = pd.read_csv("s16_884_SA.txt")
data_sa_884 = pd.DataFrame (data_GM_884_SA)
sa_884 = np.zeros((len(data_sa_884),3))
for i in range (len(sa_884)):
    df = data_sa_884.iloc[i]
    df = pd.Series(df)
    sa_884[i,:] = df.str.split(expand=True)
    
 # Scenario 17:  
# ground motion (Sa) for earthquake 121
data_GM_121_SA = pd.read_csv("s17_121_SA.txt")
data_sa_121 = pd.DataFrame (data_GM_121_SA)
sa_121 = np.zeros((len(data_sa_121),3))
for i in range (len(sa_121)):
    df = data_sa_121.iloc[i]
    df = pd.Series(df)
    sa_121[i,:] = df.str.split(expand=True)
    
   # Scenario 18:  
# ground motion (Sa) for earthquake 992
data_GM_992_SA = pd.read_csv("s18_992_SA.txt")
data_sa_992 = pd.DataFrame (data_GM_992_SA)
sa_992 = np.zeros((len(data_sa_992),3))
for i in range (len(sa_992)):
    df = data_sa_992.iloc[i]
    df = pd.Series(df)
    sa_992[i,:] = df.str.split(expand=True) 
     
# ground motion (Sa) for earthquake 235
data_GM_235_SA = pd.read_csv("s18_235_SA.txt")
data_sa_235 = pd.DataFrame (data_GM_235_SA)
sa_235 = np.zeros((len(data_sa_235),3))
for i in range (len(sa_235)):
    df = data_sa_235.iloc[i]
    df = pd.Series(df)
    sa_235[i,:] = df.str.split(expand=True)
 
# ground motion (Sa) for earthquake 109
data_GM_109_SA = pd.read_csv("s18_109_SA.txt")
data_sa_109 = pd.DataFrame (data_GM_109_SA)
sa_109 = np.zeros((len(data_sa_109),3))
for i in range (len(sa_109)):
    df = data_sa_109.iloc[i]
    df = pd.Series(df)
    sa_109[i,:] = df.str.split(expand=True)
        
# ground motion (Sa) for earthquake 1009
data_GM_1009_SA = pd.read_csv("s18_1009_SA.txt")
data_sa_1009 = pd.DataFrame (data_GM_1009_SA)
sa_1009 = np.zeros((len(data_sa_1009),3))
for i in range (len(sa_1009)):
    df = data_sa_1009.iloc[i]
    df = pd.Series(df)
    sa_1009[i,:] = df.str.split(expand=True)
           
 # Scenario 20:  
# ground motion (Sa) for earthquake 1406
data_GM_1406_SA = pd.read_csv("s20_1406_SA.txt")
data_sa_1406 = pd.DataFrame (data_GM_1406_SA)
sa_1406 = np.zeros((len(data_sa_1406),3))
for i in range (len(sa_1406)):
    df = data_sa_1406.iloc[i]
    df = pd.Series(df)
    sa_1406[i,:] = df.str.split(expand=True)
   
 # Scenario 22:  
# ground motion (Sa) for earthquake 227
data_GM_227_SA = pd.read_csv("s22_227_SA.txt")
data_sa_227 = pd.DataFrame (data_GM_227_SA)
sa_227 = np.zeros((len(data_sa_227),3))
for i in range (len(sa_227)):
    df = data_sa_227.iloc[i]
    df = pd.Series(df)
    sa_227[i,:] = df.str.split(expand=True)
    
# ground motion (Sa) for earthquake 182
data_GM_182_SA = pd.read_csv("s22_182_SA.txt")
data_sa_182 = pd.DataFrame (data_GM_182_SA)
sa_182 = np.zeros((len(data_sa_182),3))
for i in range (len(sa_182)):
    df = data_sa_182.iloc[i]
    df = pd.Series(df)
    sa_182[i,:] = df.str.split(expand=True)
           
 # Scenario 23:  
# ground motion (Sa) for earthquake 32
data_GM_32_SA = pd.read_csv("s23_32_SA.txt")
data_sa_32 = pd.DataFrame (data_GM_32_SA)
sa_32 = np.zeros((len(data_sa_32),3))
for i in range (len(sa_32)):
    df = data_sa_32.iloc[i]
    df = pd.Series(df)
    sa_32[i,:] = df.str.split(expand=True)
           
# ground motion (Sa) for earthquake 236
data_GM_236_SA = pd.read_csv("s23_236_SA.txt")
data_sa_236 = pd.DataFrame (data_GM_236_SA)
sa_236 = np.zeros((len(data_sa_236),3))
for i in range (len(sa_236)):
    df = data_sa_236.iloc[i]
    df = pd.Series(df)
    sa_236[i,:] = df.str.split(expand=True)

# ground motion (Sa) for earthquake 845
data_GM_845_SA = pd.read_csv("s23_845_SA.txt")
data_sa_845 = pd.DataFrame (data_GM_845_SA)
sa_845 = np.zeros((len(data_sa_845),3))
for i in range (len(sa_845)):
    df = data_sa_845.iloc[i]
    df = pd.Series(df)
    sa_845[i,:] = df.str.split(expand=True)
       
# Scenario 24:
# ground motion (Sa) for earthquake 107
data_GM_107_SA = pd.read_csv("s24_107_SA.txt")
data_sa_107 = pd.DataFrame (data_GM_107_SA)
sa_107 = np.zeros((len(data_sa_107),3))
for i in range (len(sa_107)):
    df = data_sa_107.iloc[i]
    df = pd.Series(df)
    sa_107[i,:] = df.str.split(expand=True)
          
# ground motion (Sa) for earthquake 30
data_GM_30_SA = pd.read_csv("s24_30_SA.txt")
data_sa_30 = pd.DataFrame (data_GM_30_SA)
sa_30 = np.zeros((len(data_sa_30),3))
for i in range (len(sa_30)):
    df = data_sa_30.iloc[i]
    df = pd.Series(df)
    sa_30[i,:] = df.str.split(expand=True) 
    
# Scenario 25:
# ground motion (Sa) for earthquake 642
data_GM_642_SA = pd.read_csv("s25_642_SA.txt")
data_sa_642 = pd.DataFrame (data_GM_642_SA)
sa_642 = np.zeros((len(data_sa_642),3))
for i in range (len(sa_642)):
    df = data_sa_642.iloc[i]
    df = pd.Series(df)
    sa_642[i,:] = df.str.split(expand=True)
    
# Scenario 26:
# ground motion (Sa) for earthquake 635
data_GM_635_SA = pd.read_csv("s26_635_SA.txt")
data_sa_635 = pd.DataFrame (data_GM_635_SA)
sa_635 = np.zeros((len(data_sa_635),3))
for i in range (len(sa_635)):
    df = data_sa_635.iloc[i]
    df = pd.Series(df)
    sa_635[i,:] = df.str.split(expand=True)
    
# Scenario 27:
# ground motion (Sa) for earthquake 871
data_GM_871_SA = pd.read_csv("s27_871_SA.txt")
data_sa_871 = pd.DataFrame (data_GM_871_SA)
sa_871 = np.zeros((len(data_sa_871),3))
for i in range (len(sa_871)):
    df = data_sa_871.iloc[i]
    df = pd.Series(df)
    sa_871[i,:] = df.str.split(expand=True)
    
# Scenario 28:
# ground motion (Sa) for earthquake 649
data_GM_649_SA = pd.read_csv("s28_649_SA.txt")
data_sa_649 = pd.DataFrame (data_GM_649_SA)
sa_649 = np.zeros((len(data_sa_649),3))
for i in range (len(sa_649)):
    df = data_sa_649.iloc[i]
    df = pd.Series(df)
    sa_649[i,:] = df.str.split(expand=True)
    
# ground motion (Sa) for earthquake 168
data_GM_168_SA = pd.read_csv("s28_168_SA.txt")
data_sa_168 = pd.DataFrame (data_GM_168_SA)
sa_168 = np.zeros((len(data_sa_168),3))
for i in range (len(sa_168)):
    df = data_sa_168.iloc[i]
    df = pd.Series(df)
    sa_168[i,:] = df.str.split(expand=True)
    
# ground motion (Sa) for earthquake 111
data_GM_111_SA = pd.read_csv("s28_111_SA.txt")
data_sa_111 = pd.DataFrame (data_GM_111_SA)
sa_111 = np.zeros((len(data_sa_111),3))
for i in range (len(sa_111)):
    df = data_sa_111.iloc[i]
    df = pd.Series(df)
    sa_111[i,:] = df.str.split(expand=True)
              
# Scenario 29:
# ground motion (Sa) for earthquake 813
data_GM_813_SA = pd.read_csv("s29_813_SA.txt")
data_sa_813 = pd.DataFrame (data_GM_813_SA)
sa_813 = np.zeros((len(data_sa_813),3))
for i in range (len(sa_813)):
    df = data_sa_813.iloc[i]
    df = pd.Series(df)
    sa_813[i,:] = df.str.split(expand=True)
 

#==========================================Bridge damage===========================  
#---------------------------Variables----------------------------------
# Damage index matrix for bridges
# row (bridge), 
# column (ID,1st year, 2nd year,..., 20th year)
# 3-dimension (scenario)
BDI = np.zeros((N_bridge, plan_horizon+1,Nscenario))

# Damage state matrix for bridges
# row (bridge), 
# column (ID,1st year, 2nd year,..., 20th year)
# 3-dimension (scenario)
bridge_DS = np.zeros((N_bridge, plan_horizon+1,Nscenario))
index = 1

#cdf_DS1 = np.zeros((N_bridge, plan_horizon+1,Nscenario))
#cdf_DS2 = np.zeros((N_bridge, plan_horizon+1,Nscenario))           
#cdf_DS3 = np.zeros((N_bridge, plan_horizon+1,Nscenario))
#cdf_DS4 = np.zeros((N_bridge, plan_horizon+1,Nscenario))
#temp_sa = np.zeros((N_bridge, plan_horizon+1,Nscenario))
for k in range(Nscenario):
    print("Calculating bridge damange for scenario #" + str(k))
    # for scenario 1 (event 745 occurs at year 16):
    if k == 0:
        for i in range(N_bridge):
            BDI [i][0][k] = bridge.values[i][0] # the 1st column is the bridge ID    
            for j in range(plan_horizon):
                if earthquake_events[k][j] != 0:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_745[bridge_loc_upperleft][2]+sa_745[bridge_loc_upperleft][2]
                    +sa_745[bridge_loc_upperleft][2]+sa_745[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1
              
    elif k == 1:
        for i in range(N_bridge):
            for j in range(plan_horizon):
                if j==4:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_241[bridge_loc_upperleft][2]+sa_241[bridge_loc_upperleft][2]
                    +sa_241[bridge_loc_upperleft][2]+sa_241[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1
                elif j == 17:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_990[bridge_loc_upperleft][2]+sa_990[bridge_loc_upperleft][2]
                    +sa_990[bridge_loc_upperleft][2]+sa_990[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1
                    
    elif k == 4:
        for i in range(N_bridge):  
            for j in range(plan_horizon):
                if j== 15:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_881[bridge_loc_upperleft][2]+sa_881[bridge_loc_upperleft][2]
                    +sa_881[bridge_loc_upperleft][2]+sa_881[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1    
    elif k == 6:
        for i in range(N_bridge):   
            for j in range(plan_horizon):
                if j== 19:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_853[bridge_loc_upperleft][2]+sa_853[bridge_loc_upperleft][2]
                    +sa_853[bridge_loc_upperleft][2]+sa_853[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1
    elif k == 7:
        for i in range(N_bridge):  
            for j in range(plan_horizon):
                if j==1:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_193[bridge_loc_upperleft][2]+sa_193[bridge_loc_upperleft][2]
                    +sa_193[bridge_loc_upperleft][2]+sa_193[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1
                elif j == 12:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_814[bridge_loc_upperleft][2]+sa_814[bridge_loc_upperleft][2]
                    +sa_814[bridge_loc_upperleft][2]+sa_814[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                   
         
    elif k == 8:
        for i in range(N_bridge): 
            for j in range(plan_horizon):
                if j==5:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_1166[bridge_loc_upperleft][2]+sa_1166[bridge_loc_upperleft][2]
                    +sa_1166[bridge_loc_upperleft][2]+sa_1166[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1
                elif j == 6:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_644[bridge_loc_upperleft][2]+sa_644[bridge_loc_upperleft][2]
                    +sa_644[bridge_loc_upperleft][2]+sa_644[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                   
                elif j==19:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_818[bridge_loc_upperleft][2]+sa_818[bridge_loc_upperleft][2]
                    +sa_818[bridge_loc_upperleft][2]+sa_818[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                       
                        
    elif k == 9:
        for i in range(N_bridge):  
            for j in range(plan_horizon):
                if j==3:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_25[bridge_loc_upperleft][2]+sa_25[bridge_loc_upperleft][2]
                    +sa_25[bridge_loc_upperleft][2]+sa_25[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1
                elif j == 17:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_824[bridge_loc_upperleft][2]+sa_824[bridge_loc_upperleft][2]
                    +sa_824[bridge_loc_upperleft][2]+sa_824[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                   
                              
    elif k == 11:
        for i in range(N_bridge):  
            for j in range(plan_horizon):
                if j==9:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_238[bridge_loc_upperleft][2]+sa_238[bridge_loc_upperleft][2]
                    +sa_238[bridge_loc_upperleft][2]+sa_238[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                      
                        
    elif k == 12:
        for i in range(N_bridge):   
            for j in range(plan_horizon):
                if j==3:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_893[bridge_loc_upperleft][2]+sa_893[bridge_loc_upperleft][2]
                    +sa_893[bridge_loc_upperleft][2]+sa_893[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                    
                        
    elif k == 13:
        for i in range(N_bridge):   
            for j in range(plan_horizon):
                if j==3:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_812[bridge_loc_upperleft][2]+sa_812[bridge_loc_upperleft][2]
                    +sa_812[bridge_loc_upperleft][2]+sa_812[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                         
                        
    elif k == 14:
        for i in range(N_bridge): 
            for j in range(plan_horizon):
                if j==5:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_173[bridge_loc_upperleft][2]+sa_173[bridge_loc_upperleft][2]
                    +sa_173[bridge_loc_upperleft][2]+sa_173[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1
                elif j == 6:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_120[bridge_loc_upperleft][2]+sa_120[bridge_loc_upperleft][2]
                    +sa_120[bridge_loc_upperleft][2]+sa_120[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                   
                elif j==7:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_243[bridge_loc_upperleft][2]+sa_243[bridge_loc_upperleft][2]
                    +sa_243[bridge_loc_upperleft][2]+sa_243[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                           
                        
    elif k == 15:
        for i in range(N_bridge):   
            for j in range(plan_horizon):
                if j== 2:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_190[bridge_loc_upperleft][2]+sa_190[bridge_loc_upperleft][2]
                    +sa_190[bridge_loc_upperleft][2]+sa_190[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1
                elif j == 6:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_117[bridge_loc_upperleft][2]+sa_117[bridge_loc_upperleft][2]
                    +sa_117[bridge_loc_upperleft][2]+sa_117[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                   
                elif j==8:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_884[bridge_loc_upperleft][2]+sa_884[bridge_loc_upperleft][2]
                    +sa_884[bridge_loc_upperleft][2]+sa_884[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                         
                        
                        
    elif k == 16:
        for i in range(N_bridge):   
            for j in range(plan_horizon):
                if j==4:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_121[bridge_loc_upperleft][2]+sa_121[bridge_loc_upperleft][2]
                    +sa_121[bridge_loc_upperleft][2]+sa_121[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                         
                        
    elif k == 17:
        for i in range(N_bridge):  
            for j in range(plan_horizon):
                if j== 0:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_992[bridge_loc_upperleft][2]+sa_992[bridge_loc_upperleft][2]
                    +sa_992[bridge_loc_upperleft][2]+sa_992[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1
                elif j == 4:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_235[bridge_loc_upperleft][2]+sa_235[bridge_loc_upperleft][2]
                    +sa_235[bridge_loc_upperleft][2]+sa_235[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                   
                elif j==15:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_109[bridge_loc_upperleft][2]+sa_109[bridge_loc_upperleft][2]
                    +sa_109[bridge_loc_upperleft][2]+sa_109[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                          
                elif j==17:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_1009[bridge_loc_upperleft][2]+sa_1009[bridge_loc_upperleft][2]
                    +sa_1009[bridge_loc_upperleft][2]+sa_1009[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                         
                        
                        
    elif k == 19:
        for i in range(N_bridge):   
            for j in range(plan_horizon):
                if j== 10:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_1406[bridge_loc_upperleft][2]+sa_1406[bridge_loc_upperleft][2]
                    +sa_1406[bridge_loc_upperleft][2]+sa_1406[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                         
                        
    elif k == 21:
        for i in range(N_bridge):   
            for j in range(plan_horizon):
                if j== 10:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_227[bridge_loc_upperleft][2]+sa_227[bridge_loc_upperleft][2]
                    +sa_227[bridge_loc_upperleft][2]+sa_227[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1
                elif j == 15:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_182[bridge_loc_upperleft][2]+sa_182[bridge_loc_upperleft][2]
                    +sa_182[bridge_loc_upperleft][2]+sa_182[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                   
                                               
    elif k == 22:
        for i in range(N_bridge):   
            for j in range(plan_horizon):
                if j== 4:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_32[bridge_loc_upperleft][2]+sa_32[bridge_loc_upperleft][2]
                    +sa_32[bridge_loc_upperleft][2]+sa_32[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1
                elif j == 6:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_236[bridge_loc_upperleft][2]+sa_236[bridge_loc_upperleft][2]
                    +sa_236[bridge_loc_upperleft][2]+sa_236[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                   
                elif j==18:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_845[bridge_loc_upperleft][2]+sa_845[bridge_loc_upperleft][2]
                    +sa_845[bridge_loc_upperleft][2]+sa_845[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                                
                        
    elif k == 23:
        for i in range(N_bridge):  
            for j in range(plan_horizon):
                if j== 6:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_107[bridge_loc_upperleft][2]+sa_107[bridge_loc_upperleft][2]
                    +sa_107[bridge_loc_upperleft][2]+sa_107[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1
                elif j == 17:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_30[bridge_loc_upperleft][2]+sa_30[bridge_loc_upperleft][2]
                    +sa_30[bridge_loc_upperleft][2]+sa_30[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                                        
                        
    elif k == 24:
        for i in range(N_bridge):   
            for j in range(plan_horizon):
                if j== 9:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_642[bridge_loc_upperleft][2]+sa_642[bridge_loc_upperleft][2]
                    +sa_642[bridge_loc_upperleft][2]+sa_642[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                        
                        
    elif k == 25:
        for i in range(N_bridge):  
            for j in range(plan_horizon):
                if j== 8:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_635[bridge_loc_upperleft][2]+sa_635[bridge_loc_upperleft][2]
                    +sa_635[bridge_loc_upperleft][2]+sa_635[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1    
                        
    elif k == 26:
        for i in range(N_bridge):  
            for j in range(plan_horizon):
                if j== 14:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_871[bridge_loc_upperleft][2]+sa_871[bridge_loc_upperleft][2]
                    +sa_871[bridge_loc_upperleft][2]+sa_871[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                        
                        
    elif k == 27:
        for i in range(N_bridge):  
            for j in range(plan_horizon):
                if j== 5:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_649[bridge_loc_upperleft][2]+sa_649[bridge_loc_upperleft][2]
                    +sa_649[bridge_loc_upperleft][2]+sa_649[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1
                elif j == 13:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_168[bridge_loc_upperleft][2]+sa_168[bridge_loc_upperleft][2]
                    +sa_168[bridge_loc_upperleft][2]+sa_168[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                   
                elif j==15:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_111[bridge_loc_upperleft][2]+sa_111[bridge_loc_upperleft][2]
                    +sa_111[bridge_loc_upperleft][2]+sa_111[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                                
                        
    elif k == 28:
        for i in range(N_bridge):   
            for j in range(plan_horizon):
                if j== 17:
                    bridge_loc_upperleft = int(bridge_loc[i][3])
                    bridge_loc_upperright = int(bridge_loc[i][4])
                    bridge_loc_lowerleft = int(bridge_loc[i][5])
                    bridge_loc_lowerright = int(bridge_loc[i][6])
                    temp_sa1 = (sa_813[bridge_loc_upperleft][2]+sa_813[bridge_loc_upperleft][2]
                    +sa_813[bridge_loc_upperleft][2]+sa_813[bridge_loc_upperleft][2])*0.25
                    temp_sa = 10**(temp_sa1*index)
                    temp_bridge_type = int(''.join(filter(str.isdigit, bridge.values[i,2])))
                    temp_mu_DS1 = bridge_fragility_mu[temp_bridge_type-1][0]
                    temp_mu_DS2 = bridge_fragility_mu[temp_bridge_type-1][1]
                    temp_mu_DS3 = bridge_fragility_mu[temp_bridge_type-1][2]
                    temp_mu_DS4 = bridge_fragility_mu[temp_bridge_type-1][3]
                    cdf_DS1 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS1)
                    cdf_DS2 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS2)
                    cdf_DS3 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS3)
                    cdf_DS4 = lognorm.cdf(temp_sa, bridge_fragility_beta, 0, temp_mu_DS4)
                    
                    R_random =random.random()
                    if R_random > cdf_DS1:
                        bridge_DS[i][j+1][k] = 0
                        BDI[i][j+1][k] = 0
                    elif cdf_DS2 < R_random <= cdf_DS1:
                        bridge_DS[i][j+1][k] = 1
                        BDI[i][j+1][k] = 0.1
                    elif cdf_DS3 < R_random <= cdf_DS2:
                        bridge_DS[i][j+1][k] = 2
                        BDI[i][j+1][k] = 0.3
                    elif cdf_DS4 < R_random <= cdf_DS3:
                        bridge_DS[i][j+1][k] = 3
                        BDI[i][j+1][k] = 0.75
                    else:
                        bridge_DS[i][j+1][k] = 4
                        BDI[i][j+1][k] = 1                        
                        
 

# Save varible outputs for following calculation
print("Saving BDI.npy")
np.save("BDI.npy", BDI)   
print("Saving bridge_DS.npy")
np.save("bridge_DS.npy", bridge_DS)   



#---------------Count bridge damage--------------------------------------
BDI = np.load("BDI.npy")   
bridge_DS = np.load("bridge_DS.npy")   


Bridge_damage_count = np.zeros((Nscenario, plan_horizon,4))

for i in range (Nscenario):
    for j in range (plan_horizon):
        Bridge_damage_count[i][j][0] = np.sum(bridge_DS[:,j+1,i]==1)
        Bridge_damage_count[i][j][1] = np.sum(bridge_DS[:,j+1,i]==2)
        Bridge_damage_count[i][j][2] = np.sum(bridge_DS[:,j+1,i]==3)
        Bridge_damage_count[i][j][3] = np.sum(bridge_DS[:,j+1,i]==4)





# Save varible outputs for following calculation
print("Saving BDI.npy")
np.save("BDI.npy", BDI)   
print("Saving bridge_DS.npy")
np.save("bridge_DS.npy", bridge_DS)







                    
                    
# Refenrence: Hashemi, M. J., Al-Attraqchi, A. Y.,  Kalfat, R.,  Al-Mahaidi, R. (2019). 
# Linking seismic resilience into sustainability assessment of limited-ductility RC buildings. 
# Engineering Structures, V188, 121-136 https://www.sciencedirect.com/science/article/pii/S0141029618320625 
