# FTOT-SCR 

Freight and Fuel Transportation Optimization Tool - Supply Chain Resilience 

## Description
FTOT is a flexible scenario-testing tool that optimizes the transportation of materials for future energy and freight scenarios.  FTOT models and tracks commodity-specific information and can take into account conversion  of raw materials to products (e.g., crude oil to jet fuel and diesel) and the fulfillment of downstream demand. FTOT was developed at the US Dept. of Transportation's Volpe National Transportation Systems Center.

FTOT-SCR is a modification of the base FTOT program to support analysis of supply chain resilience. The supply chain resilience assessment includes two parts: integrated risk assessment to capture the combined effects of multiple risk factors on supply chain performance, and resilience assessment to calculate the long-term supply chain resilience in a planning horizon. The supply chain methodology and modifications to the FTOT code were developed at Washington State University (WSU) and utilize the 2022.2 version of FTOT.  

Additional documentation developed by the WSU team explains the methodology of the risk assessment and resilience assessment. These files are available in the [docs](/docs/) directory.

## Installation 
FTOT-SCR code uses the Python environment created by the main FTOT-Public repository. If you haven't already installed FTOT, follow [instructions](https://github.com/VolpeUSDOT/FTOT-Public/wiki/FTOT-Installation-Guide) from the main FTOT-Public repository to install FTOT, install supporting Python packages, and set up the Python environment. 

To install the FTOT-SCR code, clone this repository or download and unzip the code to a directory `C:\FTOT-SCR`. This is the same process as used to [download the FTOT code](https://github.com/VolpeUSDOT/FTOT-Public/wiki/FTOT-Installation-Guide#download-ftot-repository) with the different target directory.

After downloading the FTOT-SCR code, navigate to the `\scenarios\ForestResiduals_SCR\input_GISdata` directory and un-zip the `facilities.gdb.zip` ZIP File there to the same directory (using the "Extract Here" option), so that the directory contains a folder called `facilities.gdb`. 

_If you encounter an issue extracting the facilities ZIP file, try downloading the file again directly from GitHub [here](/scenarios/ForestResiduals_SCR/input_GISdata/facilities.gdb.zip) and extracting to the same `input_GISdata` folder._

## Running the Scenario
The `scenarios\ForestResiduals_SCR` directory contains two batch files: setup_v5_1.bat and run_v5_1.bat . To get started, first run the `setup_v5_1.bat` file. This will initiate several Python scripts that will take the inputs described below to create several scenarios. Note that the setup script will take several hours or days to run.

After finishing the set up scripts, run the batch file called `run_v5_1.bat` in the `scenarios\ForestResiduals-SCR` directory. This will begin a lengthy FTOT run consisting of a single run through FTOT's S, C, F, and G steps, followed the OSCR step, which executes many runs of the O1 and O2 steps, as determined by the number of scenarios, years, and earthquake events in the input files. These runs may take many days, or even weeks, depending on the scale of the analysis. 
* If desired, a user can reduce the number of scenarios and years in each scenario by modifying the `N` and `plan_horizon` variables in the `ftot_scr.py` file in the `/program` folder. The default value is 30 scenarios, each 20 years long. 

### Set-up Scripts
FTOT-SCR’s `setup_v5_1.bat` file runs a sequence of six set up scripts. The inputs and outputs for each script are included in the table below. The output files of each script either serve as an input for a later script or are inputs necessary to run an FTOT-SCR scenario.  

File | Inputs | Outputs
--- | --- | ---
`1_SeismicEvents.py` | faultdata.xlsx <br> point.txt | seismic_catalog.npy
`2_Scenario_Generation.py` | FaultData.xlsx <br> point.txt <br> seismic_catalog.npy |  earthquake_events.npy <br> scenario_GFT.npy <br> scenario_forest.npy <br> scenario_earthquake.npy
`3_FacilityCapacity.py` | rmp.csv <br> proc.csv <br> dest.csv <br> rmp_Xycoordinate.txt <br> proc_Xycoordinate.txt <br> dstXYcoordinate.txt <br> Earthquake files | facility_cap.npy <br> facility_cap_noEarthquake.npy <br> facility_DS.npy <br> CatalystReplace_cost.npy
`4_BridgeDamage.py` | seismic_catalog.npy <br>  earthquake_events.npy <br> HighwayBridge_3state.txt <br>  MiddlePoint_Road.txt <br> bridge_location.npy <br> Earthquake files | BDI.npy <br> bridge_DS.npy
`5_EdgeCapacity.py` | HighwayBridge_3state.txt <br> Relationship_BridgeRoad_3_state.txt <br>  MiddlePoint_Road.txt <br> earthquake_events.npy  <br> BDI.npy <br> bridge_ds.npy | edge_cap.npy
`6_RepairTimeCost.py` | Relationship_BridgeRoad_3state.txt <br> seismic_catalog.npy <br> earthquake_events.npy <br> BDI.npy <br> bridge_DS.npy <br> edge_cap.npy <br> facility_cap.npy <br> facility_DS.npy | repair_costs.npy <br> repair_time_edge.npy <br> repair_time_facility.npy <br> total_repair_time.npy

### Interpreting Results
As each scenario finishes, several summary statistics will be printed in the command line and logged. After a full run of the FTOT-SCR tool, the resilience results from the full suite of scenarios can be viewed through the Numpy files:
* `Resilience.npy` for the overall resilience metric. 
* `R1.npy` and `weight1.npy` for the value and weight of hazard-induced losses, 
* `R2.npy` and `weight2.npy` for the value and weight of non-hazard-induced losses, 
* `R3.npy` and `weight3.npy` for the value and weight of opportunity-induced gains.

## Contributing 
* Add bugs and feature requests to the Issues tab for the Volpe Development Team to triage.

## Credits 
Supply Chain Resilience Scenario and FTOT Modifications
* Dr. Ji Yun Lee (WSU)
* Jie Zhao (WSU)

FTOT
* Dr. Kristin Lewis (Volpe) <Kristin.Lewis@dot.gov>
* Matthew Pearlson (Volpe) <Matthew.Pearlson@dot.gov> 
* Gary Baker (Volpe) 
* Olivia Gillham (Volpe) 
* Michelle Gilmore (Volpe) 
* Alexander Oberg (Volpe) 
* Dr. Scott B. Smith (Volpe) 
* Amy Vogel (Volpe)
* Amro El-Adle (Volpe)
* Kirby Ledvina (Volpe)
* Mark Mockett (Volpe)

## Project Sponsors
The development of FTOT that contributed to this public version was funded by the U.S. Federal Aviation Administration (FAA) Office of Environment and Energy and the Department of Defense (DOD) Office of Naval Research through Interagency Agreements (IAA) FA4SCJ and FB48CS under the supervision of FAA’s Nathan Brown and by the U.S. Department of Energy (DOE) Office of Policy under IAA VXS3A2 under the supervision of Zachary Clement. Any opinions, findings, conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the FAA nor of DOE.

## Acknowledgements
The FTOT team thanks our Beta testers and collaborators for valuable input during the FTOT Public Release beta testing, including Dane Camenzind, Kristin Brandt, and Mike Wolcott (Washington State University), Mik Dale (Clemson University), Emily Newes and Ling Tao (National Renewable Energy Laboratory), Seckin Ozkul, Robert Hooker, and George Philippides (Univ. of South Florida), and Chris Ringo (Oregon State University).

## License 
This project is licensed under the terms of the FTOT End User License Agreement. Please read it carefully.
