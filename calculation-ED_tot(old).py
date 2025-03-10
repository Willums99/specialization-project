import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to calculate the CDD (as previously done)
def calculate_cdd(df, T_base):
    CDD = np.zeros(len(df))
    for i in range(len(df)):
        Tmin = df.loc[i, 'Tmin[C]']
        Tmax = df.loc[i, 'Tmax[C]']
        Tavg = df.loc[i, 'Tavg[C]']
        
        if Tmax <= T_base:
            CDD[i] = 0
        elif Tavg <= T_base < Tmax:
            CDD[i] = (Tmax - T_base) / 4
        elif Tmin < T_base < Tavg:
            CDD[i] = ((Tmax - T_base) / 2) - ((T_base - Tmin) / 4)
        elif Tmin >= T_base:
            CDD[i] = Tavg - T_base
    
    return CDD

# Load the temperature data
df_trondheim = pd.read_csv('trondheim_temperature_SSP2-45.csv', delimiter=';')
df_rome = pd.read_csv('rome_temperature_SSP2-45.csv', delimiter=';')

# Preprocess the data
df_trondheim.columns = ['datetime', 'year', 'month', 'day', 'Tmin[K]', 'Tmax[K]']
df_rome.columns = ['datetime', 'year', 'month', 'day', 'Tmin[K]', 'Tmax[K]']

df_trondheim['Tmin[K]'] = df_trondheim['Tmin[K]'].str.replace(',', '.').astype(float)
df_trondheim['Tmax[K]'] = df_trondheim['Tmax[K]'].str.replace(',', '.').astype(float)
df_rome['Tmin[K]'] = df_rome['Tmin[K]'].str.replace(',', '.').astype(float)
df_rome['Tmax[K]'] = df_rome['Tmax[K]'].str.replace(',', '.').astype(float)

df_trondheim['Tmin[C]'] = df_trondheim['Tmin[K]'] - 273.15
df_trondheim['Tmax[C]'] = df_trondheim['Tmax[K]'] - 273.15
df_rome['Tmin[C]'] = df_rome['Tmin[K]'] - 273.15
df_rome['Tmax[C]'] = df_rome['Tmax[K]'] - 273.15

df_trondheim['Tavg[C]'] = (df_trondheim['Tmin[C]'] + df_trondheim['Tmax[C]']) / 2
df_rome['Tavg[C]'] = (df_rome['Tmin[C]'] + df_rome['Tmax[C]']) / 2

# Calculate CDD for each scenario
df_trondheim['CDD_Good'] = calculate_cdd(df_trondheim, 2)
df_trondheim['CDD_Average'] = calculate_cdd(df_trondheim, 7)
df_trondheim['CDD_Bad'] = calculate_cdd(df_trondheim, 15)

df_rome['CDD_Good'] = calculate_cdd(df_rome, 2)
df_rome['CDD_Average'] = calculate_cdd(df_rome, 7)
df_rome['CDD_Bad'] = calculate_cdd(df_rome, 15)

# Group by year
CDD_good_trondheim = df_trondheim.groupby('year')['CDD_Good'].sum()
CDD_average_trondheim = df_trondheim.groupby('year')['CDD_Average'].sum()
CDD_bad_trondheim = df_trondheim.groupby('year')['CDD_Bad'].sum()

CDD_good_rome = df_rome.groupby('year')['CDD_Good'].sum()
CDD_average_rome = df_rome.groupby('year')['CDD_Average'].sum()
CDD_bad_rome = df_rome.groupby('year')['CDD_Bad'].sum()

# U-values and constants
U_value_trondheim = 0.18
U_value_rome = 0.32
A_over_V = 0.5
hours_per_year = 8760

# Define a function to calculate energy demand
def calculate_ed(CDD, U_value):
    return (A_over_V * hours_per_year * U_value * CDD) / 1000  # kWh

# Calculate humidification energy demand
def calculate_humidity_ed(RH_trondheim, RH_rome, start_year, end_year, ACH=1.0, k=0.68, L_evap=2257, rho_air=1.225, GD=5.0):
    # Slicing RH data to the correct period and calculating mean relative humidity
    # Ensure we extract year properly for slicing
    RH_trondheim_mean = RH_trondheim.loc[df_trondheim['year'].between(start_year, end_year)].mean()
    RH_rome_mean = RH_rome.loc[df_rome['year'].between(start_year, end_year)].mean()

    # Calculate humidification energy demand
    ED_hum_trondheim = ACH * hours_per_year * k * L_evap * rho_air * (RH_trondheim_mean / 100) * GD / 1000
    ED_hum_rome = ACH * hours_per_year * k * L_evap * rho_air * (RH_rome_mean / 100) * GD / 1000

    return ED_hum_trondheim, ED_hum_rome

# Function to calculate the energy demand over a given period
def calculate_ed_period(CDD_trondheim, CDD_rome, start_year, end_year):
    # Slice the data for the given years
    CDD_trondheim_period = CDD_trondheim.loc[start_year:end_year].sum()
    CDD_rome_period = CDD_rome.loc[start_year:end_year].sum()
    
    # Calculate thermal energy demand
    ED_trondheim = calculate_ed(CDD_trondheim_period, U_value_trondheim)
    ED_rome = calculate_ed(CDD_rome_period, U_value_rome)
    
    return ED_trondheim, ED_rome

