
"""
Created on Wed Nov 01 2023

@author: Amulya
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from Outage_analysis_functions import outage_data

from scipy.integrate import simpson
from numpy import trapz

matplotlib.use("Qt5Agg")

# read in the data
# col_list = ['Outage_Reviewed','Outage',	'Time_Off',	'Time_On'	Number_Out	Duration	Customer Minutes
# Dispatch_Comments	Type	Map_Location	Cause_Cd	Cause Desc	Equip Cd	Equip Desc	Cause Grp	Master Outage
# Equip Grp	Crew	No Conn	Line Sect	Next Pro Dvc	Weather	Model ID	Voltage	Fault Location	Outage Name	District
# Trans	Phs	Dispatcher Acknowledged	Fault Current A Phase	Fault Current B Phase	Fault Current C Phase
# Fault Type A Phase	Fault Type B Phase	Fault Type C Phase	Work Orders
# ]
# df = pd.read_csv('3 Year Outage History.csv')

# Read Outage and wind data from file
df = pd.read_excel('outage_data/3 Year Outage History sorted.xlsx', sheet_name='Wind_with_loc')
wind_data = pd.read_csv('weather_data/Ford_wind_12_2020_05_2023.csv')

# Convert date and time columns to datetime dataframe
Wind_time = pd.to_datetime(wind_data['BEGIN_DATE']+' ' + wind_data['START_TIME'], format='mixed')
df['time_off'] = pd.to_datetime(df['Time Off'])
df['time_on'] = pd.to_datetime(df["Time On"])
# df['Duration'] = pd.to_datetime(df["Duration"])

outage_details = outage_data()

# Plot distribution system
plt.figure(figsize=(12, 6))
nodecoords = pd.read_excel('outage_data/nodecoords new.xlsx', sheet_name='in')
ss_coords = pd.read_excel('outage_data/nodecoords new.xlsx', sheet_name='ss')
X = nodecoords['lat']
Y = nodecoords['lon']

ax = plt.axes()
ax.set_aspect('equal')
ax.scatter(X, Y, marker='o', s=.5, label = 'Distribution system')

X_ss = ss_coords['lat']
Y_ss = ss_coords['lon']
ax.scatter(X_ss, Y_ss, marker='*', label = 'Substations')

# Weather station coordinates (Mean of the substation coordinates)
Y_ws = 37.76
X_ws = -99.96
ax.scatter(X_ws, Y_ws, marker='o', label = 'Weather Station(s)')
ax.legend()
plt.show()

# Outage locations and time wrt wind
X_outage = df['X']
Y_outage = df['Y']

r = 3961              # Radius of earth
dist = []
wind_mag_outage = []
Time_off = pd.to_datetime(df['time_off'])
for i in X_outage.index:
    # Calculate distance of outage from weather station
    d = 2 * r * np.arcsin(np.sqrt((np.sin((X_ws - X_outage.iloc[i])/2) ** 2) +
                                                                 np.cos(X_ws)*np.cos(X_outage.iloc[i]) *
                                                                 (np.sin((Y_ws - Y_outage.iloc[i])/2)) ** 2))
    dist.append(d)

# Spacial Statistics and plot
df['dist_to_ws'] = dist
print('Farthest outage distance from weather station:', max(df['dist_to_ws']))
print('Nearest outage distance from weather station:', min(df['dist_to_ws']))
print('Mean outage distance from weather station:', df['dist_to_ws'].mean())

plt.figure()
plt.hist(dist, bins=20, label = 'Outage distance from weather station')
plt.title('Outage distance from weather station')

# To Plot the performance curve
interval_duration = pd.Timedelta(minutes=5)
t_start = pd.Timestamp('2021-10-01 00:01:00')  # df['time_off'].min()   df['time_off'].iloc[100]   df['time_off'].min()    Define the start and end times
t_stop = pd.Timestamp('2021-10-31 11:59:00')   # df['time_off'].max()  # df['time_on'].iloc[50]  # max()
performance_data, Interpol_per = outage_details.performance_curve(df, wind_data, interval_duration, t_start, t_stop)

Interpol_per.to_csv('Outage_train_data.csv')
# Interpol_per.to_csv('Outage_Test_data_2022.csv')

y = np.array(performance_data['Performance'])
area = trapz(y, dx=60)
print("Customer Minutes =", area)
print("Customer Hours =", area/60)
print("Customer Days =", area/(60*24))


# CAIDI Calculation
td = interval_duration.total_seconds()
td = td/60
CAIDI = 0
SAIDI = 0
SAIFI = 0
for i in performance_data['Performance'].index:
    if performance_data['Performance'].iloc[i] != 0:
        CAIDI = CAIDI + td / performance_data['Performance'].iloc[i]
        SAIDI = SAIDI + td
        SAIFI = SAIFI + 1

print("CAIDI = ", CAIDI)


# Statistics Calculation
wind_stats = outage_details.outage_statistics(df)
print(wind_stats)