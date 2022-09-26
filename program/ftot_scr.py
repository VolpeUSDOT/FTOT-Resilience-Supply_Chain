# ---------------------------------------------------------------------------------------------------
# Name: ftot_scr.py
#
# Purpose: This module is used to organize a supply chain resilience analysis using multiple runs of the o step. .
#
# ---------------------------------------------------------------------------------------------------

import datetime
import pdb
import re
import sqlite3
from collections import defaultdict
import os
from six import iteritems

from pulp import *

import ftot_supporting
from ftot_supporting import get_total_runtime_string
from ftot import Q_
import numpy as np

# constants
storage = 1
primary = 0
fixed_schedule_id = 2
fixed_route_duration = 0

THOUSAND_GALLONS_PER_THOUSAND_BARRELS = 42

storage_cost_1 = 0.01
storage_cost_2 = 0.05
facility_onsite_storage_max = 10000000000
facility_onsite_storage_min = 0

default_max_capacity = 10000000000
default_min_capacity = 0

zero_threshold=0.00001

# MODIFICATION - load input files
os.chdir("C:\FTOT-SCR\scenarios\ForestResiduals_SCR\input_data")
#==================load output from newly developed Python files=====
# load facility capacity index 
facility_cap_noEarthquake = np.load("facility_cap_noEarthquake.npy")
facility_cap = np.load("facility_cap.npy")
# load facility damage state index 
facility_DS = np.load("facility_DS.npy")

# load repair cost array:
repair_costs = np.load("repair_costs.npy")

# Load edge capacity index
edge_cap = np.load("edge_cap.npy")
# load bridge damage state index
bridge_DS = np.load("bridge_DS.npy")

# load reair time array:
repair_time_facility = np.load("repair_time_facility.npy")
repair_time_edge = np.load("repair_time_edge.npy")

# load catalyst replament cost
CatalystReplace_cost = np.load("CatalystReplace_cost.npy")
# GFT facility operation cost
operation_cost = 12404848 # unit:$ (2007 dollars)
# daily index
daily_index = float(1)/float(365)
#unmet_demand_yearly = np.zeros((N,plan_horizon))
#costs_yearly = np.zeros((N,plan_horizon))
number = np.zeros(len(facility_cap_noEarthquake[:,0,0]))
for i in range(len(number)):
    number[i] = i   

# END MODIFICATION

FTOT_VERSION = "2022.1"
SCHEMA_VERSION = "6.0.2"
VERSION_DATE = "4/1/2022"

def supply_chain_scenarios(the_scenario, logger): 
    earthquake_scenario = np.load("earthquake_events.npy")
    total_repair_time = np.load("total_repair_time.npy")

    total_fuel_amount = 2941633.8
    # planning horizon in this example: 20 years
    plan_horizon = 20 # unit: year
    # total scenario amount:  here we consider 30 scenarios
    N = 30
    # resilience array
    Resilience = np.zeros((N))
    R1 = np.zeros((N))
    R2 = np.zeros((N))
    R3 = np.zeros((N))
    weight1 = np.zeros((N))
    weight2 = np.zeros((N))
    weight3 = np.zeros((N))

    # simulation weeks in one year
    WeekInYear = 52
    DayInYear = 52*7
    # Unmet demand threshold
    UD_level = 4190600
    # Total final demand
    total_demand_fuel = 136497 # total demand for this supply chain layout
    total_final_demand = 4073312.9 + 254401.1 # total demand before optimization
    # Variables for output from optimization
    #UnmetDemandAmount = np.zeros((int(WeekInYear*7),plan_horizon, N))
    #DailyCost = np.zeros((int(WeekInYear*7),plan_horizon, N))
    #np.save("UnmetDemandAmount.npy", UnmetDemandAmount)
    #np.save("DailyCost.npy", DailyCost)


    # for each scenario and time:
    for i in range(N):
        UnmetDemandAmount = np.load("UnmetDemandAmount.npy")
        DailyCost = np.load("DailyCost.npy")
        cost1 = 0
        cost2 = 0
        cost3 = 0
        w1 = np.zeros((plan_horizon))
        w2 = np.zeros((plan_horizon))
        w3 = np.zeros((plan_horizon))
        scenario_num = i
        np.save("scenario_num.npy", scenario_num)
        for t in range(1,plan_horizon):
            time_horizon = t
            np.save("time_horizon.npy", time_horizon)                        
            # for non earthquake occurrence scenario: weekly basis interval   
            if earthquake_scenario[i][t] != 0:
                temp_repair_week = float(total_repair_time[i][t])/float(7) # one week = 7 days 
                for j in range(WeekInYear):
                    earthquake_week = j
                    #temp_day = int(7*j)
                    np.save("earthquake_week.npy", earthquake_week)

                    o1scr(the_scenario, logger, "weekly")
                    o2scr(the_scenario, logger, "weekly")

                    for day_1 in range (int(j*7),int((j+1)*7)):
                        UnmetDemandAmount[day_1][t][i] = np.load("unmet_demand_daily.npy")
                        DailyCost[day_1][t][i]  = np.load("costs_daily.npy")  

                        np.save("UnmetDemandAmount.npy", UnmetDemandAmount)
                        np.save("DailyCost.npy", DailyCost)


                    # Calculate initial daily costs for each scenario
                    temp_day = int(7*j)
                    daily_cost = DailyCost[temp_day][t][i] - UnmetDemandAmount[0][0][0] * 5000
                    initial_cost = DailyCost[0][0][0] - UnmetDemandAmount[0][0][0] * 5000
                    UD = UnmetDemandAmount[temp_day][t][i] - float(UD_level)/float(DayInYear)
                    UDR = float(UD*DayInYear)/float(total_demand_fuel)
                    production = float(total_final_demand)/float(DayInYear) - UnmetDemandAmount[temp_day][t][i]


                    if j <= temp_repair_week:
                        UDP = abs(UD * 5000)
                        R2[i] = R2[i] + (float(daily_cost-initial_cost + UDP)/float(production))*7
                        w2[t] = w2[t] + (float(daily_cost-initial_cost + UDP)/float(production))

                    else:
                        if UDR  > 0:
                            UDP = UD * 5000
                            R1[i] = R1[i] + (float(daily_cost-initial_cost + UDP)/float(production))*7
                            w1[t] = w1[t] + (float(daily_cost-initial_cost + UDP)/float(production))

                        else:
                            R3[i] = R3[i] + (float(daily_cost-initial_cost)/float(production))*7
                            w3[t] = w3[t] + (float(daily_cost-initial_cost)/float(production))

                # weight factor for R2
                weight2[i] = weight2[i] + float(sum(w2[:]))/float(temp_repair_week + 0.01)      


            # for non earthquake occurrence scenario: yearly basis interval   
            else:
                o1scr(the_scenario, logger, "yearly")
                o2scr(the_scenario, logger, "yearly")

                temp_demand = np.load("unmet_demand_yearly.npy")
                UnmetDemandAmount[:,t,i] = float(temp_demand)/float(DayInYear)
                temp_dailycost= np.load("costs_yearly.npy")
                DailyCost[:,t,i] = float(temp_dailycost)/float(DayInYear)
                np.save("UnmetDemandAmount.npy", UnmetDemandAmount)
                np.save("DailyCost.npy", DailyCost)

                # Calculate initial daily costs for each scenario
                temp_day = 2 # either day is okay, because daily cost is the same for every day
                daily_cost = DailyCost[temp_day][t][i] - UnmetDemandAmount[0][0][0] * 5000
                initial_cost = DailyCost[0][0][0]- UnmetDemandAmount[0][0][0] * 5000
                UD = UnmetDemandAmount[temp_day][t][i] - float(UD_level)/float(DayInYear)
                UDR = float(UD*DayInYear)/float(total_demand_fuel)
                production = float(total_final_demand)/float(DayInYear) - UnmetDemandAmount[temp_day][t][i]

                if UDR  > 0:
                    UDP = UD * 5000
                    R1[i] = R1[i] + (float(daily_cost-initial_cost + UDP)/float(production))*DayInYear
                    w1[t] = w1[t] + (float(daily_cost-initial_cost + UDP)/float(production))
                else:
                    R3[i] = R3[i] + (float(daily_cost-initial_cost)/float(production))*DayInYear
                    w3[t] = w3[t] + (float(daily_cost-initial_cost)/float(production))

            # weight factor for each resilience componenet equals to average daily cost                    
        weight1[i] = float(sum(w1[:]))/float(np.count_nonzero(w1) + 0.01)
        weight2[i] = float(weight2[i])/float(np.count_nonzero(earthquake_scenario[i,:])+0.01)
        weight3[i] = float(sum(w3[:]))/float(np.count_nonzero(w3)+0.01)
        # assume the same weight for resilience cost and initial cost
        weight_factor = 1

        Resilience[i] = weight_factor*(-abs(weight1[i]*R1[i]) - abs(weight2[i]*R2[i]) + abs(weight3[i]*R3[i])) + initial_cost*DayInYear*plan_horizon
        #Resilience[i] = weight_factor*(weight1[i]*R1[i] + weight2[i]*R2[i] + weight3[i]*R3[i])+initial_cost*year*plan_horizon
        
        logger.info("Weight for hazard-induced CLF for scenario {}: {}".format(i,weight2[i]))
        logger.info("Weight for non-hazard-induced CLF for scenario {}: {}".format(i,weight1[i]))
        logger.info("Weight for opportunity-induced CGF for scenario {}: {}".format(i,weight3[i]))
        logger.info("Resilience for scenario {} : {}".format(i,Resilience[i]))


        np.save("R1.npy",R1)
        np.save("R2.npy",R2)
        np.save("R3.npy",R3)
        np.save("weight1.npy",weight1)
        np.save("weight2.npy",weight2)
        np.save("weight3.npy",weight3)
        np.save("Resilience.npy",Resilience)


