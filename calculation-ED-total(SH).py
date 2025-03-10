import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to calculate the CDD
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

# Function to calculate the GD based on specific humidity (SH)
def calculate_gram_days(df):
    # Compute daily gram-days using specific humidity (SH) and delta-T (temperature difference)
    # SH is given in kg/kg; need to convert it to gram-days
    gram_days = df['SH[kg/kg]'] * 1000  # Convert to grams
    return gram_days

# Load the temperature and SH data
df_trondheim = pd.read_csv('trondheim_T_SH_SSP2-45.csv', delimiter=';')
df_rome = pd.read_csv('rome_T_SH_SSP2-45.csv', delimiter=';')

# Preprocess the data (ensure SH is loaded and Tmin/Tmax are processed)
df_trondheim.columns = ['datetime', 'year', 'month', 'day', 'Tmin[K]', 'Tmax[K]', 'SH[kg/kg]']
df_rome.columns = ['datetime', 'year', 'month', 'day', 'Tmin[K]', 'Tmax[K]', 'SH[kg/kg]']

df_trondheim['Tmin[K]'] = df_trondheim['Tmin[K]'].str.replace(',', '.').astype(float)
df_trondheim['Tmax[K]'] = df_trondheim['Tmax[K]'].str.replace(',', '.').astype(float)
df_trondheim['SH[kg/kg]'] = df_trondheim['SH[kg/kg]'].str.replace(',', '.').astype(float)
df_rome['Tmin[K]'] = df_rome['Tmin[K]'].str.replace(',', '.').astype(float)
df_rome['Tmax[K]'] = df_rome['Tmax[K]'].str.replace(',', '.').astype(float)
df_rome['SH[kg/kg]'] = df_rome['SH[kg/kg]'].str.replace(',', '.').astype(float)

# Convert temperatures to Celsius
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

# Calculate gram-days for humidity
df_trondheim['Gram_Days'] = calculate_gram_days(df_trondheim)
df_rome['Gram_Days'] = calculate_gram_days(df_rome)

# Group by year for CDD and gram-days
CDD_good_trondheim = df_trondheim.groupby('year')['CDD_Good'].sum()
CDD_average_trondheim = df_trondheim.groupby('year')['CDD_Average'].sum()
CDD_bad_trondheim = df_trondheim.groupby('year')['CDD_Bad'].sum()

Gram_Days_trondheim = df_trondheim.groupby('year')['Gram_Days'].sum()

CDD_good_rome = df_rome.groupby('year')['CDD_Good'].sum()
CDD_average_rome = df_rome.groupby('year')['CDD_Average'].sum()
CDD_bad_rome = df_rome.groupby('year')['CDD_Bad'].sum()

Gram_Days_rome = df_rome.groupby('year')['Gram_Days'].sum()

# U-values and constants
U_value_trondheim = 0.18
U_value_rome = 0.32
A_over_V = 0.5
hours_per_year = 8760

# Define a function to calculate energy demand
def calculate_ed(CDD, U_value):
    return (A_over_V * hours_per_year * U_value * CDD) / 1000  # kWh

# Define a function to calculate humidity energy demand
def calculate_humidity_ed(gram_days, ACH=1.0, k=0.68, L_evap=2257, rho_air=1.225):
    # Evaporation energy (kWh) for dehumidification using gram-days
    return ACH * hours_per_year * k * L_evap * rho_air * (gram_days / 1000) / 1000  # Convert to kWh

# Calculate energy demand for each scenario
def calculate_total_ed(CDD_trondheim, CDD_rome, GD_trondheim, GD_rome, start_year, end_year):
    # Slice the data for the given years
    CDD_trondheim_period = CDD_trondheim.loc[start_year:end_year].sum()
    CDD_rome_period = CDD_rome.loc[start_year:end_year].sum()
    GD_trondheim_period = GD_trondheim.loc[start_year:end_year].sum()
    GD_rome_period = GD_rome.loc[start_year:end_year].sum()

    # Calculate thermal energy demand
    ED_therm_trondheim = calculate_ed(CDD_trondheim_period, U_value_trondheim)
    ED_therm_rome = calculate_ed(CDD_rome_period, U_value_rome)

    # Calculate humidity energy demand
    ED_hum_trondheim = calculate_humidity_ed(GD_trondheim_period)
    ED_hum_rome = calculate_humidity_ed(GD_rome_period)

    # Return total energy demand (thermal + humidity)
    return ED_therm_trondheim + ED_hum_trondheim, ED_therm_rome + ED_hum_rome

# Calculate energy demands for 1 year (2015), 5 years (2015-2020), and 50 years (2015-2065)
ED_tot_good_1_year = calculate_total_ed(CDD_good_trondheim, CDD_good_rome, Gram_Days_trondheim, Gram_Days_rome, 2015, 2015)
ED_tot_average_1_year = calculate_total_ed(CDD_average_trondheim, CDD_average_rome, Gram_Days_trondheim, Gram_Days_rome, 2015, 2015)
ED_tot_bad_1_year = calculate_total_ed(CDD_bad_trondheim, CDD_bad_rome, Gram_Days_trondheim, Gram_Days_rome, 2015, 2015)

ED_tot_good_5_years = calculate_total_ed(CDD_good_trondheim, CDD_good_rome, Gram_Days_trondheim, Gram_Days_rome, 2015, 2020)
ED_tot_average_5_years = calculate_total_ed(CDD_average_trondheim, CDD_average_rome, Gram_Days_trondheim, Gram_Days_rome, 2015, 2020)
ED_tot_bad_5_years = calculate_total_ed(CDD_bad_trondheim, CDD_bad_rome, Gram_Days_trondheim, Gram_Days_rome, 2015, 2020)

ED_tot_good_50_years = calculate_total_ed(CDD_good_trondheim, CDD_good_rome, Gram_Days_trondheim, Gram_Days_rome, 2015, 2065)
ED_tot_average_50_years = calculate_total_ed(CDD_average_trondheim, CDD_average_rome, Gram_Days_trondheim, Gram_Days_rome, 2015, 2065)
ED_tot_bad_50_years = calculate_total_ed(CDD_bad_trondheim, CDD_bad_rome, Gram_Days_trondheim, Gram_Days_rome, 2015, 2065)

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
