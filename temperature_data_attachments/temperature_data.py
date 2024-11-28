# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 19:02:43 2024

@author: Colin
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# temperature_data_202403060941 
tiles_df = pd.read_csv('temperature_data_202407251302.csv')
# tiles_df = pd.read_csv('temperature_data_202407241358.csv')
# tiles_df = pd.read_csv('temperature_data_202403231209.csv')
# tiles_df2 = pd.read_csv('temperature_data_202402240924.csv')
# tiles_df3 = pd.read_csv('temperature_data_202402241623.csv')
# tiles_df = pd.concat([tiles_df2, tiles_df3])

bad_data_level_upper = 70
bad_data_level_lower = 28
tiles_df['Time'] = pd.to_datetime(tiles_df['Time'])
tiles_df = tiles_df.set_index('Time')
tiles_df[tiles_df > bad_data_level_upper] = np.nan
tiles_df[tiles_df < bad_data_level_lower] = np.nan
tiles_df = tiles_df.reset_index(drop=False)

cols = {
    'Sensor 1': "Tan 1", # "KM White",
    'Sensor 10': "Behr UW + YO",
    'Sensor 6': "Z93",  # Reflective
    'Sensor 7': "Tan Dark Background",  # "Black 4.0",
    'Sensor 4': "KM W Air",
    'Sensor 2': "Tan 2",  # "White 2.0",
    'Sensor 5': "Tropicool",
    'Sensor 9': "Helmet",
    'Sensor 3': "Behr UW",
    'Sensor 8': "Tan 3",  # "KM Bead",
    'Sensor 11': "Tropi Bead",
} # 'temperature_data_202403231209.csv')
cols = {
    'Sensor 1': "Waxhead R", # "KM White",
    'Sensor 10': "BWO + Yittrium Oxide",
    'Sensor 6': "Neutrogena 55 L",  # Reflective
    'Sensor 7': "Neutrogena 55 R 1",  # "Black 4.0",
    'Sensor 4': "Waxhead L 1",
    'Sensor 2': "Blue Lizard",  # "White 2.0",
    'Sensor 5': "Z93",
    'Sensor 9': "Waxhead L 2",
    'Sensor 3': "Behr UW",
    'Sensor 8': "Neutrogena R 2",  # "KM Bead",
    'Sensor 11': "Tropicool Bead",
}  # 'temperature_data_202407241358.csv'
cols = {
    'Sensor 1': "Behr Ultra Pure White R 1", # "KM White",
    'Sensor 10': "BU + Yittrium Oxide",
    'Sensor 6': "Behr Ultra Pure White R 2",  # Reflective
    'Sensor 7': "TO/BO/silica acrylic R 1",  # "Black 4.0",
    'Sensor 4': "mirror spray",
    'Sensor 2': "TO + Thermochromic 25C",  # "White 2.0",
    'Sensor 5': "Z93",
    'Sensor 9': "TO/BO/silica acrylic L",
    'Sensor 3': "Behr Ultra Pure White L",
    'Sensor 8': "TO/BO/silica acrylic R 2",  # "KM Bead",
    'Sensor 11': "Tropicool Bead",
}  # 'temperature_data_202407251302.csv'
tiles_df = tiles_df.rename(columns=cols)

weather_df = pd.read_csv("weather_test.csv")
weather_df = weather_df.rename(columns={weather_df.columns[0]: 'Time'})
weather_df['Time'] = pd.to_datetime(weather_df['Time'])
weather_df['station_tempC'] = weather_df['station_tempf']
weather_df['station_tempC'] = weather_df['station_tempC'].replace("Error", np.nan).astype(float)
weather_df['station_solarradiation'] = weather_df['station_solarradiation'].replace("Error", np.nan).astype(float)
weather_df['station_uv'] = weather_df['station_uv'].replace("Error", np.nan).astype(float)
weather_df['station_windspeedmph'] = weather_df['station_windspeedmph'].replace("Error", np.nan).astype(float)
weather_df['station_windspeedmph_ravg'] = weather_df['station_windspeedmph'].rolling(30).mean()
weather_df['station_solarradiation_scaled'] = weather_df['station_solarradiation'] / weather_df['station_solarradiation'].max()

tiles_df['Time_min'] = tiles_df['Time'].dt.round('T')
weather_df['Time_min'] = weather_df['Time'].dt.round('T')
merged_df = pd.merge_asof(tiles_df, weather_df, on='Time_min', direction='nearest', tolerance=pd.Timedelta('1T'))
cols = ['Time_min', 'station_tempC', 'station_winddir', 'station_windspeedmph', 'station_windgustmph', 'station_uv', 'station_solarradiation_scaled']
merged_df = tiles_df.merge(weather_df[cols], on='Time_min', how='left')
merged_df = merged_df.set_index('Time')

merged_df.columns
merged_df_num = merged_df.select_dtypes("number")

merged_df_num.plot()
plt.ylabel("Temperature °C")
plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
plt.savefig("tile_temperatures_{pd.Timestamp.utcnow().strftime('%Y%m%d')}.png", dpi=300, bbox_inches="tight")

merged_df_num["Hour"] = merged_df_num.index.hour

use_cols = [x for x in merged_df_num.columns if ("station" not in x) and ("Hour" not in x) and ("Helmet" not in x) and ("Black" not in x)]
merged_df_num_plot = merged_df_num[(merged_df_num["Hour"] >= 9) & (merged_df_num["Hour"] < 16)]
# merged_df_num_plot = merged_df_num_plot - (merged_df_num_plot.ffill()[merged_df_num_plot.index == merged_df_num_plot.index[66]]).to_numpy()
merged_df_num_plot = merged_df_num_plot - (merged_df_num_plot.ffill()[merged_df_num_plot.index == merged_df_num_plot.index[22]]).to_numpy()
merged_df_num_plot[use_cols].drop(columns="Waxhead L 2", errors='ignore').plot()
plt.ylabel("Temperature °C adjusted for 13:27")
plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
plt.savefig(f"tile_temperatures_{pd.Timestamp.utcnow().strftime('%Y%m%d')}_2.png", dpi=300, bbox_inches="tight")