# ===============================================================================


def o1scr(the_scenario, logger, time_period):

    import ftot_pulp
    # create vertices, then edges for permitted modes, then set volume & capacity on edges

    logger.info("START: pre_setup_pulp")
    ftot_pulp.commodity_mode_setup(the_scenario, logger)
    ftot_pulp.source_tracking_setup(the_scenario, logger)
    schedule_dict, schedule_length = ftot_pulp.generate_schedules(the_scenario, logger)
    generate_all_vertices(the_scenario, schedule_dict, schedule_length, time_period, logger)
    ftot_pulp.add_storage_routes(the_scenario, logger)
    ftot_pulp.generate_connector_and_storage_edges(the_scenario, logger)

    from ftot_networkx import update_ndr_parameter
    update_ndr_parameter(the_scenario, logger)

    if not the_scenario.ndrOn:
        # start edges for commodities that inherit max transport distance
        ftot_pulp.generate_first_edges_from_source_facilities(the_scenario, schedule_length, logger)

        # replicate all_routes by commodity and time into all_edges dictionary
        ftot_pulp.generate_all_edges_from_source_facilities(the_scenario, schedule_length, logger)

        # replicate all_routes by commodity and time into all_edges dictionary
        ftot_pulp.generate_all_edges_without_max_commodity_constraint(the_scenario, schedule_length, logger)
        logger.info("Edges generated for modes: {}".format(the_scenario.permittedModes))

    else:
        ftot_pulp.generate_edges_from_routes(the_scenario, schedule_length, logger)

    ftot_pulp.set_edges_volume_capacity(the_scenario, logger)

    return


# ===============================================================================


def o2scr(the_scenario, logger, time_period):
    import ftot_pulp
    # create variables, problem to optimize, and constraints
    prob = setup_pulp_problem(the_scenario, time_period, logger)
    prob = ftot_pulp.solve_pulp_problem(prob, the_scenario, logger)
    save_pulp_solution(the_scenario, prob, logger, time_period, zero_threshold)
    ftot_pulp.record_pulp_solution(the_scenario, logger)
    from ftot_supporting import post_optimization
    post_optimization(the_scenario, 'o2', logger)

    return


# ===============================================================================


def setup_pulp_problem(the_scenario, time_period, logger):
    import ftot_pulp
    logger.info("START: setup PuLP problem")

    # flow_var is the flow on each edge by commodity and day.
    # the optimal value of flow_var will be solved by PuLP
    flow_vars = ftot_pulp.create_flow_vars(the_scenario, logger)

    # unmet_demand_var is the unmet demand at each destination, being determined
    unmet_demand_vars = create_unmet_demand_vars(the_scenario, logger)

    # processor_build_vars is the binary variable indicating whether a candidate processor is used
    # and thus whether its build cost is charged
    processor_build_vars = ftot_pulp.create_candidate_processor_build_vars(the_scenario, logger)

    # binary tracker variables
    processor_vertex_flow_vars = ftot_pulp.create_binary_processor_vertex_flow_vars(the_scenario, logger)

    # tracking unused production
    processor_excess_vars = ftot_pulp.create_processor_excess_output_vars(the_scenario, logger)

    # THIS IS THE OBJECTIVE FUCTION FOR THE OPTIMIZATION
    # ==================================================

    prob = create_opt_problem(logger, the_scenario, unmet_demand_vars, flow_vars, processor_build_vars)

    prob = ftot_pulp.create_constraint_unmet_demand(logger, the_scenario, prob, flow_vars, unmet_demand_vars)

    prob = ftot_pulp.create_constraint_max_flow_out_of_supply_vertex(logger, the_scenario, prob, flow_vars)

    # This constraint is being excluded because 1) it is not used in current scenarios and 2) it is not supported by
    # this version - it conflicts with the change permitting multiple inputs
    prob = create_constraint_daily_processor_capacity(logger, the_scenario, prob, flow_vars, processor_build_vars,
                                                       processor_vertex_flow_vars, time_period)

    prob = create_primary_processor_vertex_constraints(logger, the_scenario, prob, flow_vars)

    prob = ftot_pulp.create_constraint_conservation_of_flow(logger, the_scenario, prob, flow_vars, processor_excess_vars)

    if the_scenario.capacityOn:
        prob = create_constraint_max_route_capacity(logger, the_scenario, prob, flow_vars)

        prob = ftot_pulp.create_constraint_pipeline_capacity(logger, the_scenario, prob, flow_vars)

    del unmet_demand_vars

    del flow_vars

    # The problem data is written to an .lp file
    prob.writeLP(os.path.join(the_scenario.scenario_run_directory, "debug", "LP_output_c2.lp"))

    logger.info("FINISHED: setup PuLP problem")
    return prob


# ===============================================================================


