
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 2020

@author: Jie Zhao
"""
import numpy as np
import pandas as pd
import math

# added by Mark
import os
os.chdir("C:\FTOT-SCR\scenarios\ForestResiduals_SCR\input_data")


# Total number of scenarios
Nscenario = 30
# Planning Horizon
plan_horizon = 20 # unit: year

# ---------------------Load bridge and edge TXT files--------------------
data_bridge = pd.read_csv("HighwayBridge_3state.txt")
bridge = pd. DataFrame (data_bridge)
data_Bridge_Edge = pd.read_csv("Relationship_BridgeRoad_3state.txt")
relationship = pd. DataFrame (data_Bridge_Edge) 
data_edge = pd.read_csv("MiddlePoint_Road.txt")
edge = pd. DataFrame (data_edge) 

N_bridge = len(bridge) # Tatal amount of bridges
N_edge = len(edge) # Tatal amount of edges

# load seismic information 
#seismic_catalog = np.load("seismic_catalog.npy")
earthquake_events = np.load("earthquake_events.npy")
# Bridge location 
# bridge_loc = np.load("bridge_loc.npy")

# load bridge damage cells
BDI = np.load("BDI.npy")   
bridge_DS = np.load("bridge_DS.npy")  

#----------------------Variables for output-------------------------------
# Capacity matrix for edges
# row (edge), 
# column (ID,1st year, 2nd year,..., 20th year)
# 3-dimension (scenario)
edge_cap = np.ones((N_edge, plan_horizon+1,Nscenario))
# Link Damage Index :LDI
LDI = np.zeros((N_edge, plan_horizon+1,Nscenario))

#---------------------Test -----------------------------------------------
# find the most bridges for a specific edge
dup=relationship['FID_road'].value_counts()
#print(dup)
# this outcomes shows that edge 35268 has maiximum amount of bridge, which is 25
"""
# Relationship between edges and bridges: represented by bridge_edge matrix with brinary variables
# row (edges), column(bridges)
# brinary variables, 1 is bridge in this edge, otherwise, 0 
try_ = np.zeros((10,10))

for i in range(10):
    matric = relationship.loc[relationship.FID_road_selection == i+30]
    if matric.shape[0] == 0:
        try_[i][1] = uniform.rvs(size=1, loc = 0, scale=1)
    elif matric.shape[0] != 0:
        try_[i][1] = math.sqrt(sum(matric.values[:,2]*matric.values[:,2].T))
        


temp_index = edge.values[1524][1]
temp_relation = relationship.loc[relationship.FID_road ==temp_index ]
print(temp_relation)

