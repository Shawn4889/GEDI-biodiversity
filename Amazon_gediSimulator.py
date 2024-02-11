import pandas as pd
import os
import subprocess
import arcpy
#import Parquet_SA
#import LiDAR_CHM

print("Amazon_gediSimulator.py running")


def project():
    if arcpy.Exists(Amazon_merge_pro):
        print("Project already completed")
    else:
        arcpy.Project_management(Amazon_merge, Amazon_merge_pro, BoundingBox_dir)
        arcpy.CalculateGeometryAttributes_management(
            Amazon_merge_pro, [["lon", "POINT_X"], ["lat", "POINT_Y"]])


def spatial_join():
    if os.path.isfile(SJ_table):
        print("Spatial join already completed")
    else:
        arcpy.MakeFeatureLayer_management(BoundingBox_dir, 'Boundingbox_lyr')
        arcpy.SpatialJoin_analysis(Amazon_merge_pro, 'Boundingbox_lyr', SJ_output,"", "", "", "INTERSECT")
    arcpy.TableToExcel_conversion(SJ_output, SJ_table)


def rename():
    # rename clipped las file
    las_folder = os.listdir(LiDAR_dir)
    for r in las_folder:
        a = r.replace('_subset.las', '.las')
        os.rename(LiDAR_dir + r, LiDAR_dir + a)






def txt():
    for i in list_lasname:
        output = simulator_folder + str(i) + ".txt"
        print(i)
        df_sub = df.loc[df['FILE'] == str(i)]
        df_text = df_sub[["lon", "lat", "shot_numbe"]]
        df_text.to_csv(output, header=False, index=None, sep='	')


def gedi_simulator():
    print("running gediSimulator in R")
    commands = [r'E:/R/R-3.6.2/bin/Rscript.exe', r'C:/Users/lxiao/Desktop/R/SimulationPy.R']
    args = ["Amazon"]
    subprocess.call(commands + args)


def join():
    initial = []
    df_initial = pd.DataFrame(initial)
    #gedi metrics attributes
    columns = ['shot_numbe', 'GEDI_sim_rhGauss_50','GEDI_sim_rhGauss_75','GEDI_sim_rhGauss_90',
               'GEDI_sim_rhGauss_95', 'GEDI_sim_rhGauss_100', 'GEDI_sim_rhMax_50', 'GEDI_sim_rhMax_75',
               'GEDI_sim_rhMax_90', 'GEDI_sim_rhMax_95', 'GEDI_sim_rhMax_100', 'GEDI_sim_rhInfl_50',
               'GEDI_sim_rhInfl_75', 'GEDI_sim_rhInfl_90', 'GEDI_sim_rhInfl_95', 'GEDI_sim_rhInfl_100',
               'GEDI_sim_guass_cover',  'GEDI_sim_max_cover', 'GEDI_sim_infl_cover','GEDI_sim_FHD']
    #remove irrelavant files
    tile_folder = os.listdir(simulator_folder)
    for i in tile_folder:
        if ("metric.txt" not in i) and (".xls" not in i):
            os.remove(simulator_folder + i)
    tile_folder = os.listdir(simulator_folder)
    for i in tile_folder:
        if ".xls" not in i:
            print(i)
            df_loop = pd.read_csv(simulator_folder + i,
                                  usecols=[0,23,28,31,32,33,44,49,52,53,54,65,70,73,74,75,98,99,100,116],
                                  header=0,sep=" ")
            df_initial = pd.concat([df_initial, df_loop])
    df_initial.columns = columns
    df_merge = pd.merge(df_initial, df, left_on='shot_numbe', right_on='shot_numbe', how='left')
    df_merge.drop_duplicates(keep='first', inplace=True)
    df_initial.to_csv(simulator_folder + "gediSimulator.csv", index=None)
    df_merge.to_csv(csv, index=None)


def output():
    #output csv & shp
    final_SHP = GDB_dir + "final_Amazon"
    arcpy.management.XYTableToPoint(csv, final_SHP, "lon", "lat","",BoundingBox_dir)
    arcpy.Buffer_analysis(final_SHP, Out_Buffer_dir, "25 meters")
    arcpy.Delete_management(SJ_output)
    arcpy.Delete_management(Amazon_merge_pro)
    arcpy.Delete_management(final_SHP)


#folder directories
simulator_folder = r"E:\temp\Konrad\LiDAR_CHM_Amazon\gediSimulator/"
LiDAR_dir = r'E:/temp/Konrad/LiDAR_CHM_Amazon/LiDAR/Amazon/'
xls = simulator_folder + "GEDI_CHM.xls"
csv = simulator_folder + "merged.csv"
GDB_dir = "E:/temp/Konrad/LiDAR.gdb/"
Amazon_merge = GDB_dir + "Amazon_Merge"
Amazon_merge_pro = Amazon_merge + "_P"
SJ_table = simulator_folder + "GEDI_CHM.xls"
SJ_output = GDB_dir + "Merge_SJ"
Out_Buffer_dir = GDB_dir + "final_Amazon_buffer"
BoundingBox_dir = r"E:/temp/Konrad/LiDAR_CHM_Amazon/Boundingbox/LiDAR_BB.shp"
#dir test
if not os.path.isdir(simulator_folder):
    os.makedirs(simulator_folder)

#GDB processing

#project and merge, GDB
print("project")
project()

#spatial_join, GDB
print("spatial_join")
spatial_join()

#dataframe set up
df = pd.read_excel(xls)
df['FILE'] = df['FILE'].str.strip()
df_lasname = df['FILE']
list_lasname = set(df_lasname.values.tolist())

#rename
print("rename")
rename()
#create gedi shot txt files
print("txt")
txt()
#run gediSimulator in R
print("gedi_simulator")
gedi_simulator()

#merge gedisimulated metrics txt files
print("join")
join()
#Output csvs for each study sites
print("output")
output()