def generate_all_vertices(the_scenario, schedule_dict, schedule_length, time_period, logger):
    logger.info("START: generate_all_vertices table")

    # BEGIN MODIFICATION - logging
    i = np.load("scenario_num.npy")
    t = np.load("time_horizon.npy")
    logger.info("scenario {}".format(i))
    logger.info("time horizon {}".format(t))
    if time_period == "weekly" :
        j = np.load("earthquake_week.npy")
        logger.info("earthquake week {}".format(j))
    # END MODIFICATION
    
    total_potential_production = {}
    multi_commodity_name = "multicommodity"

    storage_availability = 1

    with sqlite3.connect(the_scenario.main_db) as main_db_con:

        logger.debug("create the vertices table")
        # create the vertices table
        main_db_con.executescript("""
        drop table if exists vertices
        ;

        create table if not exists vertices (
        vertex_id INTEGER PRIMARY KEY, location_id,
        facility_id integer, facility_name text, facility_type_id integer, schedule_day integer,
        commodity_id integer, activity_level numeric, storage_vertex binary,
        udp numeric, supply numeric, demand numeric,
        source_facility_id integer,
        iob text, --allows input, output, or both
        CONSTRAINT unique_vertex UNIQUE(facility_id, schedule_day, commodity_id, source_facility_id, storage_vertex))
        ;""")

        # create indexes for the networkx nodes and links tables
        logger.info("create an index for the networkx nodes and links tables")
        main_db_con.executescript("""
        CREATE INDEX IF NOT EXISTS node_index ON networkx_nodes (node_id, location_id)
        ;
        
        create index if not exists nx_edge_index on
        networkx_edges(from_node_id, to_node_id,
        artificial, mode_source, mode_source_OID,
        miles, route_cost_scaling, capacity)
        ;
        """)

        # --------------------------------

        db_cur = main_db_con.cursor()
        # nested cursor
        db_cur4 = main_db_con.cursor()
        counter = 0
        total_facilities = 0

        for row in db_cur.execute("select count(distinct facility_id) from  facilities;"):
            total_facilities = row[0]

        # create vertices for each non-ignored facility facility
        # facility_type can be "raw_material_producer", "ultimate_destination","processor";
        # get id from facility_type_id table
        # any other facility types are not currently handled

        facility_data = db_cur.execute("""
        select facility_id,
        facility_type,
        facility_name,
        location_id,
        f.facility_type_id,
        schedule_id

        from facilities f, facility_type_id ft
        where ignore_facility = '{}'
        and f.facility_type_id = ft.facility_type_id;
        """.format('false'))
        facility_data = facility_data.fetchall()
        for row_a in facility_data:

            db_cur2 = main_db_con.cursor()
            facility_id = row_a[0]
            facility_type = row_a[1]
            facility_name = row_a[2]
            facility_location_id = row_a[3]
            facility_type_id = row_a[4]
            schedule_id = row_a[5]
            if counter % 10000 == 1:
                logger.info("vertices created for {} facilities of {}".format(counter, total_facilities))
                for row_d in db_cur4.execute("select count(distinct vertex_id) from vertices;"):
                    logger.info('{} vertices created'.format(row_d[0]))
            counter = counter + 1

            if facility_type == "processor":
                # actual processors - will deal with endcaps in edges section

                # create processor vertices for any commodities that do not inherit max transport distance
                proc_data = db_cur2.execute("""select fc.commodity_id,
               ifnull(fc.quantity, 0),
               fc.units,
               ifnull(c.supertype, c.commodity_name),
               fc.io,
               mc.commodity_id,
               c.commodity_name,
                ifnull(s.source_facility_id, 0)
               from facility_commodities fc, commodities c, commodities mc
                left outer join source_commodity_ref s 
                on (fc.commodity_id = s.commodity_id and s.max_transport_distance_flag = 'Y')
               where fc.facility_id = {}
               and fc.commodity_id = c.commodity_id
               and mc.commodity_name = '{}';""".format(facility_id, multi_commodity_name))

                proc_data = proc_data.fetchall()
                # entry for each incoming commodity and its potential sources
                # each outgoing commodity with this processor as their source IF there is a max commod distance
                for row_b in proc_data:

                    commodity_id = row_b[0]
                    
                    # BEGIN MODIFICATION - replaces `quantity = row_b[1]`
                    if time_period == "yearly" :
                        quantity = facility_cap_noEarthquake[int(facility_id)-1][t+1][i]*row_b[1]
                    elif time_period == "weekly":
                        # Following part is modified to include time-varying facility capacity in the aftermath of earthquake
                        temp_day = int(7*j)
                        if temp_day < repair_time_facility[int(facility_id)-1][t+1][i]:
                            quantity = facility_cap[int(facility_id)-1][t+1][i]*row_b[1]*daily_index
                        else:
                            quantity = facility_cap_noEarthquake[int(facility_id)-1][t+1][i]*row_b[1]*daily_index
                    # END MODIFICATION
                    
                    io = row_b[4]
                    id_for_mult_commodities = row_b[5]
                    commodity_name = row_b[6]
                    source_facility_id = row_b[7]
                    new_source_facility_id = facility_id

                    # vertices for generic demand type, or any subtype specified by the destination
                    for day_before, availability in enumerate(schedule_dict[schedule_id]):
                        if io == 'i':
                            main_db_con.execute("""insert or ignore into vertices ( location_id, facility_id, 
                            facility_type_id, facility_name, schedule_day, commodity_id, activity_level, 
                            storage_vertex, source_facility_id, iob) values ({}, {}, {}, '{}', {}, {}, {}, {}, {}, 
                            '{}' );""".format(facility_location_id, facility_id, facility_type_id, facility_name, day_before+1,
                                              id_for_mult_commodities, availability, primary,
                                              new_source_facility_id, 'b'))

                            main_db_con.execute("""insert or ignore into vertices ( location_id, facility_id, 
                            facility_type_id, facility_name, schedule_day, commodity_id, activity_level, 
                            storage_vertex, demand, source_facility_id, iob) values ({}, {}, {}, '{}', {}, {}, {}, 
                            {}, {}, {}, '{}');""".format(facility_location_id, facility_id, facility_type_id,
                                                         facility_name,
                                                         day_before+1, commodity_id, storage_availability, storage, quantity,
                                                         source_facility_id, io))

                        else:
                            if commodity_name != 'total_fuel':
                                main_db_con.execute("""insert or ignore into vertices ( location_id, facility_id, 
                                facility_type_id, facility_name, schedule_day, commodity_id, activity_level, 
                                storage_vertex, supply, source_facility_id, iob) values ({}, {}, {}, '{}', {}, {}, 
                                {}, {}, {}, {}, '{}');""".format(
                                    facility_location_id, facility_id, facility_type_id, facility_name, day_before+1,
                                    commodity_id, storage_availability, storage, quantity, source_facility_id, io))


            elif facility_type == "raw_material_producer":
                rmp_data = db_cur.execute("""select fc.commodity_id, fc.quantity, fc.units,
                ifnull(s.source_facility_id, 0), io
                from facility_commodities fc
                left outer join source_commodity_ref s 
                on (fc.commodity_id = s.commodity_id 
                and s.max_transport_distance_flag = 'Y' 
                and s.source_facility_id = {})
                where fc.facility_id = {};""".format(facility_id, facility_id))

                rmp_data = rmp_data.fetchall()

                for row_b in rmp_data:
                    commodity_id = row_b[0]
                    
                    # BEGIN MODIFICATION - replacing  `quantity = row_b[1]`
                    if time_period == "yearly": 
                        quantity = facility_cap_noEarthquake[int(facility_id)-1][t+1][i]*row_b[1]
                    elif time_period == "weekly":
                        quantity = facility_cap_noEarthquake[int(facility_id)-1][t+1][i]*row_b[1]*daily_index
                    # END MODIFICATION
                    
                    # units = row_b[2]
                    source_facility_id = row_b[3]
                    iob = row_b[4]

                    if commodity_id in total_potential_production:
                        total_potential_production[commodity_id] = total_potential_production[commodity_id] + quantity
                    else:
                        total_potential_production[commodity_id] = quantity

                    for day_before, availability in enumerate(schedule_dict[schedule_id]):
                        main_db_con.execute("""insert or ignore into vertices (
                        location_id, facility_id, facility_type_id, facility_name, schedule_day, commodity_id, 
                        activity_level, storage_vertex, supply,
                            source_facility_id, iob)
                        values ({}, {}, {}, '{}', {}, {}, {}, {}, {},
                        {}, '{}');""".format(facility_location_id, facility_id, facility_type_id, facility_name, day_before+1,
                                             commodity_id, availability, primary, quantity,
                                             source_facility_id, iob))
                        main_db_con.execute("""insert or ignore into vertices (
                        location_id, facility_id, facility_type_id, facility_name, schedule_day, commodity_id, 
                        activity_level, storage_vertex, supply,
                            source_facility_id, iob)
                        values ({}, {}, {}, '{}', {}, {}, {}, {}, {},
                        {}, '{}');""".format(facility_location_id, facility_id, facility_type_id, facility_name, day_before+1,
                                             commodity_id, storage_availability, storage, quantity,
                                             source_facility_id, iob))

            elif facility_type == "storage":  # storage facility
                storage_fac_data = db_cur.execute("""select
                fc.commodity_id,
                fc.quantity,
                fc.units,
                ifnull(s.source_facility_id, 0),
                io
                from facility_commodities fc
                left outer join source_commodity_ref s 
                on (fc.commodity_id = s.commodity_id and s.max_transport_distance_flag = 'Y')
                where fc.facility_id = {} ;""".format(facility_id))

                storage_fac_data = storage_fac_data.fetchall()

                for row_b in storage_fac_data:
                    commodity_id = row_b[0]
                    source_facility_id = row_b[3]  # 0 if not source-tracked
                    iob = row_b[4]

                    for day_before in range(schedule_length):
                        main_db_con.execute("""insert or ignore into vertices (
                       location_id, facility_id, facility_type_id, facility_name, schedule_day, commodity_id, 
                       storage_vertex,
                            source_facility_id, iob)
                       values ({}, {}, {}, '{}', {}, {}, {},
                       {}, '{}');""".format(facility_location_id, facility_id, facility_type_id, facility_name, day_before+1,
                                            commodity_id, storage,
                                            source_facility_id, iob))

            elif facility_type == "ultimate_destination":

                dest_data = db_cur2.execute("""select
                fc.commodity_id,
                ifnull(fc.quantity, 0),
                fc.units,
                fc.commodity_id,
                ifnull(c.supertype, c.commodity_name),
                ifnull(s.source_facility_id, 0),
                io
                from facility_commodities fc, commodities c
                left outer join source_commodity_ref s 
                on (fc.commodity_id = s.commodity_id and s.max_transport_distance_flag = 'Y')
                where fc.facility_id = {}
                and fc.commodity_id = c.commodity_id;""".format(facility_id))

                dest_data = dest_data.fetchall()

                for row_b in dest_data:
                    commodity_id = row_b[0]
                    quantity = row_b[1]
                    commodity_supertype = row_b[4]
                    source_facility_id = row_b[5]
                    iob = row_b[6]
                    zero_source_facility_id = 0  # material merges at primary vertex

                    # vertices for generic demand type, or any subtype specified by the destination
                    for day_before, availability in enumerate(schedule_dict[schedule_id]):
                        main_db_con.execute("""insert or ignore into vertices (
                       location_id, facility_id, facility_type_id, facility_name, schedule_day, commodity_id, 
                       activity_level, storage_vertex, demand, udp,
                             source_facility_id, iob)
                       values ({}, {}, {}, '{}', {},
                        {}, {}, {}, {}, {},
                        {}, '{}');""".format(facility_location_id, facility_id, facility_type_id, facility_name, day_before+1,
                                             commodity_id, availability, primary, quantity,
                                             the_scenario.unMetDemandPenalty,
                                             zero_source_facility_id, iob))
                        main_db_con.execute("""insert or ignore into vertices (
                       location_id, facility_id, facility_type_id, facility_name, schedule_day, commodity_id, 
                       activity_level, storage_vertex, demand,
                            source_facility_id, iob)
                       values ({}, {}, {}, '{}', {}, {}, {}, {}, {},
                       {}, '{}');""".format(facility_location_id, facility_id, facility_type_id, facility_name, day_before+1,
                                            commodity_id, storage_availability, storage, quantity,
                                            source_facility_id, iob))
                    # vertices for other fuel subtypes that match the destination's supertype
                    # if the subtype is in the commodity table, it is produced by some facility in the scenario
                    db_cur3 = main_db_con.cursor()
                    for row_c in db_cur3.execute("""select commodity_id, units from commodities
                    where supertype = '{}';""".format(commodity_supertype)):
                        new_commodity_id = row_c[0]
                        # new_units = row_c[1]
                        for day_before, availability in schedule_dict[schedule_id]:
                            main_db_con.execute("""insert or ignore into vertices ( location_id, facility_id, 
                            facility_type_id, facility_name, schedule_day, commodity_id, activity_level, 
                            storage_vertex, demand, udp, source_facility_id, iob) values ({}, {}, {}, '{}', {}, {}, 
                            {}, {}, {}, {}, {}, '{}');""".format(facility_location_id, facility_id, facility_type_id,
                                                                 facility_name,
                                                                 day_before+1, new_commodity_id, availability, primary,
                                                                 quantity,
                                                                 the_scenario.unMetDemandPenalty,
                                                                 zero_source_facility_id, iob))
                            main_db_con.execute("""insert or ignore into vertices (
                              location_id, facility_id, facility_type_id, facility_name, schedule_day, commodity_id, 
                              activity_level, storage_vertex, demand,
                            source_facility_id, iob)
                              values ({}, {}, {}, '{}', {}, {}, {}, {}, {},
                              {}, '{}');""".format(facility_location_id, facility_id, facility_type_id, facility_name,
                                                   day_before+1, new_commodity_id, storage_availability, storage, quantity,
                                                   source_facility_id, iob))

            else:
                logger.warning(
                    "error, unexpected facility_type: {}, facility_type_id: {}".format(facility_type, facility_type_id))

    for row_d in db_cur4.execute("select count(distinct vertex_id) from vertices;"):
        logger.info('{} vertices created'.format(row_d[0]))

    logger.debug("total possible production in scenario: {}".format(total_potential_production))