""" 
  
# ---------------------Capacity matrix for edge-----------------------------------
print("looping through scenarios") #added by Mark
for k in range(Nscenario):
    print("working on: scenario " + str(k)) # added by Mark
    for j in range(plan_horizon):
        print("year: " + str(j)) # added by Mark
        for i in range(N_edge):
            edge_cap [i][0][k] = edge.values[i][1]  
            if earthquake_events[k][j] != 0:
               temp_index = edge.values[i][1] 
               temp_relation = relationship.loc[relationship.FID_road == temp_index]
               if temp_relation.shape[0] == 0:
                   LDI[i][j+1][k] = 0
               elif temp_relation.shape[0] == 1:
                   # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = BDI[temp_relation.values[0][11]][j+1][k]
               elif temp_relation.shape[0] == 2:
                   # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2)
               elif temp_relation.shape[0] == 3:
                # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2)
               elif temp_relation.shape[0] == 4:
                # calculate Link Damage Index (LDI)
                  LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2) 
               elif temp_relation.shape[0] == 5:
                # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2) 
               elif temp_relation.shape[0] == 6:
                # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2) 
               elif temp_relation.shape[0] == 7:
                   # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2+
                      BDI[temp_relation.values[6][11]][j+1][k]**2)     
               elif temp_relation.shape[0] == 8:
                # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2+
                      BDI[temp_relation.values[6][11]][j+1][k]**2+BDI[temp_relation.values[7][11]][j+1][k]**2) 
               elif temp_relation.shape[0] == 9:
                # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2+
                      BDI[temp_relation.values[6][11]][j+1][k]**2+BDI[temp_relation.values[7][11]][j+1][k]**2+
                      BDI[temp_relation.values[8][11]][j+1][k]**2) 
               elif temp_relation.shape[0] == 10:
                # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2+
                      BDI[temp_relation.values[6][11]][j+1][k]**2+BDI[temp_relation.values[7][11]][j+1][k]**2+
                      BDI[temp_relation.values[8][11]][j+1][k]**2+BDI[temp_relation.values[9][11]][j+1][k]**2)
               elif temp_relation.shape[0] == 11:
                # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2+
                      BDI[temp_relation.values[6][11]][j+1][k]**2+BDI[temp_relation.values[7][11]][j+1][k]**2+
                      BDI[temp_relation.values[8][11]][j+1][k]**2+BDI[temp_relation.values[9][11]][j+1][k]**2+
                      BDI[temp_relation.values[10][11]][j+1][k]**2) 
               elif temp_relation.shape[0] == 15:
                   # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2+
                      BDI[temp_relation.values[6][11]][j+1][k]**2+BDI[temp_relation.values[7][11]][j+1][k]**2+
                      BDI[temp_relation.values[8][11]][j+1][k]**2+BDI[temp_relation.values[9][11]][j+1][k]**2+
                      BDI[temp_relation.values[10][11]][j+1][k]**2+BDI[temp_relation.values[11][11]][j+1][k]**2+
                      BDI[temp_relation.values[12][11]][j+1][k]**2+BDI[temp_relation.values[13][11]][j+1][k]**2+
                      BDI[temp_relation.values[14][11]][j+1][k]**2) 
               elif temp_relation.shape[0] == 16:
                   # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2+
                      BDI[temp_relation.values[6][11]][j+1][k]**2+BDI[temp_relation.values[7][11]][j+1][k]**2+
                      BDI[temp_relation.values[8][11]][j+1][k]**2+BDI[temp_relation.values[9][11]][j+1][k]**2+
                      BDI[temp_relation.values[10][11]][j+1][k]**2+BDI[temp_relation.values[11][11]][j+1][k]**2+
                      BDI[temp_relation.values[12][11]][j+1][k]**2+BDI[temp_relation.values[13][11]][j+1][k]**2+
                      BDI[temp_relation.values[14][11]][j+1][k]**2+BDI[temp_relation.values[15][11]][j+1][k]**2) 
               elif temp_relation.shape[0] == 17:
                   # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2+
                      BDI[temp_relation.values[6][11]][j+1][k]**2+BDI[temp_relation.values[7][11]][j+1][k]**2+
                      BDI[temp_relation.values[8][11]][j+1][k]**2+BDI[temp_relation.values[9][11]][j+1][k]**2+
                      BDI[temp_relation.values[10][11]][j+1][k]**2+BDI[temp_relation.values[11][11]][j+1][k]**2+
                      BDI[temp_relation.values[12][11]][j+1][k]**2+BDI[temp_relation.values[13][11]][j+1][k]**2+
                      BDI[temp_relation.values[14][11]][j+1][k]**2+BDI[temp_relation.values[15][11]][j+1][k]**2+
                      BDI[temp_relation.values[16][11]][j+1][k]**2)
               elif temp_relation.shape[0] == 18:
                   # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2+
                      BDI[temp_relation.values[6][11]][j+1][k]**2+BDI[temp_relation.values[7][11]][j+1][k]**2+
                      BDI[temp_relation.values[8][11]][j+1][k]**2+BDI[temp_relation.values[9][11]][j+1][k]**2+
                      BDI[temp_relation.values[10][11]][j+1][k]**2+BDI[temp_relation.values[11][11]][j+1][k]**2+
                      BDI[temp_relation.values[12][11]][j+1][k]**2+BDI[temp_relation.values[13][11]][j+1][k]**2+
                      BDI[temp_relation.values[14][11]][j+1][k]**2+BDI[temp_relation.values[15][11]][j+1][k]**2+
                      BDI[temp_relation.values[16][11]][j+1][k]**2+BDI[temp_relation.values[17][11]][j+1][k]**2)
               elif temp_relation.shape[0] == 19:
                   # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2+
                      BDI[temp_relation.values[6][11]][j+1][k]**2+BDI[temp_relation.values[7][11]][j+1][k]**2+
                      BDI[temp_relation.values[8][11]][j+1][k]**2+BDI[temp_relation.values[9][11]][j+1][k]**2+
                      BDI[temp_relation.values[10][11]][j+1][k]**2+BDI[temp_relation.values[11][11]][j+1][k]**2+
                      BDI[temp_relation.values[12][11]][j+1][k]**2+BDI[temp_relation.values[13][11]][j+1][k]**2+
                      BDI[temp_relation.values[14][11]][j+1][k]**2+BDI[temp_relation.values[15][11]][j+1][k]**2+
                      BDI[temp_relation.values[16][11]][j+1][k]**2+BDI[temp_relation.values[17][11]][j+1][k]**2+
                      BDI[temp_relation.values[18][11]][j+1][k]**2)        
               elif temp_relation.shape[0] == 20:
                   # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2+
                      BDI[temp_relation.values[6][11]][j+1][k]**2+BDI[temp_relation.values[7][11]][j+1][k]**2+
                      BDI[temp_relation.values[8][11]][j+1][k]**2+BDI[temp_relation.values[9][11]][j+1][k]**2+
                      BDI[temp_relation.values[10][11]][j+1][k]**2+BDI[temp_relation.values[11][11]][j+1][k]**2+
                      BDI[temp_relation.values[12][11]][j+1][k]**2+BDI[temp_relation.values[13][11]][j+1][k]**2+
                      BDI[temp_relation.values[14][11]][j+1][k]**2+BDI[temp_relation.values[15][11]][j+1][k]**2+
                      BDI[temp_relation.values[16][11]][j+1][k]**2+BDI[temp_relation.values[17][11]][j+1][k]**2+
                      BDI[temp_relation.values[18][11]][j+1][k]**2+BDI[temp_relation.values[19][11]][j+1][k]**2)
               elif temp_relation.shape[0] == 21:
                   # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2+
                      BDI[temp_relation.values[6][11]][j+1][k]**2+BDI[temp_relation.values[7][11]][j+1][k]**2+
                      BDI[temp_relation.values[8][11]][j+1][k]**2+BDI[temp_relation.values[9][11]][j+1][k]**2+
                      BDI[temp_relation.values[10][11]][j+1][k]**2+BDI[temp_relation.values[11][11]][j+1][k]**2+
                      BDI[temp_relation.values[12][11]][j+1][k]**2+BDI[temp_relation.values[13][11]][j+1][k]**2+
                      BDI[temp_relation.values[14][11]][j+1][k]**2+BDI[temp_relation.values[15][11]][j+1][k]**2+
                      BDI[temp_relation.values[16][11]][j+1][k]**2+BDI[temp_relation.values[17][11]][j+1][k]**2+
                      BDI[temp_relation.values[18][11]][j+1][k]**2+BDI[temp_relation.values[19][11]][j+1][k]**2+
                      BDI[temp_relation.values[20][11]][j+1][k]**2)                   
               elif temp_relation.shape[0] == 22:
                   # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2+
                      BDI[temp_relation.values[6][11]][j+1][k]**2+BDI[temp_relation.values[7][11]][j+1][k]**2+
                      BDI[temp_relation.values[8][11]][j+1][k]**2+BDI[temp_relation.values[9][11]][j+1][k]**2+
                      BDI[temp_relation.values[10][11]][j+1][k]**2+BDI[temp_relation.values[11][11]][j+1][k]**2+
                      BDI[temp_relation.values[12][11]][j+1][k]**2+BDI[temp_relation.values[13][11]][j+1][k]**2+
                      BDI[temp_relation.values[14][11]][j+1][k]**2+BDI[temp_relation.values[15][11]][j+1][k]**2+
                      BDI[temp_relation.values[16][11]][j+1][k]**2+BDI[temp_relation.values[17][11]][j+1][k]**2+
                      BDI[temp_relation.values[18][11]][j+1][k]**2+BDI[temp_relation.values[19][11]][j+1][k]**2+
                      BDI[temp_relation.values[20][11]][j+1][k]**2+BDI[temp_relation.values[21][11]][j+1][k]**2)                   
               elif temp_relation.shape[0] == 23:
                   # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2+
                      BDI[temp_relation.values[6][11]][j+1][k]**2+BDI[temp_relation.values[7][11]][j+1][k]**2+
                      BDI[temp_relation.values[8][11]][j+1][k]**2+BDI[temp_relation.values[9][11]][j+1][k]**2+
                      BDI[temp_relation.values[10][11]][j+1][k]**2+BDI[temp_relation.values[11][11]][j+1][k]**2+
                      BDI[temp_relation.values[12][11]][j+1][k]**2+BDI[temp_relation.values[13][11]][j+1][k]**2+
                      BDI[temp_relation.values[14][11]][j+1][k]**2+BDI[temp_relation.values[15][11]][j+1][k]**2+
                      BDI[temp_relation.values[16][11]][j+1][k]**2+BDI[temp_relation.values[17][11]][j+1][k]**2+
                      BDI[temp_relation.values[18][11]][j+1][k]**2+BDI[temp_relation.values[19][11]][j+1][k]**2+
                      BDI[temp_relation.values[20][11]][j+1][k]**2+BDI[temp_relation.values[21][11]][j+1][k]**2+
                      BDI[temp_relation.values[22][11]][j+1][k]**2)                   
               elif temp_relation.shape[0] == 24:
                   # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2+
                      BDI[temp_relation.values[6][11]][j+1][k]**2+BDI[temp_relation.values[7][11]][j+1][k]**2+
                      BDI[temp_relation.values[8][11]][j+1][k]**2+BDI[temp_relation.values[9][11]][j+1][k]**2+
                      BDI[temp_relation.values[10][11]][j+1][k]**2+BDI[temp_relation.values[11][11]][j+1][k]**2+
                      BDI[temp_relation.values[12][11]][j+1][k]**2+BDI[temp_relation.values[13][11]][j+1][k]**2+
                      BDI[temp_relation.values[14][11]][j+1][k]**2+BDI[temp_relation.values[15][11]][j+1][k]**2+
                      BDI[temp_relation.values[16][11]][j+1][k]**2+BDI[temp_relation.values[17][11]][j+1][k]**2+
                      BDI[temp_relation.values[18][11]][j+1][k]**2+BDI[temp_relation.values[19][11]][j+1][k]**2+
                      BDI[temp_relation.values[20][11]][j+1][k]**2+BDI[temp_relation.values[21][11]][j+1][k]**2+
                      BDI[temp_relation.values[22][11]][j+1][k]**2+BDI[temp_relation.values[23][11]][j+1][k]**2)                   
               elif temp_relation.shape[0] == 25:
                   # calculate Link Damage Index (LDI)
                   LDI[i][j+1][k] = math.sqrt(BDI[temp_relation.values[0][11]][j+1][k]**2+BDI[temp_relation.values[1][11]][j+1][k]**2+
                      BDI[temp_relation.values[2][11]][j+1][k]**2+BDI[temp_relation.values[3][11]][j+1][k]**2+
                      BDI[temp_relation.values[4][11]][j+1][k]**2+BDI[temp_relation.values[5][11]][j+1][k]**2+
                      BDI[temp_relation.values[6][11]][j+1][k]**2+BDI[temp_relation.values[7][11]][j+1][k]**2+
                      BDI[temp_relation.values[8][11]][j+1][k]**2+BDI[temp_relation.values[9][11]][j+1][k]**2+
                      BDI[temp_relation.values[10][11]][j+1][k]**2+BDI[temp_relation.values[11][11]][j+1][k]**2+
                      BDI[temp_relation.values[12][11]][j+1][k]**2+BDI[temp_relation.values[13][11]][j+1][k]**2+
                      BDI[temp_relation.values[14][11]][j+1][k]**2+BDI[temp_relation.values[15][11]][j+1][k]**2+
                      BDI[temp_relation.values[16][11]][j+1][k]**2+BDI[temp_relation.values[17][11]][j+1][k]**2+
                      BDI[temp_relation.values[18][11]][j+1][k]**2+BDI[temp_relation.values[19][11]][j+1][k]**2+
                      BDI[temp_relation.values[20][11]][j+1][k]**2+BDI[temp_relation.values[21][11]][j+1][k]**2+
                      BDI[temp_relation.values[22][11]][j+1][k]**2+BDI[temp_relation.values[23][11]][j+1][k]**2+
                      BDI[temp_relation.values[24][11]][j+1][k]**2) 

                   
               # Changes in Link capacity as Function of Link Damage Index, based on following relationship (Shiraki et al., 2007):
               # capacity=0.5 --- 1.5 < LDI 
               # capacity=0.5 --- 1.0 < LDI <= 1.5
               # capacity=0.75 --- 0.5 < LDI <= 1.0
               # capacity=1 --- otherwise
                            
               if LDI[i][j+1][k] > 1.5:
                  edge_cap[i][j+1][k] = 0.5
               elif 1.0 <= LDI[i][j+1][k] < 1.5:
                  edge_cap[i][j+1][k] = 0.5
               elif 0.5 <= LDI[i][j+1][k] < 1.0:
                  edge_cap[i][j+1][k] = 0.75

             

# print(edge_cap[:,:,0])              
                
print("Saving edge_cap.npy")  
np.save("edge_cap.npy", edge_cap)         
        
edge_damage_count = np.zeros((Nscenario, plan_horizon,2))# 2 menas edge_cap = 0.75 and 0.5

for i in range (Nscenario):
    for j in range (plan_horizon):
        edge_damage_count[i][j][0] = np.sum(edge_cap[:,j+1,i]==0.75)
        edge_damage_count[i][j][1] = np.sum(edge_cap[:,j+1,i]==0.5)
"""        

aa = edge.values[16849][1] 
print(aa)
bb = relationship.loc[relationship.FID_road == aa]
print(bb)
print(bb.values[0][11])
print(BDI[bb.values[0][11]][16][0])  
print(earthquake_events[0][15]) 
print(LDI[16849][16][0])  
        
"""       
        
        