import os
import shutil
import pandas as pd
import numpy as np

# Output folder for the complete tables
output_folder = "tables_Nguyenlowmass_Costahighmass"
os.makedirs(output_folder, exist_ok=True)

# Target folder for low mass tables
target_folder_low_mass = "tables_Nguyen_lowmass_fixed/"

# Target folder for high mass tables
target_folder_high_mass = "/home/marco/Desktop/sevn/tables/SEVNtracks_parsec_ov05_AGB/"

# Iterate through each subfolder in the low mass folder
for subfolder in os.listdir(target_folder_low_mass):

    subfolder_path_low = os.path.join(target_folder_low_mass, subfolder)
    subfolder_path_high = os.path.join(target_folder_high_mass, subfolder)

    if os.path.isdir(subfolder_path_low) and os.path.isdir(subfolder_path_high):
        # Step 1: Copy the folder and its content inside the output folder
        output_subfolder = os.path.join(output_folder, subfolder)
        shutil.copytree(subfolder_path_low, output_subfolder)

        # Step 2: For every file in the new copy folder, append lines from the corresponding high mass file
        for file_name in os.listdir(subfolder_path_low):
            file_path_low = os.path.join(subfolder_path_low, file_name)
            file_path_high = os.path.join(subfolder_path_high, file_name)
            output_file_path = os.path.join(output_subfolder, file_name)

            if os.path.isfile(file_path_low) and os.path.isfile(file_path_high):
                # Read the content of both low mass and high mass files
                with open(file_path_low, 'r') as low_file:
                    low_file_content = low_file.readlines()

                with open(file_path_high, 'r') as high_file:
                    high_file_content = high_file.readlines()

                # Combine the contents of both files (append high mass content to low mass content)
                combined_content = low_file_content + high_file_content

                # Write the combined content to the output file
                with open(output_file_path, 'w') as output_file:
                    output_file.writelines(combined_content)