# ===============================================================================


def set_edges_volume_capacity(the_scenario, logger):
    logger.info("starting set_edges_volume_capacity")
    with sqlite3.connect(the_scenario.main_db) as main_db_con:
        logger.debug("starting to record volume and capacity for non-pipeline edges")

        main_db_con.execute(
            "update edges set volume = (select ifnull(ne.volume,0) from networkx_edges ne "
            "where ne.edge_id = edges.nx_edge_id ) where simple_mode in ('rail','road','water');")
        main_db_con.execute(
            "update edges set max_edge_capacity = (select ne.capacity from networkx_edges ne "
            "where ne.edge_id = edges.nx_edge_id) where simple_mode in ('rail','road','water');")
        logger.debug("volume and capacity recorded for non-pipeline edges")

        logger.debug("starting to record volume and capacity for pipeline edges")
        ##
        main_db_con.executescript("""update edges set volume =
        (select l.background_flow
         from pipeline_mapping pm,
         (select id_field_name, cn.source_OID as link_id, min(cn.capacity) capac,
        max(cn.volume) background_flow, source
        from capacity_nodes cn
        where cn.id_field_name = 'MASTER_OID'
        and ifnull(cn.capacity,0)>0
        group by link_id) l

        where edges.tariff_id = pm.id
        and pm.id_field_name = 'tariff_ID'
        and pm.mapping_id_field_name = 'MASTER_OID'
        and l.id_field_name = 'MASTER_OID'
        and pm.mapping_id = l.link_id
        and instr(edges.mode, l.source)>0)
         where simple_mode = 'pipeline'
        ;

        update edges set max_edge_capacity =
        (select l.capac
        from pipeline_mapping pm,
        (select id_field_name, cn.source_OID as link_id, min(cn.capacity) capac,
        max(cn.volume) background_flow, source
        from capacity_nodes cn
        where cn.id_field_name = 'MASTER_OID'
        and ifnull(cn.capacity,0)>0
        group by link_id) l

        where edges.tariff_id = pm.id
        and pm.id_field_name = 'tariff_ID'
        and pm.mapping_id_field_name = 'MASTER_OID'
        and l.id_field_name = 'MASTER_OID'
        and pm.mapping_id = l.link_id
        and instr(edges.mode, l.source)>0)
        where simple_mode = 'pipeline'
        ;""")
        logger.debug("volume and capacity recorded for pipeline edges")
        logger.debug("starting to record units and conversion multiplier")
        main_db_con.execute("""update edges
        set capacity_units =
        (case when simple_mode = 'pipeline' then 'kbarrels'
        when simple_mode = 'road' then 'truckload'
        when simple_mode = 'rail' then 'railcar'
        when simple_mode = 'water' then 'barge'
        else 'unexpected mode' end)
        ;""")
        main_db_con.execute("""update edges
        set units_conversion_multiplier =
        (case when simple_mode = 'pipeline' and phase_of_matter = 'liquid' then {}
        when simple_mode = 'road'  and phase_of_matter = 'liquid' then {}
        when simple_mode = 'road'  and phase_of_matter = 'solid' then {}
        when simple_mode = 'rail'  and phase_of_matter = 'liquid' then {}
        when simple_mode = 'rail'  and phase_of_matter = 'solid' then {}
        when simple_mode = 'water'  and phase_of_matter = 'liquid' then {}
        when simple_mode = 'water'  and phase_of_matter = 'solid' then {}
        else 1 end)
        ;""".format(THOUSAND_GALLONS_PER_THOUSAND_BARRELS,
                    the_scenario.truck_load_liquid.magnitude,
                    the_scenario.truck_load_solid.magnitude,
                    the_scenario.railcar_load_liquid.magnitude,
                    the_scenario.railcar_load_solid.magnitude,
                    the_scenario.barge_load_liquid.magnitude,
                    the_scenario.barge_load_solid.magnitude,
                    ))
        logger.debug("units and conversion multiplier recorded for all edges; starting capacity minus volume")
        main_db_con.execute("""update edges
        set capac_minus_volume_zero_floor =
        365*max((select (max_edge_capacity - ifnull(volume,0)) where  max_edge_capacity is not null),0)
        where  max_edge_capacity is not null
        ;""")
        logger.debug("capacity minus volume (minimum set to zero) recorded for all edges")
    return


# ===============================================================================


def create_unmet_demand_vars(the_scenario, logger):
    logger.info("START: create_unmet_demand_vars")
    demand_var_list = []
    # may create vertices with zero demand, but only for commodities that the facility has demand for at some point

    with sqlite3.connect(the_scenario.main_db) as main_db_con:
        db_cur = main_db_con.cursor()
        for row in db_cur.execute("""select v.facility_id, v.schedule_day, 
        ifnull(c.supertype, c.commodity_name) top_level_commodity_name, v.udp
         from vertices v, commodities c, facility_type_id ft, facilities f
         where v.commodity_id = c.commodity_id
         and ft.facility_type = "ultimate_destination"
         and v.storage_vertex = 0
         and v.facility_type_id = ft.facility_type_id
         and v.facility_id = f.facility_id
         and f.ignore_facility = 'false'
         group by v.facility_id, v.schedule_day, ifnull(c.supertype, c.commodity_name)
         ;""".format('')):
            # facility_id, day, and simplified commodity name
            demand_var_list.append((row[0], row[1], row[2], row[3]))
    
    # MODIFICATION = replaces 0 with None
    unmet_demand_var = LpVariable.dicts("UnmetDemand", demand_var_list, None, None)

    return unmet_demand_var


# ===============================================================================

def create_opt_problem(logger, the_scenario, unmet_demand_vars, flow_vars, processor_build_vars):
    logger.debug("START: create_opt_problem")
    prob = LpProblem("Flow assignment", LpMinimize)

    unmet_demand_costs = []
    flow_costs = {}
    processor_build_costs = []
    for u in unmet_demand_vars:
        # facility_id = u[0]
        # schedule_day = u[1]
        # demand_commodity_name = u[2]
        udp = u[3]
        unmet_demand_costs.append(udp * unmet_demand_vars[u])

    with sqlite3.connect(the_scenario.main_db) as main_db_con:
        db_cur = main_db_con.cursor()
        # Flow cost memory improvements: only get needed data; dict instead of list; narrow in lpsum
        flow_cost_var = db_cur.execute("select edge_id, edge_flow_cost from edges e group by edge_id;")
        flow_cost_data = flow_cost_var.fetchall()
        counter = 0
        for row in flow_cost_data:
            edge_id = row[0]
            edge_flow_cost = row[1]
            counter += 1

            # MODIFICATION = adds absolute value to costs None
            # flow costs cover transportation and storage
            flow_costs[edge_id] = abs(edge_flow_cost)
            # flow_costs.append(edge_flow_cost * flow_vars[(edge_id)])

        logger.info("check if candidate tables exist")
        sql = "SELECT name FROM sqlite_master WHERE type='table' " \
              "AND name in ('candidate_processors', 'candidate_process_list');"
        count = len(db_cur.execute(sql).fetchall())
        processor_build_cost_dict = {}

        if count == 2:

            generated_processor_build_cost = db_cur.execute("""
            select f.facility_id, (p.cost_formula*c.quantity) build_cost
            from facilities f, facility_type_id ft, candidate_processors c, candidate_process_list p
            where f.facility_type_id = ft.facility_type_id
            and facility_type = 'processor'
            and candidate = 1
            and ignore_facility = 'false'
            and f.facility_name = c.facility_name
            and c.process_id = p.process_id
            group by f.facility_id, build_cost;""")
            generated_candidate_processor_build_cost_data = generated_processor_build_cost.fetchall()
            for row in generated_candidate_processor_build_cost_data:
                processor_build_cost_dict[row[0]] = row[1]
        
        logger.info("check if candidate processors exist from proc.csv")
        sql = "SELECT count(candidate) from facilities where candidate = 1 and build_cost > 0;"
        input_candidates = db_cur.execute(sql).fetchall()[0][0]
        logger.debug("number of candidate processors from proc.csv = {}".format(input_candidates))

        if input_candidates > 0:
            #force ignore_facility = 'false' for processors input from file; it should always be set to false anyway
            input_processor_build_cost = db_cur.execute("""
            select f.facility_id,  f.build_cost
            from facilities f
                INNER JOIN facility_type_id ft ON f.facility_type_id = ft.facility_type_id
            where candidate = 1 and build_cost>0
            and facility_type = 'processor'
            and ifnull(ignore_facility, 'false') = 'false'
            group by f.facility_id, build_cost
            ;""")
            input_candidate_processor_build_cost_data = input_processor_build_cost.fetchall()
            for row in input_candidate_processor_build_cost_data:
                # This is allowed to overwrite, if somehow a candidate processor is showing up as both generated and from input file
                processor_build_cost_dict[row[0]] = row[1]
        logger.debug("candidate tables present: {}, input processor candidates: {}".format(count, input_candidates))
        if count == 2 or input_candidates > 0:
            for candidate_proc_facility_id, proc_facility_build_cost in iteritems(processor_build_cost_dict):
                processor_build_costs.append(
                    proc_facility_build_cost * processor_build_vars[candidate_proc_facility_id])

    prob += (lpSum(unmet_demand_costs) + lpSum(flow_costs[k] * flow_vars[k] for k in flow_costs) + lpSum(
        processor_build_costs)), "Total Cost of Transport, storage, facility building, and penalties"

    logger.debug("FINISHED: create_opt_problem")
    return prob


