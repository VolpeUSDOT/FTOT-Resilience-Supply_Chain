
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 2020

@author: Jie Zhao
"""
import numpy as np
import pandas as pd
from scipy.stats import lognorm  
from scipy.stats import norm
import sys

# added by Mark
import os
os.chdir("C:\FTOT-SCR\scenarios\ForestResiduals_SCR\input_data")


# Total number of scenarios
Nscenario = 30 # normally 30
# Planning Horizon
plan_horizon = 20 # unit: year
# Simulation region in OpenSHA
# min longitude = -110.0; max longitude =-126.0; min latitude = 41.0; max latitude = 49.0
min_lat = 41.0
max_lat = 49.0
min_lon = -110.0 
max_lon =-126.0
# ---------------------Load bridge and edge TXT files--------------------
data_Bridge_Edge = pd.read_csv("Relationship_BridgeRoad_3state.txt")
relationship = pd. DataFrame (data_Bridge_Edge)

# load seismic information 
seismic_catalog = np.load("seismic_catalog.npy")
earthquake_events = np.load("earthquake_events.npy")

# load bridge damage cells
BDI = np.load("BDI.npy")   
bridge_DS = np.load("bridge_DS.npy")  
N_bridge = len(BDI)
# load edge capacity cell
edge_cap = np.load("edge_cap.npy")
N_edge = len(edge_cap)
# load facility damage cells
facility_cap = np.load("facility_cap.npy")
facility_DS = np.load ("facility_DS.npy")
N_facility = len(facility_cap)

# ------------------------Bridge restoration function (Normal distribution)----------------
# bridge continuous restoration functions, row(DS1-4), column (mu and std)
# obtained from Table 7.7, in HAZUS earthquake technique mannual,unit: days
bridge_repair_time = [[0.6,0.6],
                        [2.5,2.7],
                        [75,42],
                        [230,110]]                  
                  
# bridge repair downtime for DS1-4, 
# obtained from Hashemi et al.(2019), unit: days
bridge_repair_downtime = [20,60,60,100]

#-------------------Facility restoration function (Normal distribution)--------------------------
# GFT continuous restoration functions, row(DS1-4), column (mu and std)
# obtained from Table 8.20, in HAZUS earthquake technique mannual,unit: days
GFT_repair_time = [[0.4,0.1],
                   [3.0,2.2],
                   [14,12],
                   [190,80]]


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
    
    
#-----------------------Variables for output------------------------
    # repair time for facility and bridge:
repair_time_bridge = np.zeros((N_bridge, plan_horizon+1,Nscenario))#unit: days
repair_time_edge = np.zeros((N_edge, plan_horizon+1,Nscenario))#unit: days
repair_time_facility = np.zeros((N_facility, plan_horizon+1,Nscenario))#unit: days

# repair cost for facility:
repair_cost_facility = np.zeros((N_facility, plan_horizon+1,Nscenario))#unit: $

# Total daily repair cost:
repair_costs = np.zeros((365, plan_horizon,Nscenario))#unit: $

# Total repair time:
total_repair_time = np.zeros((Nscenario, plan_horizon))


print("Start repair time loop for bridge")
#------------------------Repair time loop------------------------------------
# calculate the repair time for bridges:
for k in range(Nscenario):
    for i in range(N_bridge):
        repair_time_bridge [i][0][k] = bridge_DS[i][0][0] # the 1st column is the bridge ID   
        for j in range(plan_horizon):
            if earthquake_events[k][j] != 0:
                if bridge_DS[i][j+1][k] == 1:
                    repair_time_bridge [i][j+1][k] = abs(norm.rvs(bridge_repair_time[0][0], bridge_repair_time[0][1], 1))+bridge_repair_downtime[0]                    
                elif bridge_DS[i][j+1][k] == 2:
                    repair_time_bridge [i][j+1][k] = abs(norm.rvs(bridge_repair_time[1][0], bridge_repair_time[1][1], 1))+bridge_repair_downtime[1]
                elif bridge_DS[i][j+1][k] == 3:
                    repair_time_bridge [i][j+1][k] = abs(norm.rvs(bridge_repair_time[2][0], bridge_repair_time[2][1], 1))+bridge_repair_downtime[2]
                elif bridge_DS[i][j+1][k] == 4:
                    repair_time_bridge [i][j+1][k] = abs(norm.rvs(bridge_repair_time[3][0], bridge_repair_time[3][1], 1))+bridge_repair_downtime[3]


print("Start repair time loop for edge")                    
# calculate the repair time for edge                 
for k in range(Nscenario):
    sys.stdout.write("scenario {} ;".format(k)); sys.stdout.flush();  # print a small progress bar
    for j in range(plan_horizon):
        for i in range(N_edge):
            repair_time_edge [i][0][k] = edge_cap[i][0][0]
            if earthquake_events[k][j] != 0:
               temp_index = edge_cap[i][0][0]
               temp_relation = relationship.loc[relationship.FID_road == temp_index]
               if temp_relation.shape[0] == 0:
                   repair_time_edge[i][j+1][k] = 0
               elif temp_relation.shape[0] == 1:
                   repair_time_edge[i][j+1][k] = repair_time_bridge[temp_relation.values[0][11]][j+1][k]
               elif temp_relation.shape[0] == 2:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k])
               elif temp_relation.shape[0] == 3:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k])
               elif temp_relation.shape[0] == 4:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k]) 
               elif temp_relation.shape[0] == 5:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k]) 
               elif temp_relation.shape[0] == 6:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k]) 
               elif temp_relation.shape[0] == 7:
                  repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[6][11]][j+1][k])     
               elif temp_relation.shape[0] == 8:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[6][11]][j+1][k], repair_time_bridge[temp_relation.values[7][11]][j+1][k]) 
               elif temp_relation.shape[0] == 9:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[6][11]][j+1][k], repair_time_bridge[temp_relation.values[7][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[8][11]][j+1][k]) 
               elif temp_relation.shape[0] == 10:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[6][11]][j+1][k], repair_time_bridge[temp_relation.values[7][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[8][11]][j+1][k], repair_time_bridge[temp_relation.values[9][11]][j+1][k])
               elif temp_relation.shape[0] == 11:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[6][11]][j+1][k], repair_time_bridge[temp_relation.values[7][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[8][11]][j+1][k], repair_time_bridge[temp_relation.values[9][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[10][11]][j+1][k]) 
               elif temp_relation.shape[0] == 15:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[6][11]][j+1][k], repair_time_bridge[temp_relation.values[7][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[8][11]][j+1][k], repair_time_bridge[temp_relation.values[9][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[10][11]][j+1][k], repair_time_bridge[temp_relation.values[11][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[12][11]][j+1][k], repair_time_bridge[temp_relation.values[13][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[14][11]][j+1][k]) 
               elif temp_relation.shape[0] == 16:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[6][11]][j+1][k], repair_time_bridge[temp_relation.values[7][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[8][11]][j+1][k], repair_time_bridge[temp_relation.values[9][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[10][11]][j+1][k], repair_time_bridge[temp_relation.values[11][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[12][11]][j+1][k], repair_time_bridge[temp_relation.values[13][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[14][11]][j+1][k], repair_time_bridge[temp_relation.values[15][11]][j+1][k]) 
               elif temp_relation.shape[0] == 17:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[6][11]][j+1][k], repair_time_bridge[temp_relation.values[7][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[8][11]][j+1][k], repair_time_bridge[temp_relation.values[9][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[10][11]][j+1][k], repair_time_bridge[temp_relation.values[11][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[12][11]][j+1][k], repair_time_bridge[temp_relation.values[13][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[14][11]][j+1][k], repair_time_bridge[temp_relation.values[15][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[16][11]][j+1][k]) 
               elif temp_relation.shape[0] == 18:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[6][11]][j+1][k], repair_time_bridge[temp_relation.values[7][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[8][11]][j+1][k], repair_time_bridge[temp_relation.values[9][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[10][11]][j+1][k], repair_time_bridge[temp_relation.values[11][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[12][11]][j+1][k], repair_time_bridge[temp_relation.values[13][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[14][11]][j+1][k], repair_time_bridge[temp_relation.values[15][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[16][11]][j+1][k], repair_time_bridge[temp_relation.values[17][11]][j+1][k])
               elif temp_relation.shape[0] == 19:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[6][11]][j+1][k], repair_time_bridge[temp_relation.values[7][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[8][11]][j+1][k], repair_time_bridge[temp_relation.values[9][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[10][11]][j+1][k], repair_time_bridge[temp_relation.values[11][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[12][11]][j+1][k], repair_time_bridge[temp_relation.values[13][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[14][11]][j+1][k], repair_time_bridge[temp_relation.values[15][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[16][11]][j+1][k], repair_time_bridge[temp_relation.values[17][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[18][11]][j+1][k]) 
               elif temp_relation.shape[0] == 20:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[6][11]][j+1][k], repair_time_bridge[temp_relation.values[7][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[8][11]][j+1][k], repair_time_bridge[temp_relation.values[9][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[10][11]][j+1][k], repair_time_bridge[temp_relation.values[11][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[12][11]][j+1][k], repair_time_bridge[temp_relation.values[13][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[14][11]][j+1][k], repair_time_bridge[temp_relation.values[15][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[16][11]][j+1][k], repair_time_bridge[temp_relation.values[17][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[18][11]][j+1][k], repair_time_bridge[temp_relation.values[19][11]][j+1][k]) 
               elif temp_relation.shape[0] == 21:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[6][11]][j+1][k], repair_time_bridge[temp_relation.values[7][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[8][11]][j+1][k], repair_time_bridge[temp_relation.values[9][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[10][11]][j+1][k], repair_time_bridge[temp_relation.values[11][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[12][11]][j+1][k], repair_time_bridge[temp_relation.values[13][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[14][11]][j+1][k], repair_time_bridge[temp_relation.values[15][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[16][11]][j+1][k], repair_time_bridge[temp_relation.values[17][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[18][11]][j+1][k], repair_time_bridge[temp_relation.values[19][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[20][11]][j+1][k])

               elif temp_relation.shape[0] == 22:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[6][11]][j+1][k], repair_time_bridge[temp_relation.values[7][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[8][11]][j+1][k], repair_time_bridge[temp_relation.values[9][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[10][11]][j+1][k], repair_time_bridge[temp_relation.values[11][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[12][11]][j+1][k], repair_time_bridge[temp_relation.values[13][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[14][11]][j+1][k], repair_time_bridge[temp_relation.values[15][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[16][11]][j+1][k], repair_time_bridge[temp_relation.values[17][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[18][11]][j+1][k], repair_time_bridge[temp_relation.values[19][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[20][11]][j+1][k], repair_time_bridge[temp_relation.values[21][11]][j+1][k]) 
               elif temp_relation.shape[0] == 23:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[6][11]][j+1][k], repair_time_bridge[temp_relation.values[7][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[8][11]][j+1][k], repair_time_bridge[temp_relation.values[9][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[10][11]][j+1][k], repair_time_bridge[temp_relation.values[11][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[12][11]][j+1][k], repair_time_bridge[temp_relation.values[13][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[14][11]][j+1][k], repair_time_bridge[temp_relation.values[15][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[16][11]][j+1][k], repair_time_bridge[temp_relation.values[17][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[18][11]][j+1][k], repair_time_bridge[temp_relation.values[19][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[20][11]][j+1][k], repair_time_bridge[temp_relation.values[21][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[22][11]][j+1][k])
               elif temp_relation.shape[0] == 24:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[6][11]][j+1][k], repair_time_bridge[temp_relation.values[7][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[8][11]][j+1][k], repair_time_bridge[temp_relation.values[9][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[10][11]][j+1][k], repair_time_bridge[temp_relation.values[11][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[12][11]][j+1][k], repair_time_bridge[temp_relation.values[13][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[14][11]][j+1][k], repair_time_bridge[temp_relation.values[15][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[16][11]][j+1][k], repair_time_bridge[temp_relation.values[17][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[18][11]][j+1][k], repair_time_bridge[temp_relation.values[19][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[20][11]][j+1][k], repair_time_bridge[temp_relation.values[21][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[22][11]][j+1][k], repair_time_bridge[temp_relation.values[23][11]][j+1][k]) 
               elif temp_relation.shape[0] == 25:
                   repair_time_edge[i][j+1][k] = max(repair_time_bridge[temp_relation.values[0][11]][j+1][k], repair_time_bridge[temp_relation.values[1][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[2][11]][j+1][k], repair_time_bridge[temp_relation.values[3][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[4][11]][j+1][k], repair_time_bridge[temp_relation.values[5][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[6][11]][j+1][k], repair_time_bridge[temp_relation.values[7][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[8][11]][j+1][k], repair_time_bridge[temp_relation.values[9][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[10][11]][j+1][k], repair_time_bridge[temp_relation.values[11][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[12][11]][j+1][k], repair_time_bridge[temp_relation.values[13][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[14][11]][j+1][k], repair_time_bridge[temp_relation.values[15][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[16][11]][j+1][k], repair_time_bridge[temp_relation.values[17][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[18][11]][j+1][k], repair_time_bridge[temp_relation.values[19][11]][j+1][k],
                      repair_time_bridge[temp_relation.values[20][11]][j+1][k], repair_time_bridge[temp_relation.values[21][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[22][11]][j+1][k], repair_time_bridge[temp_relation.values[23][11]][j+1][k], 
                      repair_time_bridge[temp_relation.values[24][11]][j+1][k])


print("Start repair time loop for facility")
# calculate the repair time for facility:
for k in range(Nscenario):
    for i in range(N_facility):
        repair_time_facility [i][0][k] = facility_cap[i][0][0] # the 1st column is the facilty ID    
        for j in range(plan_horizon):
            if earthquake_events[k][j] != 0:
                if facility_DS[i][j+1][k] == 1:
                    # downtime:
                    seq1 = abs(lognorm.rvs(inspection_time[0][1],0,inspection_time[0][0], 1)) + abs(lognorm.rvs(fin_time[0][1],0, fin_time[0][0], 1))
                    seq2 = abs(lognorm.rvs(inspection_time[0][1],0, inspection_time[0][0], 1)) + abs(lognorm.rvs(eng_time[0][1],0,eng_time[0][0], 1))
                    abs(lognorm.rvs(per_time[0][1],0, per_time[0][0], 1))
                    seq3 = abs(lognorm.rvs(inspection_time[0][1], 0, inspection_time[0][0], 1))+abs(lognorm.rvs(con_time[0][1], 0, con_time[0][0], 1))
                    GFT_delay_time = max(seq1,seq2,seq3)
                    repair_time_facility [i][j+1][k] = abs(norm.rvs(GFT_repair_time[0][0], GFT_repair_time[0][1], 1))+GFT_delay_time                   
                elif facility_DS[i][j+1][k] == 2:
                    # downtime:
                    seq1 = abs(lognorm.rvs(inspection_time[1][1],0,inspection_time[1][0], 1)) + abs(lognorm.rvs(fin_time[1][1],0, fin_time[1][0], 1))
                    seq2 = abs(lognorm.rvs(inspection_time[1][1],0,inspection_time[1][0], 1)) + abs(lognorm.rvs(eng_time[1][1],0,eng_time[1][0], 1))
                    abs(lognorm.rvs(per_time[1][1],0, per_time[1][0], 1))
                    seq3 = abs(lognorm.rvs(inspection_time[1][1], 0, inspection_time[1][0], 1))+abs(lognorm.rvs(con_time[1][1], 0, con_time[1][0], 1))
                    GFT_delay_time = max(seq1,seq2,seq3)
                    repair_time_facility [i][j+1][k] = abs(norm.rvs(GFT_repair_time[1][0], GFT_repair_time[1][1], 1))+GFT_delay_time 
                elif facility_DS[i][j+1][k] == 3:
                    # downtime:
                    seq1 = abs(lognorm.rvs(inspection_time[2][1],0,inspection_time[2][0], 1)) + abs(lognorm.rvs(fin_time[2][1],0, fin_time[2][0], 1))
                    seq2 = abs(lognorm.rvs(inspection_time[2][1],0,inspection_time[2][0], 1)) + abs(lognorm.rvs(eng_time[2][1],0,eng_time[2][0], 1))
                    abs(lognorm.rvs(per_time[2][1],0, per_time[2][0], 1))
                    seq3 = abs(lognorm.rvs(inspection_time[2][1], 0, inspection_time[2][0], 1))+abs(lognorm.rvs(con_time[2][1], 0, con_time[2][0], 1))
                    GFT_delay_time = max(seq1,seq2,seq3)
                    repair_time_facility [i][j+1][k] = abs(norm.rvs(GFT_repair_time[2][0], GFT_repair_time[2][1], 1))+GFT_delay_time 
                elif facility_DS[i][j+1][k] == 4:
                    # downtime:
                    seq1 = abs(lognorm.rvs(inspection_time[3][1],0,inspection_time[3][0], 1)) + abs(lognorm.rvs(fin_time[3][1],0, fin_time[3][0], 1))
                    seq2 = abs(lognorm.rvs(inspection_time[3][1],0,inspection_time[3][0], 1)) + abs(lognorm.rvs(eng_time[3][1],0,eng_time[3][0], 1))
                    abs(lognorm.rvs(per_time[3][1],0, per_time[3][0], 1))
                    seq3 = abs(lognorm.rvs(inspection_time[3][1], 0, inspection_time[3][0], 1))+abs(lognorm.rvs(con_time[3][1], 0, con_time[3][0], 1))
                    GFT_delay_time = max(seq1,seq2,seq3)
                    repair_time_facility [i][j+1][k] = abs(norm.rvs(GFT_repair_time[3][0], GFT_repair_time[3][1], 1))+GFT_delay_time 

print("Start repair time")
# Total repair time
for k in range(Nscenario):
    for j in range(plan_horizon):
        total_repair_time[k][j] =int( max(max(repair_time_facility[:,j+1,k]), max(repair_time_edge[:,j+1,k])))

#------------------------Repair cost loop-------------------------------------------
# calculate the daily repair cost for each facility:
for k in range(Nscenario):
    for i in range(N_facility):
        repair_cost_facility [i][0][k] = facility_cap[i][0][0] # the 1st column is the facilty ID    
        for j in range(plan_horizon):
            if earthquake_events[k][j] != 0:
                if facility_DS[i][j+1][k] == 1:
                    repair_cost_facility [i][j+1][k] = GFT_repair_cost[0]/(repair_time_facility[i][j+1][k]+0.001)
                elif facility_DS[i][j+1][k] == 2:
                     repair_cost_facility [i][j+1][k] = GFT_repair_cost[1]/(repair_time_facility[i][j+1][k]+0.001)
                elif facility_DS[i][j+1][k] == 3:
                     repair_cost_facility [i][j+1][k] = GFT_repair_cost[2]/(repair_time_facility[i][j+1][k]+0.001)
                elif facility_DS[i][j+1][k] == 4:
                     repair_cost_facility [i][j+1][k] = GFT_repair_cost[3]/(repair_time_facility[i][j+1][k]+0.001)                        
                       

# calculate the daily repair cost for all facilities:
for k in range(Nscenario):
    for i in range(365):
        for j in range(plan_horizon):
            if earthquake_events[k][j] != 0:                     
               for f in range (N_facility):
                   if repair_time_facility[f][j+1][k] > i:
                       repair_costs[i][j][k] = repair_costs[i][j][k] + repair_cost_facility[f][j+1][k]



print("Saving repair_costs.npy")
np.save("repair_costs.npy",repair_costs)
print("Saving repair_time_edge.npy")
np.save("repair_time_edge.npy", repair_time_edge)
print("Saving repair_time_facility.npy")
np.save("repair_time_facility.npy",repair_time_facility) 
print("Saving total_repair_time.npy")
np.save("total_repair_time.npy", total_repair_time)

