# Combine thermal and humidification energy demand
def calculate_total_ed(CDD_trondheim, CDD_rome, RH_trondheim, RH_rome, start_year, end_year):
    # Calculate thermal ED
    ED_therm_trondheim, ED_therm_rome = calculate_ed_period(CDD_trondheim, CDD_rome, start_year, end_year)
    
    # Calculate humidity ED
    ED_hum_trondheim, ED_hum_rome = calculate_humidity_ed(RH_trondheim, RH_rome, start_year, end_year)
    
    # Total ED
    return ED_therm_trondheim + ED_hum_trondheim, ED_therm_rome + ED_hum_rome

# Placeholder RH values (random for now, replace with real data)
df_trondheim['RH_Good'] = np.random.uniform(30, 50, len(df_trondheim))
df_trondheim['RH_Average'] = np.random.uniform(40, 60, len(df_trondheim))
df_trondheim['RH_Bad'] = np.random.uniform(50, 70, len(df_trondheim))
df_rome['RH_Good'] = np.random.uniform(30, 50, len(df_rome))
df_rome['RH_Average'] = np.random.uniform(40, 60, len(df_rome))
df_rome['RH_Bad'] = np.random.uniform(50, 70, len(df_rome))

# Calculate energy demands for 1 year (2015), 5 years (2015-2020), and 50 years (2015-2065)
ED_tot_good_1_year = calculate_total_ed(CDD_good_trondheim, CDD_good_rome, df_trondheim['RH_Good'], df_rome['RH_Good'], 2015, 2015)
ED_tot_average_1_year = calculate_total_ed(CDD_average_trondheim, CDD_average_rome, df_trondheim['RH_Average'], df_rome['RH_Average'], 2015, 2015)
ED_tot_bad_1_year = calculate_total_ed(CDD_bad_trondheim, CDD_bad_rome, df_trondheim['RH_Bad'], df_rome['RH_Bad'], 2015, 2015)

ED_tot_good_5_years = calculate_total_ed(CDD_good_trondheim, CDD_good_rome, df_trondheim['RH_Good'], df_rome['RH_Good'], 2015, 2020)
ED_tot_average_5_years = calculate_total_ed(CDD_average_trondheim, CDD_average_rome, df_trondheim['RH_Average'], df_rome['RH_Average'], 2015, 2020)
ED_tot_bad_5_years = calculate_total_ed(CDD_bad_trondheim, CDD_bad_rome, df_trondheim['RH_Bad'], df_rome['RH_Bad'], 2015, 2020)

ED_tot_good_50_years = calculate_total_ed(CDD_good_trondheim, CDD_good_rome, df_trondheim['RH_Good'], df_rome['RH_Good'], 2015, 2065)
ED_tot_average_50_years = calculate_total_ed(CDD_average_trondheim, CDD_average_rome, df_trondheim['RH_Average'], df_rome['RH_Average'], 2015, 2065)
ED_tot_bad_50_years = calculate_total_ed(CDD_bad_trondheim, CDD_bad_rome, df_trondheim['RH_Bad'], df_rome['RH_Bad'], 2015, 2065)

# Print the results
print(f"Total Energy Demand (Thermal + Humidity) for 1 Year (Good Scenario):\nNorway: {ED_tot_good_1_year[0]:.2f} kWh, Italy: {ED_tot_good_1_year[1]:.2f} kWh")
print(f"Total Energy Demand (Thermal + Humidity) for 1 Year (Average Scenario):\nNorway: {ED_tot_average_1_year[0]:.2f} kWh, Italy: {ED_tot_average_1_year[1]:.2f} kWh")
print(f"Total Energy Demand (Thermal + Humidity) for 1 Year (Bad Scenario):\nNorway: {ED_tot_bad_1_year[0]:.2f} kWh, Italy: {ED_tot_bad_1_year[1]:.2f} kWh")

print(f"\nTotal Energy Demand (Thermal + Humidity) for 5 Years (Good Scenario):\nNorway: {ED_tot_good_5_years[0]:.2f} kWh, Italy: {ED_tot_good_5_years[1]:.2f} kWh")
print(f"Total Energy Demand (Thermal + Humidity) for 5 Years (Average Scenario):\nNorway: {ED_tot_average_5_years[0]:.2f} kWh, Italy: {ED_tot_average_5_years[1]:.2f} kWh")
print(f"Total Energy Demand (Thermal + Humidity) for 5 Years (Bad Scenario):\nNorway: {ED_tot_bad_5_years[0]:.2f} kWh, Italy: {ED_tot_bad_5_years[1]:.2f} kWh")

print(f"\nTotal Energy Demand (Thermal + Humidity) for 50 Years (Good Scenario):\nNorway: {ED_tot_good_50_years[0]:.2f} kWh, Italy: {ED_tot_good_50_years[1]:.2f} kWh")
print(f"Total Energy Demand (Thermal + Humidity) for 50 Years (Average Scenario):\nNorway: {ED_tot_average_50_years[0]:.2f} kWh, Italy: {ED_tot_average_50_years[1]:.2f} kWh")
print(f"Total Energy Demand (Thermal + Humidity) for 50 Years (Bad Scenario):\nNorway: {ED_tot_bad_50_years[0]:.2f} kWh, Italy: {ED_tot_bad_50_years[1]:.2f} kWh")