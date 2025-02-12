
"""
These below are all the sevn tables produced with the Costa+2025 tracks
and the respective PARSEC column name from which the tables are derived
-------------------------------------------------------
PARSEC                  SEVN               NOT PRESENT
COLUMN                 OUTPUT             IN NGUYEN 2022
NAME                    TABLE                 TRACKS
-------------------------------------------------------
MASS                  mass_line
DPTH_CNV           depthconv_line               X
QCAROX               mco_line
TCNV_YR               tconv_line                X
Xsup/H_SUP            hsup_line
Ysup/HR_SUP          hesup_line
XCsup/C_SUP         csup_line.dat
XOsup/C_SUP          osup_line.dat
XNsup/N_SUP         nsup_line.dat
M_INERTI/TOT_INERTIA inertia_line               X
QHEL                   mhe_line
Rstar/RSTAR           radius_line
AGE                   time_line
LOG_L                 lumi_line
RHEL                   rhe_line                 X
RCAROX/R_CAROX         rco_line                 X
Q_CNV                  qconv_line               X

phase
----------------------------------------------------------
Regarding NGUYEN 2022 Tracks:
Whatchout, as some columns have different names for tracks
at different mass (e.g. Rstar for low mass, RSTAR for high mass)
+ high mass stars have more columns that are missing in low mass stars


Regarding trackcruncher:
read_track.h line 120 contains the name of the parsec columns assigned to the variable names
table.cpp line 180 assigns the variable names to the file names + the math used to write them
in the files

"""

# The following parameter is used to exclude lines from the original tracks
# e.g. Nmult=10 keeps only 1 every 10 lines of the original track
Nmult = 10 # Not used anymore

# Default values used if the PARSEC track column is not existing (valid only for optional tables,
# if a mandatory column is missing, the script is interrupted) - see Tab.1 Iorio+2023
# NB: the script returns a warning with all the column name missing from the tracks
# NB remember that, if any of these is used, to turn it off in the run.sh in sevn! These are all optionals
Q_CNV_def       = 0
DPTH_CNV_def    = 0
TCNV_YR_def     = 0
Xsup_def        = 0.7
Ysup_def        = 0.28
XCsup_def       = 0.003
XC13sup_def     = 4e-5
XOsup_def       = 0
XNsup_def       = 0
TOT_INERTIA_def = 1e54
RHEL_def        = 0
R_CAROX_def     = 0

import os
import shutil
import pandas as pd
import numpy as np
import phasefinder
import filtertracks

# Column effectively used in the tracks used to create the sevn tables, insert here all possible names (and also later in the script)
# NB: capital or lower characters do no matter, what needs to match is the sequence of characters
col = ["mass", "dpth_conv", "qcarox", "tcnv_yr", "xsup", "ysup", "xcsup", "xosup", "xnsup", "tot_inertia",
       "qhel", "rstar", "age", "log_l", "rhel", "r_carox", "q_cnv", "xcen", "ycen", "l_grav",
       "lx", "lc", "psi_c", "m_core_c", "xc_cen"]

# Step 1: Create the output folder for the sevn tables
output_folder = "tables_Costa_filtertracks"
os.makedirs(output_folder, exist_ok=True)

# Step 2: Define the target folder containing the PARSEC tracks
target_folder = "/home/marco/Desktop/tracks_costa/"
Nskip=0