# ===============================================================================


def create_constraint_daily_processor_capacity(logger, the_scenario, prob, flow_var, processor_build_vars,
                                               processor_daily_flow_vars, time_period):
    logger.debug("STARTING:  create_constraint_daily_processor_capacity")
    # primary vertices only
    # flow into vertex is capped at facility max_capacity per day
    # sum over all input commodities, grouped by day and facility
    # conservation of flow and ratios are handled in other methods

    ### get primary processor vertex and its input quantityi
    total_scenario_min_capacity = 0

    # BEGIN MODIFICATION - logging
    i = np.load("scenario_num.npy")
    t = np.load("time_horizon.npy")
    logger.info("scenario {}".format(i))
    logger.info("time horizon {}".format(t))
    if time_period == "weekly" :
        j = np.load("earthquake_week.npy")
        logger.info("earthquake week {}".format(j))
    # END MODIFICATION

    with sqlite3.connect(the_scenario.main_db) as main_db_con:
        db_cur = main_db_con.cursor()
        sql = """select f.facility_id,
        ifnull(f.candidate, 0), ifnull(f.max_capacity, -1), v.schedule_day, v.activity_level
        from facility_commodities fc, facility_type_id ft, facilities f, vertices v
        where ft.facility_type = 'processor'
        and ft.facility_type_id = f.facility_type_id
        and f.facility_id = fc.facility_id
        and fc.io = 'i'
        and v.facility_id = f.facility_id
        and v.storage_vertex = 0
        group by f.facility_id, ifnull(f.candidate, 0), f.max_capacity, v.schedule_day, v.activity_level
        ;
        """
        # iterate through processor facilities, one constraint per facility per day
        # no handling of subcommodities

        processor_facilities = db_cur.execute(sql)

        processor_facilities = processor_facilities.fetchall()

        for row_a in processor_facilities:

            # input_commodity_id = row_a[0]
            facility_id = row_a[0]
            is_candidate = row_a[1]
            
            # BEGIN MODIFICATION - max_capacity changed
            if time_period == "yearly" :
                max_capacity = facility_cap_noEarthquake[int(facility_id)-1][t+1][i]*row_a[3]
            else :
                # In order to incorporate time-varying facility capacity into FTOT
                temp_day = int(7*j)
                if temp_day < repair_time_facility[int(facility_id)-1][t+1][i]:
                    max_capacity = facility_cap[int(facility_id)-1][t+1][i]*row_a[3]*daily_index
                else:
                    max_capacity = facility_cap_noEarthquake[int(facility_id)-1][t+1][i]*row_a[3]*daily_index
            # END MODIFICATION
            
            day = row_a[3]
            daily_activity_level = row_a[4]

            if max_capacity >= 0:
                daily_inflow_max_capacity = float(max_capacity) * float(daily_activity_level)
                daily_inflow_min_capacity = daily_inflow_max_capacity / 2
                logger.debug(
                    "processor {}, day {},  input capacity min: {} max: {}".format(facility_id, day, daily_inflow_min_capacity,
                                                                             daily_inflow_max_capacity))
                total_scenario_min_capacity = total_scenario_min_capacity + daily_inflow_min_capacity
                flow_in = []

                # all edges that end in that processor facility primary vertex, on that day
                db_cur2 = main_db_con.cursor()
                for row_b in db_cur2.execute("""select edge_id from edges e, vertices v
                where e.start_day = {}
                and e.d_vertex_id = v.vertex_id
                and v.facility_id = {}
                and v.storage_vertex = 0
                group by edge_id""".format(day, facility_id)):
                    input_edge_id = row_b[0]
                    flow_in.append(flow_var[input_edge_id])

                logger.debug(
                    "flow in for capacity constraint on processor facility {} day {}: {}".format(facility_id, day, flow_in))
                prob += lpSum(flow_in) <= daily_inflow_max_capacity * processor_daily_flow_vars[(facility_id, day)], \
                        "constraint max flow into processor facility {}, day {}, flow var {}".format(
                            facility_id, day, processor_daily_flow_vars[facility_id, day])

                prob += lpSum(flow_in) >= daily_inflow_min_capacity * processor_daily_flow_vars[
                    (facility_id, day)], "constraint min flow into processor {}, day {}".format(facility_id, day)
            # else:
            #     pdb.set_trace()

            if is_candidate == 1:
                # forces processor build var to be correct
                # if there is flow through a candidate processor then it has to be built
                prob += processor_build_vars[facility_id] >= processor_daily_flow_vars[
                    (facility_id, day)], "constraint forces processor build var to be correct {}, {}".format(
                    facility_id, processor_build_vars[facility_id])

    logger.debug("FINISHED:  create_constraint_daily_processor_capacity")
    return prob


# ===============================================================================


