# -*- coding: utf-8 -*-
"""
Created on Thur Oct 12 2023

@author: Amulya
"""
import math

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib

matplotlib.use('Tkagg')    # Added since figure was not responding in Pycharm


class outage_data():
    def __init__(self):
        print("outage class is invoked")

    def distance_calc(self, phi2, phi1, lam2, lam1):
        r = 3961              # Radius of earth
        d = 2 * r * np.arcsin(np.sqrt((np.sin((phi2 - phi1)/2) ** 2) +
                                      np.cos(phi1)*np.cos(phi2)*(np.sin((lam2 - lam1)/2)) ^ 2))
        return d

    def performance_curve(self, df, interval_duration, t_start, t_stop):  # df: Outage Management System data
        # Create a new DataFrame to store the aggregated data
        interval_data = pd.DataFrame(columns=['Interval Start', 'Interval End', 'Total Outages', 'Total Restored'])
        interval_data1 = pd.DataFrame(columns=['Interval Start', 'Total Outages', 'Total Restores', 'Performance'])

        # Iterate through intervals and calculate the total outages in each interval
        current_interval_start = t_start
        total_outages = 0
        total_restores = 0
        current_time = []

        while current_interval_start <= t_stop:

            # Performance curve calculation
            # print(current_interval_start, end=' ')
            current_interval_end = current_interval_start + interval_duration
            total_outage_entries = df[
                (df['time_off'] <= current_interval_end) & (df['time_off'] > current_interval_start)]
            total_outages = total_outages + total_outage_entries['Demand Loss (MW)'].sum()
            total_restore_entries = df[
                (df['time_on'] < current_interval_end) & (df['time_on'] >= current_interval_start)]

            total_restores = total_restores + total_restore_entries['Demand Loss (MW)'].sum()

            total_performance_in_interval = total_restores - total_outages

            interval_data = pd.concat([interval_data, pd.DataFrame({
                'Interval Start': [current_interval_start],
                'Interval End': [current_interval_end],
                'Total Outages': [total_outages],
                'Total Restored': [total_restores]
            })], ignore_index=True)
            interval_data1 = pd.concat([interval_data1, pd.DataFrame({
                'Interval Start': [current_interval_start],
                'Total Outages': [total_outages],
                'Total Restores': [total_restores],
                'Performance': total_performance_in_interval
            })], ignore_index=True)
            interval_data1 = pd.concat([interval_data1, pd.DataFrame({
                'Interval Start': [current_interval_end],
                'Total Outages': [total_outages],
                'Total Restores': [total_restores],
                'Performance': total_performance_in_interval
            })], ignore_index=True)


            current_time.append(current_interval_start)
            current_time.append(current_interval_end)
            current_interval_start = current_interval_end

        # Create a plot
        plt.figure(figsize=(12, 6))
        plt.plot(interval_data1['Interval Start'], interval_data1['Total Outages'], linestyle='-', label="Outage Curve")
        plt.plot(interval_data1['Interval Start'], interval_data1['Total Restores'], linestyle='-',
                 label="Restore curve")
        plt.plot(interval_data1['Interval Start'], interval_data1['Performance'], linestyle='-',
                 label="Performance curve")
        plt.xlabel('Date and Time')
        plt.ylabel('Number of Customers')
        plt.title('Performance Curve for Number of Customer Outages (5-Minute Resolution)')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()

        # Show the plot
        plt.tight_layout()
        plt.show()

        return interval_data1

    def outage_statistics(self, df):
        stats = pd.DataFrame(columns=['Demand Loss (MW)', 'Outage Rate', 'Duration', 'Customer hours'])
        duration = df['time_on'] - df['time_off']
        new = pd.DataFrame({'Demand Loss (MW)': [min(df['Demand Loss (MW)'])], 'Outage Rate': [0], 'Duration': [min(duration)],
                            'Customer hours': [min(df['Customer Minutes'])]})
        stats = pd.concat([stats, new], ignore_index=True)
        new = pd.DataFrame({'Demand Loss (MW)': [max(df['Demand Loss (MW)'])], 'Outage Rate': [0], 'Duration': [max(duration)],
                            'Customer hours': [max(df['Customer Minutes'])]})
        stats = pd.concat([stats, new], ignore_index=True)
        new = pd.DataFrame({'Demand Loss (MW)': [df['Demand Loss (MW)'].mean()], 'Outage Rate': [0], 'Duration': [duration.mean()],
                            'Customer hours': [df['Customer Minutes'].mean()]})
        stats = pd.concat([stats, new], ignore_index=True)
        new = pd.DataFrame({'Demand Loss (MW)': [df['Demand Loss (MW)'].std()], 'Outage Rate': [0], 'Duration': [duration.std()],
                            'Customer hours': [df['Customer Minutes'].std()]})
        stats = pd.concat([stats, new], ignore_index=True)
        return stats

    def non_performance_curve(self, df, wind_data, interval_duration, t_start, t_stop):  # df: Outage Management System data
        # Create a new DataFrame to store the aggregated data
        interval_data = pd.DataFrame(columns=['Interval Start', 'Interval End', 'Total Outages', 'Total Restored'])
        interval_data1 = pd.DataFrame(columns=['Interval Start', 'Total Outages', 'Total Restores', 'Performance'])

        # Iterate through intervals and calculate the total outages in each interval
        current_interval_start = t_start
        total_outages = 0
        total_restores = 0
        current_time = []
        V = []
        dist = []

        while current_interval_start <= t_stop:
            # i = i+1
            # Performance curve calculation
            print(current_interval_start, end=' ')
            current_interval_end = current_interval_start + interval_duration
            total_outage_entries = df[
                (df['time_off'] <= current_interval_end) & (df['time_off'] > current_interval_start)]
            n_out = len(total_outage_entries)
            np_outage = total_outage_entries['Demand Loss (MW)']*total_outage_entries['vul_zone']
            total_outages = total_outages + np_outage.sum()
            total_restore_entries = df[
                (df['time_on'] < current_interval_end) & (df['time_on'] >= current_interval_start)]
            np_restores = total_restore_entries['Demand Loss (MW)']*total_restore_entries['vul_zone']
            total_restores = total_restores + np_restores.sum()

            total_performance_in_interval = total_restores - total_outages

            interval_data = pd.concat([interval_data, pd.DataFrame({
                'Interval Start': [current_interval_start],
                'Interval End': [current_interval_end],
                'Total Outages': [total_outages],
                'Total Restored': [total_restores]
            })], ignore_index=True)
            interval_data1 = pd.concat([interval_data1, pd.DataFrame({
                'Interval Start': [current_interval_start],
                'Total Outages': [total_outages],
                'Total Restores': [total_restores],
                'Performance': total_performance_in_interval
            })], ignore_index=True)
            interval_data1 = pd.concat([interval_data1, pd.DataFrame({
                'Interval Start': [current_interval_end],
                'Total Outages': [total_outages],
                'Total Restores': [total_restores],
                'Performance': total_performance_in_interval
            })], ignore_index=True)

            V_mean = np.mean(total_outage_entries['wind_mag'])
            if math.isnan(V_mean):
                V_current = 20
            else:
                V_current = V_mean
            V.append(V_current)

            current_time.append(current_interval_start)
            V.append(V_current)
            current_time.append(current_interval_end)
            current_interval_start = current_interval_end

        # Create a plot
        plt.figure(figsize=(12, 6))
        plt.plot(interval_data1['Interval Start'], interval_data1['Total Outages'], linestyle='-', label="Outage Curve")
        plt.plot(interval_data1['Interval Start'], interval_data1['Total Restores'], linestyle='-',
                 label="Restore curve")
        plt.plot(interval_data1['Interval Start'], interval_data1['Performance'], linestyle='-',
                 label="Performance curve")
        plt.xlabel('Date and Time')
        plt.ylabel('Number of Customers')
        plt.title('Performance Curve for Number of Customer Outages (5-Minute Resolution)')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()

        # Show the plot
        plt.tight_layout()
        plt.show()

        d = {'Time': current_time, 'Wind speed': V, 'Outage Rate': interval_data1['Performance'].abs()}
        Interpol_per = pd.DataFrame(data=d)
        Interpol_per.to_csv('Wind Interpolated.csv')
        interval_data1.to_csv('Outage Interpolated.csv')

        return interval_data1, Interpol_per



