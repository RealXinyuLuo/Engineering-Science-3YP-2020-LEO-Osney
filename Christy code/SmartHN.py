import sys
sys.path.append(r'c:\python37\lib\site-packages')



filename = r"C:\Users\chris\OneDrive\Documents\3rd Year\B3 - 3YP\Data\Heating1902.csv"

def SmartHN(filename):
    ''' Returns a date frame with normal and SMART HN demand for heating and cooling
    input: filename - cvs file containing and building heating and cooling demand'''

    import numpy as np
    import pandas as pd
    from HeatNetwork import HN_Demand

    df = pd.read_csv(filename)

    time = np.asarray(df['Time'].tolist())
    heating_demand = df['Heating Demand (kWh)'].tolist()
    cooling_demand = df['Cooling Demand (kWh)'].tolist()

    heating_elec = np.zeros(len(heating_demand))
    cooling_elec = np.zeros(len(cooling_demand))


    # Model Inputs
    COP_h = 5.2                   #COP of heating
    COP_c = 4                     #COP of cooling


    # Operating Flow Temperatures
    Tsc = 55                      #degrees C Flow Temperature
    Trc = 35                      #degrees C Return Temperatures



    ''' The function HN_Demand(Qc, Tsc, Trc, COP) returns a list

    [0] = HP Electricity Demand Under Normal Operation
    [1] = HN Pumping Demand
    [2] = HN Combined Electricity Demand without SMART operations '''

    # Normal Heating Mode
    i = 0
    while i < len(heating_demand):

        Qh = heating_demand[i]
        Qc = cooling_demand[i]


        if Qh == 0:
            heating_elec[i] = 7 / COP_h
        else:
            demand_h = HN_Demand(Qh, Tsc, Trc, COP_h)
            heating_elec[i] = demand_h[2]

        if Qc == 0:
            cooling_elec[i] = 7 / COP_c
        else:
            demand_c = HN_Demand(Qc, Tsc, Trc, COP_c)
            cooling_elec[i] = demand_c[2]

        i += 1



    # SMART Heating Mode

    grid_sig = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.8, 0.8, 0.8, 0.8, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1)

    excess_h = heating_demand[17] + heating_demand[18] + heating_demand[19]
    excess_c = cooling_demand[17] + cooling_demand[18] + cooling_demand[19]

    extra_h = excess_h/(COP_h*21)
    extra_c = excess_c/(COP_c*21)

    # Initialise vectors for SMART demand
    smart_heating_elec = np.zeros(len(heating_demand))
    smart_cooling_elec = np.zeros(len(heating_demand))

    hn_min = 0.024  # Minimum pumping power

    # Build SMART Electricity demand
    i = 0
    while i < len(heating_demand):

        Qh = heating_demand[i]
        Qc = cooling_demand[i]

        peak_times = (18, 19, 20)
        off_peak_times = (11, 12, 13, 14)

        # SMART Heating
        if Qh == 0:
            smart_heating_elec[i] = hn_min

        else:
            smartdemand_h = HN_Demand(Qh, Tsc, Trc, COP_h)

            hp_demand_h = smartdemand_h[0]
            pump_demand_h = smartdemand_h[1]
            hn_demand_h = smartdemand_h[2]

            if i in peak_times:

                smart_heating_elec[i] = 1.5 * pump_demand_h

            elif i in off_peak_times:

                smart_heating_elec[i] = hn_demand_h + 1 * extra_h

            else:
                smart_heating_elec[i] = hn_demand_h + 2 * extra_h



        # SMART Cooling
        if Qc == 0:
            smart_cooling_elec[i] = hn_min

        else:
            smartdemand_c = HN_Demand(Qc, Tsc, Trc, COP_c)

            hp_demand_c = smartdemand_c[0]
            pump_demand_c = smartdemand_c[1]
            hn_demand_c = smartdemand_c[2]

            if i in peak_times:

                smart_cooling_elec[i] = 1.5 * pump_demand_c

            elif i in off_peak_times:

                smart_cooling_elec[i] = hn_demand_c + 1 * extra_c

            else:
                smart_cooling_elec[i] = hn_demand_c + 2 * extra_c

        i += 1


    # Create Data Frame

    # time = time of day
    # grid_sig = Current Grid signal
    # heating_elec = HN electricity demand for normal heating
    # smart_heating_elec = HN electricity demand for SMART heating
    # cooling_elec = HN electricity demand for normal cooling
    # smart_cooling_elec = HN electricity demand for SMART cooling

    headings = ['Time', 'Grid Signal', 'Normal Heating (kWh)', 'SMART Heating (kWh)', 'Normal Cooling (kWh)',
                'SMART Cooling (kWh)']
    data = [time, grid_sig, heating_elec, smart_heating_elec,
            cooling_elec, smart_cooling_elec]

    sm_df = pd.DataFrame(data).T
    sm_df.columns = headings

    return sm_df










