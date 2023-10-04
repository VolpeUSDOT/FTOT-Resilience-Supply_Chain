@ECHO OFF
cls
set PYTHONDONTWRITEBYTECODE=1 
REM   default is #ECHO OFF, cls (clear screen), and disable .pyc files 
REM   for debugging REM @ECHO OFF line above to see commands 
REM -------------------------------------------------     
 
REM ==============================================
REM =========== ENVIRONMENT VARIABLES ============
REM ==============================================
set PYTHON="C:\FTOT\python3_env\python.exe"
set FTOT="c:\FTOT-SCR\program\ftot.py"
set SETUP_SEISMIC="C:\FTOT-SCR\scenarios\ForestResiduals_SCR\1_SeismicEvents.py"
set SETUP_SCENARIO="C:\FTOT-SCR\scenarios\ForestResiduals_SCR\2_ScenarioGeneration.py"
set SETUP_FACILITY="C:\FTOT-SCR\scenarios\ForestResiduals_SCR\3_FacilityCapacity.py"
set SETUP_BRIDGE="C:\FTOT-SCR\scenarios\ForestResiduals_SCR\4_BridgeDamage.py"
set SETUP_EDGE="C:\FTOT-SCR\scenarios\ForestResiduals_SCR\5_EdgeCapacity.py"
set SETUP_REPAIR="C:\FTOT-SCR\scenarios\ForestResiduals_SCR\6_RepairTimeCost.py"


REM ==============================================
REM ====== RUN THE FTOT-SCR SET UP SCRIPTs =======
REM ==============================================

REM  SETUP SEISMIC EVENTS
%PYTHON% %SETUP_SEISMIC% || exit /b

REM  SETUP SCENARIO FILES
%PYTHON% %SETUP_SCENARIO% || exit /b

REM  SETUP FACILITY CAPACITY
%PYTHON% %SETUP_FACILITY% || exit /b

REM  SETUP BRIDGE DAMAGE FROM EARTHQUAKES
%PYTHON% %SETUP_BRIDGE% || exit /b

REM  SETUP EDGE CAPACITY
%PYTHON% %SETUP_EDGE% || exit /b

REM  SETUP REPAIR TIMES AND COSTS
%PYTHON% %SETUP_REPAIR% || exit /b