# Step 3: Loop through subfolders in the target folder
for subfolder in os.listdir(target_folder):
    subfolder_path = os.path.join(target_folder, subfolder)

    if os.path.isdir(subfolder_path):
        new_name = next((part[1:].replace('.', '') for part in subfolder.split('_') if part.startswith('Z')), None) # change to a sevn table compatible name
        new_subfolder_path = os.path.join(output_folder, new_name)
        if os.path.exists(new_subfolder_path):
            shutil.rmtree(new_subfolder_path)
        os.makedirs(new_subfolder_path, exist_ok=True)

        # Step 4: Loop through PARSEC tracks and order them in ascending order
        files_and_masses = []

        for file_name in os.listdir(subfolder_path):
            if not file_name.endswith(".HB"):  # Exclude files ending with .HB
                file_path = os.path.join(subfolder_path, file_name)

                # Extract the mass from the file name
                original_name, ext = os.path.splitext(file_name)
                mass_str = original_name.split("_M")[-1]  # Extract part after "_M"
                if mass_str.startswith("."):  # Add leading zero if mass starts with a dot and remove the file extension
                    mass_str = "0" + mass_str
                try:
                    masstrack = float(mass_str)  # Convert to float
                    files_and_masses.append((file_name, masstrack))
                except ValueError:
                    print(f"Skipping file {file_name} due to invalid mass format")

        # Sort the files by masstrack (ascending order)
        files_and_masses.sort(key=lambda x: x[1])


        # Step 4: Loop through PARSEC tracks at different mass
        for file_name, masstrack in files_and_masses:
            print('Z=',new_name, ' -- Mtrack=',masstrack)

            # Check if mass is less than 2.2
            if (masstrack > 2.):                                                       # change

                file_path = os.path.join(subfolder_path, file_name)

                # Load the file with pandas
                df = pd.read_csv(
                    file_path,
                    sep=r"\s+",
                    skiprows=Nskip,
                    skipfooter=1,
                    engine="python"
                )
                # convert all the column in lower case as sometimes tracks
                # have not coherent column names
                df.columns = df.columns.str.lower()

                # FILTER 1: filter low time lines
                df = df[df['age'] > 0.2]
                df = df.reset_index(drop=True)

                # PHASE: compute the stellar phase as in trackcruncher original
                df = phasefinder.determine_phases(df)

                # CORRECT TIME: set the first output to time 0
                df["age"] = df["age"] - df.loc[0,"age"]

                # SAVE THE PHASE: the float after the phase number is the age when the phase begins
                file_path = os.path.join(new_subfolder_path, "phase.dat")
                if not os.path.exists(file_path):
                        with open(file_path, "w") as f:
                            pass  # Create an empty file if it doesn't exist
                phase_firstline = df.drop_duplicates(subset="phase", keep="first")
                with open(file_path, "a") as f:
                    for _, row in phase_firstline.iterrows():
                        f.write(f"{int(row['phase'])}   {row['age']/1e6:.8e}   ")
                    f.write("\n")

                # FILTER LINES 2
                # df = df.iloc[::Nmult]
                # df = df.reset_index(drop=True)
                df = filtertracks.filter_tracks(df)

                # FILTER COLUMNS: keeping only useful columns, and rise warning for missing
                df = df.loc[:, df.columns.intersection(col)]
                missing_cols = [c for c in col if c not in df.columns]
                if missing_cols:
                    print("WARNING - Missing columns in tracks ",masstrack," Msun: ", missing_cols)
                    print("These columns will be replaced with fixed default values")

                # CORRECTIONS
                # Here I follow the transformation of line 188 in table.cpp from trackcruncher
                # If a mandatory column is missing from the track, the script is stopped
                if 'mass' not in df.columns:
                    raise ValueError("MASS column is missing from the track with M=",masstrack)
                df.rename(columns={'MASS': 'mass'}, inplace=True)

                if 'q_cnv' not in df.columns:
                    df['q_cnv'] = Q_CNV_def
                df.rename(columns={'q_cnv': 'qconv'}, inplace=True)

                if 'dpth_conv' not in df.columns:
                    df['dpth_conv'] = DPTH_CNV_def
                df['depthconv'] = np.where(df['dpth_conv'] == 0, 0, np.power(10, df['dpth_conv']) / df['rstar'])
                df['depthconv'] = np.where(df['dpth_conv'] > 1, 1.0, df['dpth_conv'])

                if 'qcarox' not in df.columns:
                    raise ValueError("QCAROX column is missing from the track with M=",masstrack)
                df['mco'] = df['qcarox'] * df['mass']

                if 'tcnv_yr' not in df.columns:
                    df['tcnv_yr'] = TCNV_YR_def
                df['tconv'] = np.where(df['tcnv_yr'] == 0, 0, np.power(10, df['tcnv_yr'])) # in Parsec tconv is in log(yr)

                if 'xsup' not in df.columns:
                    df['xsup'] = Xsup_def
                df.rename(columns={'xsup': 'hsup'}, inplace=True)

                if 'ysup' not in df.columns:
                    df['ysup'] = Ysup_def
                df.rename(columns={'ysup': 'hesup'}, inplace=True)

                if 'xcsup' not in df.columns:
                    df['xcsup'] = XCsup_def
                if 'XC13sup' not in df.columns:
                    df['XC13sup'] = XC13sup_def
                df['csup'] = df['xcsup'] + df['XC13sup']

                if 'xosup' not in df.columns:
                    df['xosup'] = XOsup_def
                df.rename(columns={'xosup': 'osup'}, inplace=True)

                if 'xnsup' not in df.columns:
                    df['xnsup'] = xnsup_def
                df.rename(columns={'xnsup': 'nsup'}, inplace=True)

                if 'tot_inertia' not in df.columns:
                    df['tot_inertia'] = TOT_INERTIA_def
                df['inertia'] = np.power(10.0, np.log10(df['tot_inertia']) - 2.0 * np.log10(6.96e10) - np.log10(1.98892e+33)) # in solar units!! (Rsun^2 Msun)

                if 'qhel' not in df.columns:
                    raise ValueError("QHEL column is missing from the track with M=",masstrack)
                df['mhe'] = df['qhel'] * df['mass']

                if 'rstar' not in df.columns:
                    raise ValueError("Rstar column is missing from the track with M=",masstrack)
                df['radius'] = df['rstar']/6.96e10 # Rsun

                if 'age' not in df.columns:
                    raise ValueError("AGE column is missing from the track with M=",masstrack)
                df['time'] = df['age']/1.0e6 # Myr

                if 'log_l' not in df.columns:
                    raise ValueError("LOG_L column is missing from the track with M=",masstrack)
                df['lumi'] = np.power(10.0, df['log_l'])

                if 'rhel' not in df.columns:
                    df['rhel'] = RHEL_def
                df['rhe'] = df['rhel']/6.96e10 # Rsun

                if 'r_carox' not in df.columns:
                    df['r_carox'] = R_CAROX_def
                df['rco'] = df['r_carox']/6.96e10 # Rsun

                # Filter useless columns and keep only those used for the tables
                col_final = ["csup", "depthconv", "hesup", "hsup", "inertia", "lumi", "mass", "mco", "mhe", "nsup", "osup", "qconv", "radius", "rco", "rhe", "tconv", "time", "phase"]
                df = df.loc[:, df.columns.intersection(col_final)]


                # save in file for each column (if the file does not exist in the new_subfolder_path create the file and append)
                for column in df.columns:
                    file_path = os.path.join(new_subfolder_path, f"{column}.dat")

                    # Check if file exists, if not, create it
                    if not os.path.exists(file_path):
                        with open(file_path, "w") as f:
                            pass  # Create an empty file if it doesn't exist

                    # Get the values of the column
                    column_values = df[column].values

                    # Append the line to the file
                    with open(file_path, "a") as f:
                        f.write(f"{column_values[0]:.8e}")  # Write the first value without leading spaces
                        # Write the rest of the values with the separator
                        for value in column_values[1:]:
                            f.write(f"   {value:.8e}")
                        f.write("\n")  # End the line


