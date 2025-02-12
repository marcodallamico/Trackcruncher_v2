import numpy as np
import pandas as pd

def check_variation(values, v0, v1, t0, inv_dt, start, end, df, tab, max_rel_error=0.02):
    """
    Checks if the variation in values exceeds the allowed relative error.
    Returns True if the previous point (end-1) should be included.
    """
    slope = (v1 - v0) * inv_dt
    intercept = v0 - slope * t0

    for k in range(start, end):
        vinterp = slope * df["age"].iloc[k] + intercept
        vreal = values.iloc[k]
        variation = abs(vinterp - vreal)

        if variation != 0:
            error = variation / max(abs(vinterp), abs(vreal))
            if error > max_rel_error:
                tab[0] = end - 1  # Update tab to the last valid point
                return True
    return False

def check_variation_pow(values, v0, v1, t0, inv_dt, start, end, df, tab, max_rel_error=0.02):
    """
    Similar to check_variation, but applied to logarithmic values.
    """
    slope = (v1 - v0) * inv_dt
    intercept = v0 - slope * t0

    for k in range(start, end):
        vinterp = slope * df["age"].iloc[k] + intercept
        vreal = 10 ** values.iloc[k]
        variation = abs(vinterp - vreal)

        if variation != 0:
            error = variation / max(abs(vinterp), abs(vreal))
            if error > max_rel_error:
                tab[0] = end - 1  # Update tab to the last valid point
                return True
    return False

def filter_tracks(df, ndigit=8, max_rel_error=0.02):
    """
    Filters the dataframe based on linear interpolation error constraints.
    """
    filtered_indices = [0]  # First point is always included
    tab = [0]
    dimension = len(df)

    for i in range(2, dimension):
        order_of_mag = int(np.log10(df["age"].iloc[i]))
        min_dt = 10 ** (-ndigit) * 10 ** order_of_mag

        if i != 0 and (df["age"].iloc[i - 1] - df["age"].iloc[tab[0]]) < min_dt:
            continue

        if i != 0 and df["mass"].iloc[i - 1] < (df["qhel"].iloc[i - 1] * df["mass"].iloc[i - 1]):
            continue

        if i != 0 and df["qhel"].iloc[i - 1] < df["qcarox"].iloc[i - 1]:
            continue

        inv_dt = 1.0 / (df["age"].iloc[i] - df["age"].iloc[tab[0]])

        if check_variation(df["mass"], df["mass"].iloc[tab[0]], df["mass"].iloc[i], df["age"].iloc[tab[0]], inv_dt, tab[0] + 1, i, df, tab, max_rel_error):
            filtered_indices.append(tab[0])
            continue

        if check_variation_pow(df["log_l"], 10 ** df["log_l"].iloc[tab[0]], 10 ** df["log_l"].iloc[i], df["age"].iloc[tab[0]], inv_dt, tab[0] + 1, i, df, tab, max_rel_error):
            filtered_indices.append(tab[0])
            continue

        if check_variation(df["rstar"], df["rstar"].iloc[tab[0]], df["rstar"].iloc[i], df["age"].iloc[tab[0]], inv_dt, tab[0] + 1, i, df, tab, max_rel_error):
            filtered_indices.append(tab[0])
            continue

        if check_variation(df["qhel"], df["qhel"].iloc[tab[0]], df["qhel"].iloc[i], df["age"].iloc[tab[0]], inv_dt, tab[0] + 1, i, df, tab, max_rel_error):
            filtered_indices.append(tab[0])
            continue

        if i != 0 and df["qcarox"].iloc[i - 1] < df["qcarox"].iloc[tab[0]]:
            continue

        if check_variation(df["qcarox"], df["qcarox"].iloc[tab[0]], df["qcarox"].iloc[i], df["age"].iloc[tab[0]], inv_dt, tab[0] + 1, i, df, tab, max_rel_error):
            filtered_indices.append(tab[0])
            continue

    filtered_indices.append(dimension - 1)  # Ensure last point is included
    return df.iloc[sorted(set(filtered_indices))].reset_index(drop=True)