def create_primary_processor_vertex_constraints(logger, the_scenario, prob, flow_var):
    logger.debug("STARTING:  create_primary_processor_vertex_constraints - conservation of flow")
    # for all of these vertices, flow in always  == flow out
    # node_counter = 0
    # node_constraint_counter = 0

    # BEGIN MODIFICATION - logging            
    i = np.load("scenario_num.npy")
    t = np.load("time_horizon.npy")
    logger.info("scenario {}".format(i))
    logger.info("time horizon {}".format(t))
    # END MODIFICATION

    with sqlite3.connect(the_scenario.main_db) as main_db_con:
        db_cur = main_db_con.cursor()

        # total flow in == total flow out, subject to conversion;
        # dividing by "required quantity" functionally converts all commodities to the same "processor-specific units"

        # processor primary vertices with input commodity and  quantity needed to produce specified output quantities
        # 2 sets of constraints; one for the primary processor vertex to cover total flow in and out
        # one for each input and output commodity (sum over sources) to ensure its ratio matches facility_commodities

        # the current construction of this method is dependent on having only one input commodity type per processor
        # this limitation makes sharing max transport distance from the input to an output commodity feasible

        logger.debug("conservation of flow and commodity ratios, primary processor vertices:")
        sql = """select v.vertex_id,
        (case when e.o_vertex_id = v.vertex_id then 'out' 
        when e.d_vertex_id = v.vertex_id then 'in' else 'error' end) in_or_out_edge,
        (case when e.o_vertex_id = v.vertex_id then start_day 
        when e.d_vertex_id = v.vertex_id then end_day else 0 end) constraint_day,
        e.commodity_id,
        e.mode,
        e.edge_id,
        nx_edge_id, fc.quantity, v.facility_id, c.commodity_name,
        fc.io,
        v.activity_level,
        ifnull(f.candidate, 0) candidate_check,
        e.source_facility_id,
        v.source_facility_id,
        v.commodity_id,
        c.share_max_transport_distance
        from vertices v, facility_commodities fc, facility_type_id ft, commodities c, facilities f
        join edges e on (v.vertex_id = e.o_vertex_id or v.vertex_id = e.d_vertex_id)
        where ft.facility_type = 'processor'
        and v.facility_id = f.facility_id
        and ft.facility_type_id = v.facility_type_id
        and storage_vertex = 0
        and v.facility_id = fc.facility_id
        and fc.commodity_id = c.commodity_id
        and fc.commodity_id = e.commodity_id
        group by v.vertex_id,
        in_or_out_edge,
        constraint_day,
        e.commodity_id,
        e.mode,
        e.edge_id,
        nx_edge_id, fc.quantity, v.facility_id, c.commodity_name,
        fc.io,
        v.activity_level,
        candidate_check,
        e.source_facility_id,
        v.commodity_id,
        v.source_facility_id,
        ifnull(c.share_max_transport_distance, 'N')
        order by v.facility_id, e.source_facility_id, v.vertex_id, fc.io, e.edge_id
        ;"""

        logger.info("Starting the execute")
        execute_start_time = datetime.datetime.now()
        sql_data = db_cur.execute(sql)
        logger.info("Done with the execute fetch all for :")
        logger.info(
            "execute for processor primary vertices, with their in and out edges - Total Runtime (HMS): \t{} \t ".format(
                get_total_runtime_string(execute_start_time)))

        logger.info("Starting the fetchall")
        fetchall_start_time = datetime.datetime.now()
        sql_data = sql_data.fetchall()
        logger.info(
            "fetchall processor primary vertices, with their in and out edges - Total Runtime (HMS): \t{} \t ".format(
                get_total_runtime_string(fetchall_start_time)))

        # Nested dictionaries
        # flow_in_lists[primary_processor_vertex_id] = dict of commodities handled by that processor vertex

        # flow_in_lists[primary_processor_vertex_id][commodity1] =
        # list of edge ids that flow that commodity into that vertex

        # flow_in_lists[vertex_id].values() to get all flow_in edges for all commodities, a list of lists
        # if edge out commodity inherits transport distance, then source_facility id must match. if not, aggregate

        flow_in_lists = {}
        flow_out_lists = {}
        inherit_max_transport = {}
        # inherit_max_transport[commodity_id] = 'Y' or 'N'

        for row_a in sql_data:

            vertex_id = row_a[0]
            in_or_out_edge = row_a[1]
            # constraint_day = row_a[2]
            commodity_id = row_a[3]
            # mode = row_a[4]
            edge_id = row_a[5]
            # nx_edge_id = row_a[6]
            
            facility_id = row_a[8]
            
            # MODIFICATION - replaces quantity = 
            quantity = facility_cap_noEarthquake[int(facility_id)-1][t+1][i]*float(row_a[7])

            # commodity_name = row_a[9]
            # fc_io_commodity = row_a[10]
            # activity_level = row_a[11]
            # is_candidate = row_a[12]
            edge_source_facility_id = row_a[13]
            vertex_source_facility_id = row_a[14]
            # v_commodity_id = row_a[15]
            inherit_max_transport_distance = row_a[16]
            if commodity_id not in inherit_max_transport.keys():
                if inherit_max_transport_distance == 'Y':
                    inherit_max_transport[commodity_id] = 'Y'
                else:
                    inherit_max_transport[commodity_id] = 'N'

            if in_or_out_edge == 'in':
                # if the vertex isn't in the main dict yet, add it
                # could have multiple source facilities
                # could also have more than one input commodity now
                flow_in_lists.setdefault(vertex_id, {})
                flow_in_lists[vertex_id].setdefault((commodity_id, quantity, edge_source_facility_id), []).append(flow_var[edge_id])
                # flow_in_lists[vertex_id] is itself a dict keyed on commodity, quantity (ratio) and edge_source_facility;
                # value is a list of edge ids into that vertex of that commodity and edge source

            elif in_or_out_edge == 'out':
                # for out-lists, could have multiple commodities as well as multiple sources
                # some may have a max transport distance, inherited or independent, some may not
                flow_out_lists.setdefault(vertex_id, {})  # if the vertex isn't in the main dict yet, add it
                flow_out_lists[vertex_id].setdefault((commodity_id, quantity, edge_source_facility_id), []).append(flow_var[edge_id])

            # Because we keyed on commodity, source facility tracking is merged as we pass through the processor vertex

            # 1) for each output commodity, check against an input to ensure correct ratio - only need one input
            # 2) for each input commodity, check against an output to ensure correct ratio - only need one output;
            # 2a) first sum sub-flows over input commodity

        # 1----------------------------------------------------------------------
        constrained_input_flow_vars = set([])
        # pdb.set_trace()

        for key, value in iteritems(flow_out_lists):
            #value is a dictionary with commodity & source as keys
            # set up a dictionary that will be filled with input lists to check ratio against
            compare_input_dict = {}
            compare_input_dict_commod = {}
            vertex_id = key
            zero_in = False
            #value is a dictionary keyed on output commodity, quantity required, edge source
            if vertex_id in flow_in_lists:
                in_quantity = 0
                in_commodity_id = 0
                in_source_facility_id = -1
                for ikey, ivalue in iteritems(flow_in_lists[vertex_id]):
                    in_commodity_id = ikey[0]
                    in_quantity = ikey[1]
                    in_source = ikey[2]
                    # list of edges
                    compare_input_dict[in_source] = ivalue
                    # to accommodate and track multiple input commodities; does not keep sources separate
                    # aggregate lists over sources, by commodity
                    if in_commodity_id not in compare_input_dict_commod.keys():
                        compare_input_dict_commod[in_commodity_id] = set([])
                    for edge in ivalue:
                        compare_input_dict_commod[in_commodity_id].add(edge)
            else:
                zero_in = True


            # value is a dict - we loop once here for each output commodity and source at the vertex
            for key2, value2 in iteritems(value):
                out_commodity_id = key2[0]
                out_quantity = key2[1]
                out_source = key2[2]
                # edge_list = value2
                flow_var_list = value2
                # if we need to match source facility, there is only one set of input lists
                # otherwise, use all input lists - this aggregates sources
                # need to keep commodities separate, units may be different
                # known issue -  we could have double-counting problems if only some outputs have to inherit max
                # transport distance through this facility
                match_source = inherit_max_transport[out_commodity_id]
                compare_input_list = []
                if match_source == 'Y':
                    if len(list(compare_input_dict_commod.keys())) > 1:
                        error = "Multiple input commodities for processors and shared max transport distance are" \
                                " not supported within the same scenario."
                        logger.error(error)
                        raise Exception(error)

                    if out_source in compare_input_dict.keys():
                        compare_input_list = compare_input_dict[out_source]
                # if no valid input edges - none for vertex, or if output needs to match source and there are no
                # matching source
                if zero_in or (match_source == 'Y' and len(compare_input_list) == 0):
                    prob += lpSum(
                        flow_var_list) == 0, "processor flow, vertex {} has zero in so zero out of commodity {} " \
                                             "with source {} if applicable".format(
                        vertex_id, out_commodity_id, out_source)
                else:
                    if match_source == 'Y':
                        # ratio constraint for this output commodity relative to total input of each commodity
                        required_flow_out = lpSum(flow_var_list) / out_quantity
                        # check against an input dict
                        prob += required_flow_out == lpSum(
                            compare_input_list) / in_quantity, "processor flow, vertex {}, source_facility {}," \
                                                               " commodity {} output quantity" \
                                                               " checked against single input commodity quantity".format(
                            vertex_id, out_source, out_commodity_id, in_commodity_id)
                        for flow_var in compare_input_list:
                            constrained_input_flow_vars.add(flow_var)
                    else:
                        for k, v in iteritems(compare_input_dict_commod):
                            # pdb.set_trace()
                            # as long as the input source doesn't match an output that needs to inherit
                            compare_input_list = list(v)
                            in_commodity_id = k
                            # ratio constraint for this output commodity relative to total input of each commodity
                            required_flow_out = lpSum(flow_var_list) / out_quantity
                            # check against an input dict
                            prob += required_flow_out == lpSum(
                                compare_input_list) / in_quantity, "processor flow, vertex {}, source_facility {}," \
                                                                   " commodity {} output quantity" \
                                                                   " checked against commodity {} input quantity".format(
                                vertex_id, out_source, out_commodity_id, in_commodity_id)
                            for flow_var in compare_input_list:
                                constrained_input_flow_vars.add(flow_var)

        for key, value in iteritems(flow_in_lists):
            vertex_id = key
            for key2, value2 in iteritems(value):
                commodity_id = key2[0]
                # out_quantity = key2[1]
                source = key2[2]
                # edge_list = value2
                flow_var_list = value2
                for flow_var in flow_var_list:
                    if flow_var not in constrained_input_flow_vars:
                        prob += flow_var == 0, "processor flow, vertex {} has no matching out edges so zero in of " \
                                               "commodity {} with source {}".format(
                            vertex_id, commodity_id, source)

    logger.debug("FINISHED:  create_primary_processor_conservation_of_flow_constraints")
    return prob


# ===============================================================================

