# Author: Xiaoxuan Li
import pandas as pd
import numpy as np
import shutil
import os
import h5py


beam0 = ["BEAM0000", "BEAM0001", "BEAM0010", "BEAM0011"]
beam1 = ["BEAM0101", "BEAM0110", "BEAM1000", "BEAM1011"]

GEDI_L4A_dir = r"E:\GEDI\GEDI_archive\GEDI04A\Amazon/"
Result_dir = r"E:\GEDI\Result_Luther\Basic_GEDI/"

# result directory
coordinate_output = Result_dir + "GEDI_Amazon_biomass_01272024.csv"
coordinate_initial = []
df_coordinate_initial = pd.DataFrame(coordinate_initial)
lat_max = -2.317222
lat_min = -2.484444
lon_max = -59.734444
lon_min = -60.151111
HDF_folder = os.listdir(GEDI_L4A_dir)
for i in HDF_folder:
    if ".h5" in i:
        # read HDF file
        file = GEDI_L4A_dir + i
        print(file)
        f_L4A = h5py.File(file, 'r')
        # beam list
        beam = list(f_L4A.keys())
        beam.remove("METADATA")
        beam.remove("ANCILLARY")
        for b in beam:
            print(b)
            # beam sel
            if b in beam0:
                Beam = b + "_0"
            else:
                Beam = b + "_1"
            print(Beam)
            df_lat = pd.DataFrame(np.array(f_L4A[b + '/lat_lowestmode'][:]), columns=['lat'])
            df_long = pd.DataFrame(np.array(f_L4A[b + '/lon_lowestmode'][:]), columns=['long'])
            #df_quality_l2A = pd.DataFrame(np.array(f_L4A[b + '/l2_quality_flag'][:]), columns=['ql2'])
            df_quality_l4A = pd.DataFrame(np.array(f_L4A[b + '/l4_quality_flag'][:]), columns=['ql4'])
            df_Coor = pd.concat([df_lat, df_long, df_quality_l4A], axis=1)
            df_interaction = df_Coor[(df_Coor["lat"] > lat_min) &
                                     (df_Coor["lat"] < lat_max) &
                                     (df_Coor["long"] > lon_min) &
                                     (df_Coor["long"] < lon_max)]
            index_result = np.asarray(df_interaction.index.values)
            print(index_result)
            if not df_interaction.empty:
                # selected algor
                df_sa = pd.DataFrame(np.array(f_L4A[b + '/selected_algorithm'][:]), columns=['sel_al_biom'])
                # Geolocation & Quality data & AGBD
                df_shot = pd.DataFrame(np.array(f_L4A[b + '/shot_number'][:]), columns=['shot_number'])
                df_agbd = pd.DataFrame(np.array(f_L4A[b + '/agbd'][:]), columns=['AGBD'])
                # Merge all variables into one dataframe
                df = pd.concat([df_shot,df_Coor, df_agbd, df_sa], axis=1)
                df = df.loc[index_result, :]
                df["Beam"] = Beam
                df_coordinate_initial = pd.concat([df_coordinate_initial, df])
            else:
                print("no interaction between the GEDI track and bounding box")
if not df_coordinate_initial.empty:
    df_coordinate_initial['shot_number'] = 'Shot_' + df_coordinate_initial['shot_number'].astype(str)
    df_coordinate_initial.to_csv(coordinate_output, index=None)
else:
    print("No GEDI shots locate within the area")
if len(os.listdir(Result_dir)) == 0:
    shutil.rmtree(Result_dir)