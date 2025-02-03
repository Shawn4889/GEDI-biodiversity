#Author: Xiaoxuan Li
import pandas as pd
import numpy as np
import shutil
import os
import h5py


beam0 = ["BEAM0000", "BEAM0001", "BEAM0010", "BEAM0011"]
beam1 = ["BEAM0101", "BEAM0110", "BEAM1000", "BEAM1011"]
GEDI_loc = r"F:\GEDI\GEDI_archive"
GEDI_L2A_dir = GEDI_loc + r"/GEDI02A/Amazon/"
GEDI_L2B_dir = GEDI_loc + r"/GEDI02B/Amazon/"
CSV_dir = GEDI_loc + r"/SA.csv"
Result_dir = r"F:\GEDI\Result_Luther\Result_11132024\GEDI/"


coordinate_output = Result_dir  + "GEDI_Amazon_11132024.csv"
coordinate_initial = []
df_coordinate_initial = pd.DataFrame(coordinate_initial)
df_geo = pd.read_csv(CSV_dir, sep=",")
lat_max = -2.317222
lat_min = -2.484444
lon_max = -59.734444
lon_min = -60.151111
#-2.484444,-60.151111
#-2.317222,-59.734444

HDF_folder = os.listdir(GEDI_L2A_dir)
#for i in range(6):
for files in HDF_folder:
    print(files)
    # read HDF file
    GEDI_L2A = GEDI_L2A_dir + files
    GEDI_L2B_1 = GEDI_L2B_dir + 'GEDI02_B_' + os.path.splitext(files)[0][9:-15] + "_02_003_01_V002.h5"
    f_L2A = h5py.File(GEDI_L2A, 'r')
    if os.path.exists(GEDI_L2B_1):
        f_L2B = h5py.File(GEDI_L2B_1, 'r')
    else:
        GEDI_L2B_2 = GEDI_L2B_dir + 'GEDI02_B_' + os.path.splitext(files)[0][9:-15] + "_02_003_02_V002.h5"
        f_L2B = h5py.File(GEDI_L2B_2, 'r')
    # beam list
    beam = list(f_L2A.keys())
    beam.remove("METADATA")
    for b in beam:
        #print(b)
        # beam sel
        if b in beam0:
            Beam = b + "_0"
        else:
            Beam = b + "_1"
        #print(Beam)
        df_lat = pd.DataFrame(np.array(f_L2A[b + '/lat_lowestmode'][:]), columns=['lat'])
        df_long = pd.DataFrame(np.array(f_L2A[b + '/lon_lowestmode'][:]), columns=['long'])
        df_quality_l2A = pd.DataFrame(np.array(f_L2B[b + '/l2a_quality_flag'][:]), columns=['ql2a'])
        df_quality_l2B = pd.DataFrame(np.array(f_L2B[b + '/l2b_quality_flag'][:]), columns=['ql2b'])
        df_Coor = pd.concat([df_lat, df_long,df_quality_l2A,df_quality_l2B], axis=1)
        df_interaction = df_Coor[(df_Coor["lat"] > lat_min) &
                                 (df_Coor["lat"] < lat_max) &
                                 (df_Coor["long"] > lon_min) &
                                 (df_Coor["long"] < lon_max)]
        index_result = np.asarray(df_interaction.index.values)
        #print(index_result)
        if not df_interaction.empty:
            # Geolocation & Quality data
            df_shot = pd.DataFrame(np.array(f_L2B[b + '/shot_number'][index_result]), columns=['shot_number'])
            df_lat = pd.DataFrame(np.array(f_L2A[b + '/lat_lowestmode'][index_result]), columns=['lat'])
            df_long = pd.DataFrame(np.array(f_L2A[b + '/lon_lowestmode'][index_result]), columns=['long'])
            df_quality_l2A = pd.DataFrame(np.array(f_L2B[b + '/l2a_quality_flag'][index_result]), columns=['ql2a'])
            df_quality_l2B = pd.DataFrame(np.array(f_L2B[b + '/l2b_quality_flag'][index_result]), columns=['ql2b'])
            df_sensitivity = pd.DataFrame(np.array(f_L2A[b + '/sensitivity'][index_result]),columns=['sensitivity'])
            df_sf = pd.DataFrame(np.array(f_L2A[b + '/sensitivity'][index_result]),columns=['surface_flag'])
            df_dif = pd.DataFrame(np.array(f_L2A[b + '/degrade_flag'][index_result]),
                                                   columns=['degrade_flag'])
            df_pft_class = pd.DataFrame(np.array(f_L2A[b + '/land_cover_data/pft_class'][index_result]),
                                                   columns=['pft_class'])
            df_region_class = pd.DataFrame(np.array(f_L2A[b + '/land_cover_data/region_class'][index_result]),
                                                   columns=['region_class'])
            df_lwp = pd.DataFrame(np.array(f_L2A[b + '/land_cover_data/landsat_water_persistence'][index_result]),
                                           columns=['landsat_water_persistence'])
            df_up = pd.DataFrame(np.array(f_L2A[b + '/land_cover_data/urban_proportion'][index_result]),
                                  columns=['urban_proportion'])
            # RH metrics
            df_rh = pd.DataFrame(np.array(f_L2A[b + '/rh'][index_result]),
                                 columns=["{:02d}".format(x) for x in range(101)])
            df_rh_a = df_rh.loc[:, ['10', '30', '50', '70', '90', '95', '98', '100']]
            head = "RH"
            df_rh_a.columns = [head + '_10', head + '_30',
                               head + '_50', head + '_70', head + '_90',
                               head + '_95', head + '_98', head + '_100']
            #L2B metrics -z 5m interval
            df_fhd = pd.DataFrame(np.array(f_L2B[b + '/fhd_normal'][index_result]), columns=['FHD'])

            df_cover_a = pd.DataFrame(np.array(f_L2B[b + '/cover_z'][index_result]))
            df_cover_list = df_cover_a.loc[:, range(10)]
            head = "cover"
            df_cover_list.columns = [head + '_5', head + '_10', head + '_15',
                                     head + '_20', head + '_25', head + '_30',
                                     head + '_35', head + '_40', head + '_45', head + '_50']
            df_pai_a = pd.DataFrame(np.array(f_L2B[b + '/pai_z'][index_result]))
            df_pai_list = df_pai_a.loc[:, range(10)]
            head = "pai"
            df_pai_list.columns = [head + '_5', head + '_10', head + '_15',
                                     head + '_20', head + '_25', head + '_30',
                                     head + '_35', head + '_40', head + '_45', head + '_50']
            df_pavd_a = pd.DataFrame(np.array(f_L2B[b + '/pavd_z'][index_result]))
            df_pavd_list = df_pavd_a.loc[:, range(10)]
            head = "pavd"
            df_pavd_list.columns = [head + '_5', head + '_10', head + '_15',
                                     head + '_20', head + '_25', head + '_30',
                                     head + '_35', head + '_40', head + '_45', head + '_50']

            def count_local_maxima(df, suffix):
                def count_local_maxima(nums):
                    count = 0
                    for i in range(1, len(nums) - 1):
                        if nums[i] > nums[i - 1] + 0.1 * nums[i] and \
                                nums[i] > nums[i + 1] + 0.1 * nums[i] \
                                and nums[i] > 0:
                            count += 1
                    return count
                df_c = df.apply(lambda row: count_local_maxima(row.values), axis=1)
                df_c = pd.DataFrame(df_c, columns=[suffix])
                return df_c

            df_covers = count_local_maxima(df_cover_a, "cover_LMC")
            df_pais = count_local_maxima(df_pai_a, "pai_LMC")
            df_pavds = count_local_maxima(df_pavd_a, "pavd_LMC")

            def sum_first_half(row):
                non_negative_values = [value for value in row if value not in [-9999.0,0.0, np.inf]]
                half_index = len(non_negative_values) // 2
                if len(row) % 2 == 1:
                    return sum(row[:half_index]) + 0.5 * row[half_index]
                else:
                    return sum(row[:half_index])
            def sum_last_half(row):
                non_negative_values = [value for value in row if value not in [-9999.0,0.0, np.inf]]
                half_index = len(non_negative_values) // 2
                if len(row) % 2 == 1:
                    return sum(row[half_index + 1:]) + 0.5 * row[half_index]
                else:
                    return sum(row[half_index:])
            df_cover_ratio = df_cover_list.apply(sum_first_half, axis=1)/df_cover_list.apply(sum_last_half, axis=1)
            df_pai_ratio = df_pai_list.apply(sum_first_half, axis=1)/df_pai_list.apply(sum_last_half, axis=1)
            df_pavd_ratio = df_pavd_list.apply(sum_first_half, axis=1)/df_pavd_list.apply(sum_last_half, axis=1)
            df_cover_ratio = pd.DataFrame(df_cover_ratio, columns=["cover_ratio"])
            df_pai_ratio = pd.DataFrame(df_pai_ratio, columns=["pai_ratio"])
            df_pavd_ratio = pd.DataFrame(df_pavd_ratio, columns=["pavd_ratio"])
            df_profile = pd.concat([df_shot, df_lat, df_long,
                                    df_quality_l2A, df_quality_l2B, df_rh_a,
                                    df_fhd, df_cover_list, df_pai_list, df_pavd_list,
                                    df_covers, df_pais, df_pavds, df_cover_ratio, df_pai_ratio, df_pavd_ratio,
                                    df_sensitivity, df_sf, df_dif, df_pft_class, df_region_class, df_lwp, df_up],
                                   axis=1)
            #df_profile = df_profile.loc[index_result, :]
            df_coordinate_initial = pd.concat([df_coordinate_initial,df_profile])
        else:
            print("no interaction between the GEDI track and bounding box")
if not df_coordinate_initial.empty:
    print("Output..." + coordinate_output)
    df_coordinate_initial['shot_number'] = 'Shot_' + df_coordinate_initial['shot_number'].astype(str)
    df_coordinate_initial.to_csv(coordinate_output, index=None)
else:
    print("no GEDI shots locate within the area")