def create_constraint_max_route_capacity(logger, the_scenario, prob, flow_var):
    logger.info("STARTING:  create_constraint_max_route_capacity")
    logger.info("modes with background flow turned on: {}".format(the_scenario.backgroundFlowModes))
    # min_capacity_level must be a number from 0 to 1, inclusive
    # min_capacity_level is only relevant when background flows are turned on
    # it sets a floor to how much capacity can be reduced by volume.
    # min_capacity_level = .25 means route capacity will never be less than 25% of full capacity,
    # even if "volume" would otherwise restrict it further
    # min_capacity_level = 0 allows a route to be made unavailable for FTOT flow if base volume is too high
    # this currently applies to all modes

    # BEGIN MODIFICATION - logging
    i = np.load("scenario_num.npy")
    t = np.load("time_horizon.npy")
    j = np.load("earthquake_week.npy")
    logger.info("scenario {}".format(i))
    logger.info("time horizon {}".format(t))
    logger.info("earthquake week {}".format(j))
    # END MODIFICATION
    
    logger.info("minimum available capacity floor set at: {}".format(the_scenario.minCapacityLevel))

    with sqlite3.connect(the_scenario.main_db) as main_db_con:
        db_cur = main_db_con.cursor()
        # capacity for storage routes
        sql = """select
                rr.route_id, sr.storage_max, sr.route_name, e.edge_id, e.start_day
                from route_reference rr
                join storage_routes sr on sr.route_name = rr.route_name
                join edges e on rr.route_id = e.route_id
                ;"""
        # get the data from sql and see how long it takes.

        logger.info("Starting the execute")
        execute_start_time = datetime.datetime.now()
        storage_edge_data = db_cur.execute(sql)
        logger.info("Done with the execute fetch all for storage edges:")
        logger.info("execute for edges for storage - Total Runtime (HMS): \t{} \t ".format(
            get_total_runtime_string(execute_start_time)))

        logger.info("Starting the fetchall")
        fetchall_start_time = datetime.datetime.now()
        storage_edge_data = storage_edge_data.fetchall()
        logger.info("fetchall edges for storage - Total Runtime (HMS): \t{} \t ".format(
            get_total_runtime_string(fetchall_start_time)))

        flow_lists = {}

        for row_a in storage_edge_data:
            route_id = row_a[0]
            aggregate_storage_capac = row_a[1]
            storage_route_name = row_a[2]
            edge_id = row_a[3]
            start_day = row_a[4]

            flow_lists.setdefault((route_id, aggregate_storage_capac, storage_route_name, start_day), []).append(
                flow_var[edge_id])

        for key, flow in iteritems(flow_lists):
            prob += lpSum(flow) <= key[1], "constraint max flow on storage route {} named {} for day {}".format(key[0],
                                                                                                                key[2],
                                                                                                                key[3])

        logger.debug("route_capacity constraints created for all storage routes")

        # capacity for transport routes
        # Assumption - all flowing material is in kgal, all flow is summed on a single non-pipeline nx edge
        sql = """select e.edge_id, e.nx_edge_id, e.max_edge_capacity, e.start_day, e.simple_mode, e.phase_of_matter,
         e.capac_minus_volume_zero_floor
        from edges e
        where e.max_edge_capacity is not null
        and e.simple_mode != 'pipeline'
        ;"""
        # get the data from sql and see how long it takes.

        logger.info("Starting the execute")
        execute_start_time = datetime.datetime.now()
        route_capac_data = db_cur.execute(sql)
        logger.info("Done with the execute fetch all for transport edges:")
        logger.info("execute for non-pipeline edges for transport edge capacity - Total Runtime (HMS): \t{} \t ".format(
            get_total_runtime_string(execute_start_time)))

        logger.info("Starting the fetchall")
        fetchall_start_time = datetime.datetime.now()
        route_capac_data = route_capac_data.fetchall()
        logger.info("fetchall non-pipeline  edges for transport edge capacity - Total Runtime (HMS): \t{} \t ".format(
            get_total_runtime_string(fetchall_start_time)))

        flow_lists = {}

        for row_a in route_capac_data:
            edge_id = row_a[0]
            nx_edge_id = row_a[1]
            nx_edge_capacity = row_a[2]
            start_day = row_a[3]
            simple_mode = row_a[4]
            phase_of_matter = row_a[5]
            capac_minus_background_flow = max(row_a[6], 0)
            min_restricted_capacity = max(capac_minus_background_flow, nx_edge_capacity * the_scenario.minCapacityLevel)

            if simple_mode in the_scenario.backgroundFlowModes:
                use_capacity = min_restricted_capacity
            else:
                use_capacity = nx_edge_capacity

            # flow is in thousand gallons (kgal), for liquid, or metric tons, for solid
            # capacity is in truckload, rail car, barge, or pipeline movement per day
            # if mode is road and phase is liquid, capacity is in truckloads per day, we want it in kgal
            # ftot_supporting_gis tells us that there are 8 kgal per truckload,
            # so capacity * 8 gives us correct units or kgal per day
            # => use capacity * ftot_supporting_gis multiplier to get capacity in correct flow units

            multiplier = 1  # if units match, otherwise specified here
            if simple_mode == 'road':
                if phase_of_matter == 'liquid':
                    multiplier = the_scenario.truck_load_liquid.magnitude
                elif phase_of_matter == 'solid':
                    multiplier = the_scenario.truck_load_solid.magnitude
            elif simple_mode == 'water':
                if phase_of_matter == 'liquid':
                    multiplier = the_scenario.barge_load_liquid.magnitude
                elif phase_of_matter == 'solid':
                    multiplier = the_scenario.barge_load_solid.magnitude
            elif simple_mode == 'rail':
                if phase_of_matter == 'liquid':
                    multiplier = the_scenario.railcar_load_liquid.magnitude
                elif phase_of_matter == 'solid':
                    multiplier = the_scenario.railcar_load_solid.magnitude

            # BEGIN MODIFICATION - modified to include time-varying edge capacity in FTOT for weekly scenarios
            temp_day = int(7*j)
            if temp_day < repair_time_edge[float(edge_id)-1][t+1][i]:
                capacity_reduction_index = edge_cap[float(edge_id)-1][t+1][i]
            else:
                capacity_reduction_index = 1
            #logger.info("capacity_reduction_index {}".format(capacity_reduction_index))
            converted_capacity = use_capacity * multiplier * capacity_reduction_index

            #converted_capacity = use_capacity * multiplier
            # END MODIFICATION

            flow_lists.setdefault((nx_edge_id, converted_capacity, start_day), []).append(flow_var[edge_id])

        for key, flow in iteritems(flow_lists):
            prob += lpSum(flow) <= key[1], "constraint max flow on nx edge {} for day {}".format(key[0], key[2])

        logger.debug("route_capacity constraints created for all non-pipeline  transport routes")

    logger.debug("FINISHED:  create_constraint_max_route_capacity")
    return prob


# ===============================================================================

def save_pulp_solution(the_scenario, prob, logger,  time_period, zero_threshold):
    # BEGIN MODIFICATION - logging
    i = np.load("scenario_num.npy")
    t = np.load("time_horizon.npy")
    logger.info("scenario {}".format(i))
    logger.info("time horizon {}".format(t))
    if time_period == "weekly" :
        j = np.load("earthquake_week.npy")
        logger.info("earthquake week {}".format(j))
    # END MODIFICATION
    
    import datetime
    start_time = datetime.datetime.now()
    logger.info("START: save_pulp_solution")
    non_zero_variable_count = 0

    with sqlite3.connect(the_scenario.main_db) as db_con:

        db_cur = db_con.cursor()
        # drop  the optimal_solution table
        # -----------------------------
        db_cur.executescript("drop table if exists optimal_solution;")

        # create the optimal_solution table
        # -----------------------------
        db_cur.executescript("""
                                create table optimal_solution
                                (
                                    variable_name string,
                                    variable_value real
                                );
                                """)

        # insert the optimal data into the DB
        # -------------------------------------
        for v in prob.variables():
            if v.varValue is None:
                logger.debug("Variable value is none: " + str(v.name))
            else:
                if v.varValue > zero_threshold:  # eliminates values too close to zero
                    sql = """insert into optimal_solution  (variable_name, variable_value) values ("{}", {});""".format(
                        v.name, float(v.varValue))
                    db_con.execute(sql)
                    non_zero_variable_count = non_zero_variable_count + 1

        # query the optimal_solution table in the DB for each variable we care about
        # ----------------------------------------------------------------------------
        sql = "select count(variable_name) from optimal_solution where variable_name like 'BuildProcessor%';"
        data = db_con.execute(sql)
        optimal_processors_count = data.fetchone()[0]
        logger.info("number of optimal_processors: {}".format(optimal_processors_count))

        sql = "select count(variable_name) from optimal_solution where variable_name like 'UnmetDemand%';"
        data = db_con.execute(sql)
        optimal_unmet_demand_count = data.fetchone()[0]

        # BEGIN MODIFICATION - save unmet demand
        if time_period == "yearly":
            unmet_demand_yearly = optimal_unmet_demand_sum
            np.save("unmet_demand_yearly.npy", unmet_demand_yearly)

            UnmetDemandAmount = np.load("UnmetDemandAmount.npy")
            for j in range (len(UnmetDemandAmount)):
                UnmetDemandAmount[j][t][i] = optimal_unmet_demand_sum*daily_index
            np.save("UnmetDemandAmount.npy",UnmetDemandAmount)
        
        else: #weekly
            unmet_demand_daily = optimal_unmet_demand_sum
            np.save("unmet_demand_daily.npy", unmet_demand_daily)
            logger.info("Repair Cost : {}".format(repair_costs[int(j*7)][t][i]))
        # END MODIFICATION  

        logger.info("number facilities with optimal_unmet_demand : {}".format(optimal_unmet_demand_count))
        sql = "select ifnull(sum(variable_value),0) from optimal_solution where variable_name like 'UnmetDemand%';"
        data = db_con.execute(sql)
        optimal_unmet_demand_sum = data.fetchone()[0]
        logger.info("Total Unmet Demand : {}".format(optimal_unmet_demand_sum))

        # MODIFICATION - add catalyst replacement
        logger.info("Catalyst Replacement : {}".format(sum(CatalystReplace_cost[:,t+1,i])))

        logger.info("Penalty per unit of Unmet Demand : ${0:,.0f}".format(the_scenario.unMetDemandPenalty))
        logger.info("Total Cost of Unmet Demand : \t ${0:,.0f}".format(
            optimal_unmet_demand_sum * the_scenario.unMetDemandPenalty))

        # BEGIN MODFIICATION 
        if optimal_unmet_demand_sum < 0:
            costs_daily = abs(float(value(prob.objective))- optimal_unmet_demand_sum * the_scenario.unMetDemandPenalty) + sum(CatalystReplace_cost[:,t+1,i])*daily_index + operation_cost*((1.03)**(t+13))*daily_index + repair_costs[int(j*7)][t][i]

            logger.result(
                "Total Scenario Cost = (transportation + processor construction + operation + catalyst replacement): \t ${0:,.0f}"
                "".format(costs_daily))
        else:
            costs_daily = abs(float(value(prob.objective))-optimal_unmet_demand_sum * the_scenario.unMetDemandPenalty)+sum(CatalystReplace_cost[:,t+1,i])*daily_index +operation_cost*((1.03)**(t+13))*daily_index + repair_costs[int(j*7)][t][i] + optimal_unmet_demand_sum*the_scenario.unMetDemandPenalty
            logger.result(
                "Total Scenario Cost = (transportation + unmet demand penalty + processor construction + operation+ catalyst replacement): \t ${0:,.0f}"
                "".format(costs_daily))
            
        np.save("costs_daily.npy", costs_daily)
        logger.info("costs_daily: {}".format(costs_daily))

        if optimal_unmet_demand_sum < 0:
            costs_yearly = abs(float(value(prob.objective))- optimal_unmet_demand_sum * the_scenario.unMetDemandPenalty) + sum(CatalystReplace_cost[:,t+1,i]) + operation_cost*((1.03)**(t+13))

            logger.result(
                "Total Scenario Cost = (transportation + processor construction + operation + catalyst replacement): \t ${0:,.0f}"
                "".format(costs_yearly))
        else:
            costs_yearly = abs(float(value(prob.objective))-optimal_unmet_demand_sum * the_scenario.unMetDemandPenalty)+sum(CatalystReplace_cost[:,t+1,i])+operation_cost*((1.03)**(t+13))+optimal_unmet_demand_sum*the_scenario.unMetDemandPenalty
            logger.result(
                "Total Scenario Cost = (transportation + unmet demand penalty + processor construction + operation+ catalyst replacement): \t ${0:,.0f}"
                "".format(costs_yearly))
            
        np.save("costs_yearly.npy", costs_yearly)        
        logger.info("costs_yearly: {}".format(costs_yearly))
        # END MODIFICATION

        sql = "select count(variable_name) from optimal_solution where variable_name like 'Edge%';"
        data = db_con.execute(sql)
        optimal_edges_count = data.fetchone()[0]
        logger.info("number of optimal edges: {}".format(optimal_edges_count))

    # logger.info("Total Cost of building and transporting : \t ${0:,.0f}".format(
    #    float(value(prob.objective)) - optimal_unmet_demand_sum * the_scenario.unMetDemandPenalty))
    logger.info(
        "Total Scenario Cost = (transportation + unmet demand penalty + "
        "processor construction): \t ${0:,.0f}".format(
            float(value(prob.objective))))

    logger.info(
        "FINISH: save_pulp_solution: Runtime (HMS): \t{}".format(ftot_supporting.get_total_runtime_string(start_time)))

