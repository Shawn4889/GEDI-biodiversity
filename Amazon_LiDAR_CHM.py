# Author: Xiaoxuan Li
import os
import shutil
import arcpy
import subprocess
import pandas as pd
from whitebox_tools import WhiteboxTools

print("Amazon_LiDAR_CHM.py running")


def csv_to_shp():
    if os.path.isfile(Out_Buffer_dir3):
        print("Buffered GEDI shots already exist")
    else:
        print("Creating buffered GEDI shot shapefiles")
        arcpy.management.XYTableToPoint(Result_coordinate_dir, Out_XY_dir, "lon", "lat")
        arcpy.Buffer_analysis(Out_XY_dir, Out_Buffer_dir, "25 meters")
        arcpy.FeatureClassToShapefile_conversion(Out_Buffer_dir, SHP_dir)
        arcpy.Delete_management(Out_XY_dir)
        arcpy.Delete_management(Out_Buffer_dir)
        # set SR to buffered GEDI shots
        arcpy.Project_management(Out_Buffer_dir2, Out_Buffer_dir3, BoundingBox_dir)



def laz_to_las():
    las_folder = os.listdir(LiDAR_dir)
    data_folder = os.listdir(LiDAR_Ori_dir)
    # laszip file copy
    if len(las_folder) <= 1:
        try:
            #laszip copy
            shutil.copy2(LiDAR_Ori_dir + "laszip.exe", LiDAR_dir)
            # laz & prj file copy
            for i in data_folder:
                shutil.copy2(LiDAR_Ori_dir + i, LiDAR_dir)
        except:
            print("laszip.exe already exist or laz & prj files not found in target directory, check orbits")
        # convert laz to las
        print("Converting laz to las files")
        subprocess.call(LiDAR_dir + r'laszip ' + LiDAR_dir + r'*.laz')

    else:
        print("laz and prj file already transfered")


def las_subset():
    # create las, laz and prj file for clipping
    las_folder = os.listdir(LiDAR_dir)
    for j in las_folder:
        if "subset" not in j:
            if "las" in j:
                output = LiDAR_dir + str(j).split(".")[0] + "_subset.las"
                wbt.clip_lidar_to_polygon(i=LiDAR_dir + j, polygons=Out_Buffer_dir3, output=output)
                os.remove(LiDAR_dir + j)
            if "laz" in j:
                os.remove(LiDAR_dir + j)
        else:
            print("las files already clipped")

def chm():
    chm_folder = os.listdir(CHM_dir)
    if len(chm_folder) == 0:
        # Subset LAS to CHMs
        commands = [r'E:/R/R-3.6.2/bin/Rscript.exe', r'C:/Users/lxiao/Desktop/R/CHM.R']
        args = [Location]
        subprocess.call(commands + args)
    else:
        print("CHMs already exist")


def raster_to_point():
    # convert CHMs to points
    if not os.path.isfile(Result_CHM_dir):
        chm_folder = os.listdir(CHM_dir)
        chm_list = []
        for chm in chm_folder:
            fullname = CHM_dir + chm
            chm_list.append(fullname)
        arcpy.Append_management(chm_list[1:], chm_list[0], "TEST")
        # CHMs projections
        arcpy.DefineProjection_management(chm_list[0], BoundingBox_dir)
        arcpy.RasterToPoint_conversion(chm_list[0], Out_Point_dir, "VALUE")
    else:
        print("CHMs have transformed to points")


def spatial_join():
    if not os.path.isfile(Result_CHM_dir):
        # Spatial join
        fieldmappings = arcpy.FieldMappings()
        fieldmappings.addTable(Out_Buffer_dir3)
        fieldmappings.addTable(Out_Point_dir)
        attributes = ["Min", "Max", "StDev", "Mean", "Sum", "Count"]
        for a in attributes:
            chm_index = fieldmappings.findFieldMapIndex("grid_code")
            fieldmap = fieldmappings.getFieldMap(chm_index)
            field = fieldmap.outputField
            field.name = a
            field.aliasName = a
            fieldmap.outputField = field
            fieldmap.mergeRule = a
            fieldmappings.addFieldMap(fieldmap)

        removelist = ["grid_code", "BUFF_DIST", "ORIG_FID", "Shape_Leng", "Shape_Area", "pointid"]
        for r in removelist:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(r))
        arcpy.SpatialJoin_analysis(Out_Buffer_dir3, Out_Point_dir, Out_SpatialJoin_dir,
                                   "#", "KEEP_COMMON", fieldmappings, "INTERSECT")
        arcpy.SelectLayerByLocation_management(Out_SpatialJoin_dir, 'Within', 'Boundingbox_lyr')
        arcpy.TableToExcel_conversion(Out_SpatialJoin_dir, Result_CHM_dir)
        arcpy.Delete_management(Out_Point_dir)
    else:
        print("CHM tables already exist")


