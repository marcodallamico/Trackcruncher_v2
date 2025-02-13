import os
import shutil
import pandas as pd
import numpy as np

# Some of the tracks do not complete the full evolution, and thus cannot be used in SEVN.
# To fix this issue, here we add fake lines in the tables to still allow SEVN to read them
# Of course, it is necessary to evolve these stars in SEVN only for the age below which all the
# outputs in the tables are true, and not fake


# Output folder for the complete tables
output_folder = "tables_Nguyen_lowmass_fixed"
os.makedirs(output_folder, exist_ok=True)

# Target folder for tracks to be fixed
target_folder = "tables_Nguyen_lowmass/"

# Iterate through each subfolder in the low mass folder
for subfolder in os.listdir(target_folder):
    subfolder_path = os.path.join(target_folder, subfolder)

    if os.path.isdir(subfolder_path):
        # Step 1: Copy the folder and its content inside the output folder
        output_subfolder = os.path.join(output_folder, subfolder)
        shutil.copytree(subfolder_path, output_subfolder)

        phase_file = os.path.join(output_subfolder, 'phase.dat')

        if os.path.exists(phase_file):
            with open(phase_file, 'r') as pf:
                phase_lines = pf.readlines()

            # Process phase.dat
            updated_phase_lines = []
            added_odd_count_list = []  # List to keep track of added odd columns for each line
            added_odd_values_list = []  # List to store the odd values added for each line
            for line in phase_lines:
                columns = line.split()
                added_odd_count = 0  # Counter for odd columns added
                added_odd_values = []  # List to store the odd values added to this line

                if len(columns) < 14:
                    last_odd  = float(columns[-2])            # TEMPO
                    last_even = int(columns[-1])           # FASE

                    while len(columns) < 14:
                        last_odd += 1e9                             #   add a huge number to the age
                        columns.append(f"{last_odd:.8e}")
                        added_odd_count += 1
                        added_odd_values.append(f"{last_odd:.8e}")  # Store added odd values
                        last_even += 1
                        columns.append(str(last_even))

                updated_phase_lines.append("   ".join(columns) + "\n")
                added_odd_count_list.append(added_odd_count)  # Store the count for each line
                added_odd_values_list.append(added_odd_values)  # Store the added odd values

            # Write back the corrected phase.dat
            with open(phase_file, 'w') as pf:
                pf.writelines(updated_phase_lines)

            # Step 2: Update every other file with the last value extension
            phase_line_count = len(updated_phase_lines)
            for file_name in os.listdir(output_subfolder):
                if file_name == "phase.dat":
                    continue

                elif file_name == 'time.dat':
                    file_path = os.path.join(output_subfolder, file_name)
                    with open(file_path, 'r') as f:
                        lines = f.readlines()

                    with open(file_path, 'w') as f:
                        for i, line in enumerate(lines):
                            # Get the odd values that were added for this line
                            added_odd_values = added_odd_values_list[i]

                            # Append the added odd values as floats
                            new_line = line.strip() + "   " + "   ".join(added_odd_values) + "\n"

                            # Write the modified line
                            f.write(new_line)

                else:
                    file_path = os.path.join(output_subfolder, file_name)
                    with open(file_path, 'r') as f:
                        lines = f.readlines()

                    with open(file_path, 'w') as f:
                        for i, line in enumerate(lines):
                            # Get how many odd values were added for this line
                            added_values_count = added_odd_count_list[i]

                            # Get the last value in the line
                            last_value = line.split()[-1]
                            # last_value *= 1000                      #   add a random large amount to highlight this is fake

                            if last_value!=0:
                                # Create the new line with added values
                                # new_line = line.strip() + "   " + "   ".join([f"{float(last_value) * 1000:.8e}"] * (added_values_count)) + "\n"
                                new_line = line.strip() + "   " + "   ".join([f"{float(last_value):.8e}"] * (added_values_count)) + "\n"

                            else:
                                new_line = line.strip() + "   " + "   ".join([f"{0.1:.8e}"] * (added_values_count)) + "\n"

                            # Write the modified line
                            f.write(new_line)
