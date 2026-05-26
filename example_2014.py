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

matplotlib.use('TkAgg')

outage_file = 'data/Grid_disruption_2014.xlsx'
outage_df = pd.read_excel(outage_file)

# Performance curve analysis
# To Plot the performance curve
font = {'size': 22}

matplotlib.rc('font', **font)

outage_details = outage_data()
out_min = 5             # time delta for analysis
interval_duration = pd.Timedelta(minutes=out_min)
t_start = pd.Timestamp('2000-01-23 00:00:00')  # Define the start and end times  t_start > winddata minimum time
t_stop = pd.Timestamp('2000-08-31 00:36:00')   # df['time_off'].max()  # df['time_on'].iloc[50]  # max()
performance_data = outage_details.performance_curve(outage_df, interval_duration, t_start, t_stop)
# # Metrics Calculation
# y = np.array(performance_data['Performance'])
