"""
Created on Wed Dec 13 2023

@author: Amulya
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import geopandas as gpd
from outage_analysis_functions import outage_data
from scipy.integrate import simpson
from numpy import trapz

def cum_analysis(outage_ford):
    unique_wind_speeds = outage_ford['wind_mag'].unique()  # Interpol_per['Wind speed'].unique()
    unique_wind_speeds = np.sort(unique_wind_speeds)
    # Calculate cumulative outages for each wind speed
    cum_outage = [0] * len(unique_wind_speeds)
    num_outage = [0] * len(unique_wind_speeds)
    cum_outage_std = [0] * len(unique_wind_speeds)
    c = 0
    for wind in unique_wind_speeds:
        total = []
        for i in outage_ford['wind_mag'].index:  # Interpol_per['Wind speed'].index:
            if outage_ford['wind_mag'].iloc[i] == wind:  # Interpol_per['Wind speed'].iloc[i] == wind:
                total.append(outage_ford['# Out'].iloc[i])  # Interpol_per['Outage Rate'].iloc[i])
        # print(df['# Out'].iloc[i])
        cum_outage[c] = np.mean(total)
        cum_outage_std[c] = np.std(total)
        num_outage[c] = len(total)
        c = c + 1

    cum_outage_std = np.array(cum_outage_std)
    cum_outage = np.array(cum_outage)
    cum_outage_data = {'wind_speed':unique_wind_speeds, 'cum_outage':cum_outage, 'outage_std':cum_outage_std}
    cum_outage_data = pd.DataFrame(data = cum_outage_data)
    return cum_outage_data

matplotlib.use("Qt5Agg")

outage_ford = pd.read_excel('Outage_with_wind.xlsx', sheet_name='Ford')
wind_data_ford = pd.read_csv('weather_data/ford_wind_data.csv')
# outage_ford = pd.read_excel('outage_data/3 Year Outage History new.xlsx', sheet_name='Outage_Ford')
outage_ford = outage_ford.dropna(subset=['Outage'])

sections = outage_ford['Section'].unique()

plt.hist(outage_ford['Section'], bins= len(sections) , histtype='bar', rwidth=0.8)
plt.xticks(rotation='vertical')

# ********************************* Plot county ***************************************************************
county_shp = gpd.read_file('Social_data/cb_2022_20_bg_500k.zip')
lou_shp_ford = county_shp[county_shp['COUNTYFP'] == '057']
lou_shp_ford['FIPS'] = lou_shp_ford['STATEFP'] + lou_shp_ford['COUNTYFP'] + lou_shp_ford['TRACTCE'] + lou_shp_ford['BLKGRPCE']
svs_data = pd.read_excel('Social_data/SVS values for Ford county, Kansas at block group level.xlsx')

ax1 = lou_shp_ford.plot(color='#D3D3B2', label="Ford County")
# lou_shp_ford.boundary.plot(ax =ax1, color = 'gray')

# ******************************** Plot distribution system **********************************************************
nodecoords = pd.read_excel('outage_data/nodecoords new.xlsx', sheet_name='in')
ss_coords = pd.read_excel('outage_data/nodecoords new.xlsx', sheet_name='ss')

nodecoords = nodecoords[nodecoords['Folder'].isin(sections)]
# Get unique groups
uniqueGroups = np.unique(nodecoords['Folder'])
# Set colors and markers
colors = plt.cm.hsv(np.linspace(0, 1, len(uniqueGroups)))
colors[:, 3] = 0.1
colors[21, 3] = 1 #np.array([0,0,0,1])   # 'TRAIL_D1_STREET'
colors[5 ,3] = 1 #np.array([0,0,0,0.5])  # 'BUCKLIN-RURAL'  '14TH_D1_AVE'
colors[15, 3] = 1 #np.array([1,0,0,1])   #'MULBERRY-RURAL'
markers = 'o' * len(uniqueGroups)
X = nodecoords['lat']
Y = nodecoords['lon']
# Create figure and scatter plot
for i, group in enumerate(uniqueGroups):
    mask = nodecoords['Folder'] == group
    ax1.scatter(X[mask], Y[mask], c=colors[i], s=.5, marker=markers[i])
ax1.axis('tight')
ax1.legend(uniqueGroups)
plt.show()

plt.figure()
plt.scatter(outage_ford['wind_mag'], outage_ford['# Out'])

cum_outage_data = cum_analysis(outage_ford)

cum_outage_std = np.array(cum_outage_data['outage_std'])
cum_outage = np.array(cum_outage_data['cum_outage'])
plt.figure()
plt.plot(cum_outage_data['wind_speed'], cum_outage, '-o')
plt.fill_between(cum_outage_data['wind_speed'], 0, (cum_outage+cum_outage_std), color='b', alpha=.1)
plt.xlabel('Wind speed (mph)')
plt.ylabel('Average #Outages')    #('Average Outage Rate (Outages/hour)')
plt.title('Wind based Outage Data: 2020-2023')

# Regression model
x = cum_outage_data['wind_speed']
y = cum_outage
y[list(x).index(55)] = 65
mymodel = np.poly1d(np.polyfit(x, y, 3))
myline = np.linspace(45, 75, 100)
# plt.scatter(x, y)
plt.figure()
plt.plot(myline, mymodel(myline)*1.6, label='Model fit')

# plt.fill_between(unique_wind_speeds, 0, (cum_outage+max(cum_outage_std)), color='b', alpha=.1)

# Model 2
test = pd.read_excel('Outage_with_wind.xlsx', sheet_name='test')
train = pd.read_excel('Outage_with_wind.xlsx', sheet_name='train')
# Create training data in correct format
train['Time'] = pd.to_datetime(train['time_off'])
train['date_delta'] = (train['Time'] - train['Time'].min())/np.timedelta64(1, 'D') # Convert date to float
train['wind_mag'] = train['wind_mag'].astype(float)

train_outage = mymodel(train['wind_mag'])
# font = {'family' : 'normal',
#         'weight' : 'bold',
#         'size'   : 22}
#
# matplotlib.rc('font', **font)
plt.figure()
plt.plot(train['Time'],train['# Out'], label='Actual')
plt.plot(train['Time'],train_outage, label='Model based')
plt.fill_between(train['Time'], 0, (train_outage+max(cum_outage_std)), color='b', alpha=.1)
plt.xlabel('Time')
plt.ylabel('# Outages')
plt.legend()
plt.title('2020-2022 Data')
# plt.rc('legend', fontsize=10)
# plt.rc('xtick', labelsize=8)    # fontsize of the tick labels
# plt.rc('ytick', labelsize=8)
# plt.rc('axes', labelsize=10)
# Step 5: Predict response
test['Time'] = pd.to_datetime(test['time_off'])
test['date_delta'] = (test['Time'] - test['Time'].min())/np.timedelta64(1, 'D') # Convert date to float
test['wind_mag'] = test['wind_mag'].astype(float)

test_outage = mymodel(test['wind_mag'])
plt.figure()
plt.scatter(test['Time'],test['# Out'], label='Actual')
plt.scatter(test['Time'],test_outage, label='Model based')
plt.fill_between(test['Time'], 0, (test_outage+max(cum_outage_std)), color='b', alpha=.1)
plt.legend()
plt.xlabel('Time')
plt.ylabel('# Outages')
plt.title('2023 Outages')

plt.figure()
plt.scatter(test['# Out'], test_outage)

# Performance curve analysis
# To Plot the performance curve
font = {'size': 22}

matplotlib.rc('font', **font)

outage_details = outage_data()
out_min = 5
interval_duration = pd.Timedelta(minutes=out_min)
t_start = pd.Timestamp('2022-05-10 00:00:00')  # Define the start and end times  t_start > winddata minimum time
t_stop = pd.Timestamp('2022-05-15 11:59:00')   # df['time_off'].max()  # df['time_on'].iloc[50]  # max()
performance_data, Interpol_per = outage_details.performance_curve(outage_ford, wind_data_ford, interval_duration, t_start, t_stop)
# Metrics Calculation
y = np.array(performance_data['Performance'])

new_per = []
pos = performance_data.index[performance_data['Performance'] < 0].tolist()
for i in pos:
    new_per.append(performance_data['Performance'].iloc[i])
area = -trapz(new_per, dx=out_min)
print("Customer Minutes =", area)
print("Customer Hours =", area/60)
print("Customer Days =", area/(60*24))

n_customers = 35000  #*3/4
SAIDI = area*(1/n_customers)
print("SAIDI: ", SAIDI)

non_per_data, Interpol_non_per = outage_details.non_performance_curve(outage_ford, wind_data_ford, interval_duration, t_start, t_stop)
new_per = []
pos = non_per_data.index[non_per_data['Performance'] < 0].tolist()
for i in pos:
    new_per.append(non_per_data['Performance'].iloc[i])
area = -trapz(new_per, dx=out_min)
print("Customer Minutes =", area)
print("Customer Hours =", area/60)
print("Customer Days =", area/(60*24))
SAIDI = area*(1/n_customers)
print("SAIDI: ", SAIDI)
