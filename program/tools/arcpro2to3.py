from arcpy import AnalyzeToolsForPro_management
import glob
import os

# get all of the py2 files matching the pattern
report_directory = 'c:/ftot-scr/program/2to3report/'
if not os.path.exists(report_directory):
    os.makedirs(report_directory)


print("Starting the inspection")
py2_files = glob.glob('c:/ftot-scr/program/*.py')
py2_files += glob.glob('c:/ftot-scr/program/tools/*.py')
py2_files += glob.glob('c:/ftot-scr/SecondaryScripts/*.py')
py2_files += glob.glob('C:/FTOT-SCR/scenarios/ForestResiduals_SCR/*.py')
print("number of files: {}".format(len(py2_files)))
counter = 0
for a_file in py2_files:
    counter += 1
    print("inspecting: {}".format(a_file))
    try:
        AnalyzeToolsForPro_management(a_file, '{}_{}_2to3pro.txt'.format(report_directory, counter))
    except:
        print("...error...moving on!")
        continue
    print("...complete!")


# get all the reports
print("concating the reports'")
py2to3_reports = glob.glob("{}*.txt".format(report_directory))
print("length of reports to process: ".format(len(py2to3_reports)))
report_file = os.path.join(report_directory, "concat_report.txt")
with open(report_file, 'w') as wf:
    wf.write('\nFTOT 2020.1 REPORT ON PYTHON 2 to 3 CONVERSION USING AnalyzeToolsForPro\n')
    for a_report in py2to3_reports:
        #  - concat tableau_report.csv
        print("...working on {}".format(a_report))
        txt_in = open(a_report)
        for line in txt_in:
            if line.find("Found Python 2 to 3 errors: Line") > 0:
                wf.write(line.split('errors: ')[0])
                wf.write(line.split(': ')[1])
            else:
                wf.write(line)
        txt_in.close()
        wf.write('\n\n\n')
        print("......done!")
print("...done!")