def save_pulp_solution(the_scenario, prob, logger, time_period, zero_threshold=0.00001):

    # BEGIN MODIFICATION - logging
    i = np.load("scenario_num.npy")
    t = np.load("time_horizon.npy")
    logger.info("scenario {}".format(i))
    logger.info("time horizon {}".format(t))
    if time_period == "weekly" :
        j = np.load("earthquake_week.npy")
        logger.info("earthquake week {}".format(j))
    # END MODIFICATION


    import datetime
    start_time = datetime.datetime.now()
    logger.info("START: save_pulp_solution")
    non_zero_variable_count = 0

    with sqlite3.connect(the_scenario.main_db) as db_con:

        db_cur = db_con.cursor()
        # drop  the optimal_solution table
        # -----------------------------
        db_cur.executescript("drop table if exists optimal_solution;")

        # create the optimal_solution table
        # -----------------------------
        db_cur.executescript("""
                                create table optimal_solution
                                (
                                    variable_name string,
                                    variable_value real
                                );
                                """)

        # insert the optimal data into the DB
        # -------------------------------------
        for v in prob.variables():
            if v.varValue > zero_threshold:  # eliminates values too close to zero
                sql = """insert into optimal_solution  (variable_name, variable_value) values ("{}", {});""".format(
                    v.name, float(v.varValue))
                db_con.execute(sql)
                non_zero_variable_count = non_zero_variable_count + 1

        # query the optimal_solution table in the DB for each variable we care about
        # ----------------------------------------------------------------------------
        sql = "select count(variable_name) from optimal_solution where variable_name like 'BuildProcessor%';"
        data = db_con.execute(sql)
        optimal_processors_count = data.fetchone()[0]
        logger.info("number of optimal_processors: {}".format(optimal_processors_count))

        sql = "select count(variable_name) from optimal_solution where variable_name like 'UnmetDemand%';"
        data = db_con.execute(sql)
        optimal_unmet_demand_count = data.fetchone()[0]
        logger.info("number facilities with optimal_unmet_demand : {}".format(optimal_unmet_demand_count))
        sql = "select ifnull(sum(variable_value),0) from optimal_solution where variable_name like 'UnmetDemand%';"
        data = db_con.execute(sql)
        optimal_unmet_demand_sum = data.fetchone()[0]
        
        # BEGIN MODIFICATION - save unmet demand
        if time_period == "yearly":
            unmet_demand_yearly = optimal_unmet_demand_sum
            np.save("unmet_demand_yearly.npy", unmet_demand_yearly)

            UnmetDemandAmount = np.load("UnmetDemandAmount.npy")
            for j in range (len(UnmetDemandAmount)):
                UnmetDemandAmount[j][t][i] = optimal_unmet_demand_sum*daily_index
            np.save("UnmetDemandAmount.npy",UnmetDemandAmount)
        
        else: #weekly
            unmet_demand_daily = optimal_unmet_demand_sum
            np.save("unmet_demand_daily.npy", unmet_demand_daily)
            logger.info("Repair Cost : {}".format(repair_costs[int(j*7)][t][i]))
        # END MODIFICATION        
            
        logger.info("Total Unmet Demand : {}".format(optimal_unmet_demand_sum))
        logger.info("Catalyst Replacement : {}".format(sum(CatalystReplace_cost[:,t+1,i]))) #MODIFICATION
        logger.info("Penalty per unit of Unmet Demand : ${0:,.0f}".format(the_scenario.unMetDemandPenalty))
        logger.info("Total Cost of Unmet Demand : \t ${0:,.0f}".format(
            optimal_unmet_demand_sum * the_scenario.unMetDemandPenalty))
        logger.info("Total Cost of building and transporting : \t ${0:,.0f}".format(abs(float(value(prob.objective))- optimal_unmet_demand_sum * the_scenario.unMetDemandPenalty)))

        # BEGIN MODIFICATION
        #logger.info("Total Cost of building and transporting and operation : \t ${0:,.0f}".format(
            #float(value(prob.objective)) - optimal_unmet_demand_sum * the_scenario.unMetDemandPenalty +operation_cost*((1.03)**(t+13))))
        #=================================non consider the UDP when UD < 0======================================
        if time_period == "weekly":
            if optimal_unmet_demand_sum < 0:
                costs_daily = abs(float(value(prob.objective))- optimal_unmet_demand_sum * the_scenario.unMetDemandPenalty) + sum(CatalystReplace_cost[:,t+1,i])*daily_index + operation_cost*((1.03)**(t+13))*daily_index + repair_costs[int(j*7)][t][i]

                logger.result(
                    "Total Scenario Cost = (transportation + processor construction + operation + catalyst replacement): \t ${0:,.0f}"
                    "".format(costs_daily))
            else:
                costs_daily = abs(float(value(prob.objective))-optimal_unmet_demand_sum * the_scenario.unMetDemandPenalty)+sum(CatalystReplace_cost[:,t+1,i])*daily_index +operation_cost*((1.03)**(t+13))*daily_index + repair_costs[int(j*7)][t][i] + optimal_unmet_demand_sum*the_scenario.unMetDemandPenalty
                logger.result(
                    "Total Scenario Cost = (transportation + unmet demand penalty + processor construction + operation+ catalyst replacement): \t ${0:,.0f}"
                    "".format(costs_daily))
                
            np.save("costs_daily.npy", costs_daily)
            logger.info("costs_daily: {}".format(costs_daily))

        else :
            if optimal_unmet_demand_sum < 0:
                costs_yearly = abs(float(value(prob.objective))- optimal_unmet_demand_sum * the_scenario.unMetDemandPenalty) + sum(CatalystReplace_cost[:,t+1,i]) + operation_cost*((1.03)**(t+13))

                logger.result(
                    "Total Scenario Cost = (transportation + processor construction + operation + catalyst replacement): \t ${0:,.0f}"
                    "".format(costs_yearly))
            else:
                costs_yearly = abs(float(value(prob.objective))-optimal_unmet_demand_sum * the_scenario.unMetDemandPenalty)+sum(CatalystReplace_cost[:,t+1,i])+operation_cost*((1.03)**(t+13))+optimal_unmet_demand_sum*the_scenario.unMetDemandPenalty
                logger.result(
                    "Total Scenario Cost = (transportation + unmet demand penalty + processor construction + operation+ catalyst replacement): \t ${0:,.0f}"
                    "".format(costs_yearly))
                
            np.save("costs_yearly.npy", costs_yearly)        
            logger.info("costs_yearly: {}".format(costs_yearly))

        # END MODIFICATION 

        sql = "select count(variable_name) from optimal_solution where variable_name like 'Edge%';"
        data = db_con.execute(sql)
        optimal_edges_count = data.fetchone()[0]
        logger.info("number of optimal edges: {}".format(optimal_edges_count))


    logger.info(
        "Total Scenario Cost = (transportation + unmet demand penalty + "
        "processor construction): \t ${0:,.0f}".format(
            float(value(prob.objective))))

    logger.info(
        "FINISH: save_pulp_solution: Runtime (HMS): \t{}".format(ftot_supporting.get_total_runtime_string(start_time)))

# ===============================================================================