def merge():
    data_xls = pd.read_excel(Result_CHM_dir)
    data_xls.to_csv(Result_CHM_final)
    arcpy.management.XYTableToPoint(Result_CHM_final, Out_Merge_dir, "lon", "lat")
    arcpy.Delete_management(Out_SpatialJoin_dir)


Location = "Amazon"
beam = [0, 1]

GDB_dir = "E:/temp/Konrad/LiDAR.gdb/"
SHP_dir = r"E:/temp/Konrad/LiDAR_CHM_Amazon/SHP/"
BB_dir = r"E:/temp/Konrad/LiDAR_CHM_Amazon/Boundingbox/"
BoundingBox_dir = BB_dir + "LiDAR_BB.shp"
arcpy.MakeFeatureLayer_management(BoundingBox_dir, 'Boundingbox_lyr')

print(Location)x`
Result_dir = r"E:/temp/Konrad/LiDAR_CHM_Amazon/Parquet_Amazon/" + Location + "/"
Result_M_dir = r"E:/temp/Konrad/LiDAR_CHM_Amazon/Merge/" + Location + "/"
Result_coordinate_dir = Result_dir + "GEDI.csv"

if not os.path.isfile(Result_coordinate_dir):
    print("No data output from Parquet_Amazon.py, please check")
else:
    print(Location)
    wbt = WhiteboxTools()
    LiDAR_dir = r'E:/temp/Konrad/LiDAR_CHM_Amazon/LiDAR/' + Location + "/"
    CHM_dir = "E:/temp/Konrad/LiDAR_CHM_Amazon/CHM/" + Location + "/"
    Out_XY_dir = GDB_dir + Location + "_coordinates"
    Out_Buffer_dir = GDB_dir + Location + "_Buffer"
    Out_Buffer_dir2 = SHP_dir + Location + "_Buffer.shp"
    Out_Buffer_dir3 = SHP_dir + Location + "_Buffer_Project.shp"
    Out_Point_dir = GDB_dir + Location + "_point"
    Out_SpatialJoin_dir = GDB_dir + Location + "_SpatialJoin"
    Out_Merge_dir = GDB_dir + Location + "_Merge"
    LiDAR_Ori_dir = "E:/temp/Konrad/LiDAR_Ori/Amazon/data/"
    Result_CHM_dir = Result_M_dir + "GEDI_CHMs.xls"
    Result_CHM_final = Result_M_dir + "GEDI_CHMs.csv"
    list = []
    #dir test
    if not os.path.isdir(Result_M_dir):
        os.makedirs(Result_M_dir)
    if not os.path.isdir(SHP_dir):
        os.makedirs(SHP_dir)
    if not os.path.isdir(LiDAR_dir):
        os.makedirs(LiDAR_dir)
    if not os.path.isdir(CHM_dir):
        os.makedirs(CHM_dir)


    print("CSV_to_Shp")
    print("Select_by_Location")
    # intersection between boundingbox and GEDI shots: identify tiles
    # GEDI shots from CSV to Shapefile: create GEDI shot feature class
    csv_to_shp()

    print("laz_to_las")
    # laz to las: only those las files within identified tiles are converted
    laz_to_las()

    print("las_subset")
    # subset las using GEDI shots: clip those selected las files based on GEDI footprints
    las_subset()

    print("las to CHM raster")
    # las to CHM raster: CHMs are created in R using those clipped las files
    # Defile projection: project CHMs using standard spatial reference
    chm()

    print("Raster Statistics")
    print("Defile projection")
    # Raster to Point
    raster_to_point()

    print("Spatial Join")
    #Spatial Join: CHM statistics
    spatial_join()


    print("Merge")
    #Merge CHM csv file and GEDI foorprint csv files
    merge()
