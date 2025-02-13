import numpy as np
import pandas as pd

# here the code is not using the trackcruncher functions reset_hecore and reset_cocore (see table.h lin.420)

# Define the phase enumeration
class Phases:
    PreMainSequence = 0
    MainSequence = 1
    TerminalMainSequence = 2
    HshellBurning = 3
    HecoreBurning = 4
    TerminalHecoreBurning = 5
    HeshellBurning = 6
    Remnant = 7
    Nphases = 8

def determine_phases(df, stevocode="parsec", agb_flag=False, PSIC_tshold=15):
    """ Assigns evolutionary phases to the dataframe based on trackcruncher table.cpp l.494 """

    df['phase'] = np.nan  # Initialize the phase column
    sethe = False
    maxindex_ycen_last = df['ycen'].idxmax()
    maxindex_co_first = df['qcarox'].idxmax()

    for i in range(len(df)):
        last_phase = df['phase'].iloc[i-1] if i > 0 else None

        if df.loc[i, 'qhel'] != 0.0 and not sethe:
            sethe = True

        if df.loc[i, 'xcen'] > 1e-3 and last_phase is None:
            df.loc[i, 'phase'] = Phases.PreMainSequence
            maximum_phase = Phases.PreMainSequence

        elif (stevocode != "mist" and df.loc[i, 'xcen'] > 1e-3 and df.loc[i, 'xcen'] < df.loc[0, 'xcen'] * 0.99
              and df.loc[i, 'l_grav'] < 0.0 and df.loc[i, 'lx'] > 0.6 and last_phase < Phases.MainSequence
              and df.loc[i, 'qhel'] == 0.0):
            if last_phase != Phases.PreMainSequence:
                print(f"Error: Setting MainSequence but last phase was {last_phase}")
                return df, True
            df.loc[i, 'phase'] = Phases.MainSequence
            maximum_phase = Phases.MainSequence

        elif (stevocode == "mist" and df.loc[i, 'xcen'] > 1e-3 and df.loc[i, 'xcen'] < df.loc[0, 'xcen'] * 0.99
              and df.loc[i, 'lx'] > 0.6 and last_phase < Phases.MainSequence and df.loc[i, 'qhel'] == 0.0):
            if last_phase != Phases.PreMainSequence:
                print(f"Error: Setting MainSequence but last phase was {last_phase}")
                return df, True
            df.loc[i, 'phase'] = Phases.MainSequence
            maximum_phase = Phases.MainSequence

        elif df.loc[i, 'qhel'] != 0.0 and df.loc[i, 'qcarox'] == 0.0 and last_phase < Phases.TerminalMainSequence:
            if last_phase != Phases.MainSequence:
                print(f"Error: Setting TerminalMainSequence but last phase was {last_phase}")
                return df, True
            df.loc[i, 'phase'] = Phases.TerminalMainSequence
            maximum_phase = Phases.TerminalMainSequence

        elif df.loc[i, 'qcarox'] == 0.0 and df.loc[i, 'xcen'] < 1e-8 and last_phase < Phases.HshellBurning:
            if last_phase != Phases.TerminalMainSequence:
                print(f"Error: Setting HshellBurning but last phase was {last_phase}")
                return df, True
            df.loc[i, 'phase'] = Phases.HshellBurning
            maximum_phase = Phases.HshellBurning

        elif (df.loc[i, 'qcarox'] == 0.0 and i > maxindex_ycen_last
              and df.loc[i, 'ycen'] / df.loc[maxindex_ycen_last, 'ycen'] < 0.99
              and df.loc[i, 'xcen'] < 1e-8 and df.loc[i, 'ycen'] > 1e-3
              and last_phase < Phases.HecoreBurning):
            if last_phase != Phases.HshellBurning:
                print(f"Error: Setting HecoreBurning but last phase was {last_phase}")
                return df, True
            df.loc[i, 'phase'] = Phases.HecoreBurning
            maximum_phase = Phases.HecoreBurning

        elif df.loc[i, 'qcarox'] != 0.0 and last_phase < Phases.TerminalHecoreBurning:
            if last_phase != Phases.HecoreBurning:
                print(f"Error: Setting TerminalHecoreBurning but last phase was {last_phase}")
                return df, True
            df.loc[i, 'phase'] = Phases.TerminalHecoreBurning
            maximum_phase = Phases.TerminalHecoreBurning

        elif df.loc[i, 'qcarox'] != 0.0 and df.loc[i, 'lc'] < 0.2 and df.loc[i, 'ycen'] < 1e-8 and last_phase < Phases.HeshellBurning:
            if last_phase != Phases.TerminalHecoreBurning:
                print(f"Error: Setting HeshellBurning but last phase was {last_phase}")
                return df, True
            df.loc[i, 'phase'] = Phases.HeshellBurning
            maximum_phase = Phases.HeshellBurning

        elif (df.loc[i, 'xc_cen'] > 1e-8 and df.loc[i, 'ycen'] < 1e-8 and last_phase == Phases.HeshellBurning
              and 'psi_c' in df.columns and 'm_core_c' in df.columns):
            if agb_flag and df.loc[i, 'psi_c'] >= PSIC_tshold:
                print("Track stopped before AGB due to high degeneration")
                break
            elif (df.loc[i, 'm_core_c'] >= 0.9 * df.loc[maxindex_co_first, 'm_core_c'] and df.loc[i, 'lc'] > 0.2):
                print("Track stopped for reaching high lc")
                break
        else:
            df.loc[i, 'phase'] = last_phase

    return df, False
