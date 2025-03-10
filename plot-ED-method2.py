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

# Function to calculate specific humidity (Method 2) based on T in °C and RH in [-]
def calculate_specific_humidity_method_2(T, RH):
    esat = 0.61094 * np.exp((17.625 * T) / (243.04 + T))  # saturation vapor pressure in kPa
    SH = (622 * RH * esat) / (101.325 - (RH * esat))  # specific humidity in g/kg
    return SH / 1000  # Convert to kg/kg

# Load the temperature data
df_trondheim = pd.read_csv('trondheim_temperature_SSP2-45.csv', delimiter=';')
df_rome = pd.read_csv('rome_temperature_SSP2-45.csv', delimiter=';')

# Preprocess the data (ensure Tmin/Tmax are processed)
df_trondheim.columns = ['datetime', 'year', 'month', 'day', 'Tmin[K]', 'Tmax[K]']
df_rome.columns = ['datetime', 'year', 'month', 'day', 'Tmin[K]', 'Tmax[K]']

df_trondheim['Tmin[K]'] = df_trondheim['Tmin[K]'].str.replace(',', '.').astype(float)
df_trondheim['Tmax[K]'] = df_trondheim['Tmax[K]'].str.replace(',', '.').astype(float)
df_rome['Tmin[K]'] = df_rome['Tmin[K]'].str.replace(',', '.').astype(float)
df_rome['Tmax[K]'] = df_rome['Tmax[K]'].str.replace(',', '.').astype(float)

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

# Define Relative Humidity values for each scenario
RH_good = 0.30  # 30% for Good scenario
RH_average = 0.50  # 50% for Average scenario
RH_bad = 0.70  # 70% for Bad scenario

# Calculate specific humidity using Method 2
df_trondheim['SH_Good'] = calculate_specific_humidity_method_2(df_trondheim['Tavg[C]'], RH_good)
df_trondheim['SH_Average'] = calculate_specific_humidity_method_2(df_trondheim['Tavg[C]'], RH_average)
df_trondheim['SH_Bad'] = calculate_specific_humidity_method_2(df_trondheim['Tavg[C]'], RH_bad)

df_rome['SH_Good'] = calculate_specific_humidity_method_2(df_rome['Tavg[C]'], RH_good)
df_rome['SH_Average'] = calculate_specific_humidity_method_2(df_rome['Tavg[C]'], RH_average)
df_rome['SH_Bad'] = calculate_specific_humidity_method_2(df_rome['Tavg[C]'], RH_bad)

# Group by year for CDD and SH
CDD_good_trondheim = df_trondheim.groupby('year')['CDD_Good'].sum()
CDD_average_trondheim = df_trondheim.groupby('year')['CDD_Average'].sum()
CDD_bad_trondheim = df_trondheim.groupby('year')['CDD_Bad'].sum()

SH_good_trondheim = df_trondheim.groupby('year')['SH_Good'].mean()
SH_average_trondheim = df_trondheim.groupby('year')['SH_Average'].mean()
SH_bad_trondheim = df_trondheim.groupby('year')['SH_Bad'].mean()

CDD_good_rome = df_rome.groupby('year')['CDD_Good'].sum()
CDD_average_rome = df_rome.groupby('year')['CDD_Average'].sum()
CDD_bad_rome = df_rome.groupby('year')['CDD_Bad'].sum()

SH_good_rome = df_rome.groupby('year')['SH_Good'].mean()
SH_average_rome = df_rome.groupby('year')['SH_Average'].mean()
SH_bad_rome = df_rome.groupby('year')['SH_Bad'].mean()

# U-values and constants
U_value_trondheim = 0.18
U_value_rome = 0.32
A_over_V = 0.5
hours_per_year = 8760

# Define function to calculate energy demand
def calculate_ed(CDD, U_value):
    return (A_over_V * hours_per_year * U_value * CDD) / 1000  # kWh

# Define function to calculate humidity energy demand based on SH
def calculate_humidity_ed(SH, ACH=1.0, k=0.68, L_evap=2257, rho_air=1.225):
    return ACH * hours_per_year * k * L_evap * rho_air * SH / 1000  # kWh

# Function to calculate total energy demand
def calculate_total_ed_period(CDD_trondheim, CDD_rome, SH_trondheim, SH_rome, start_year, end_year):
    CDD_trondheim_period = CDD_trondheim.loc[start_year:end_year].sum()
    CDD_rome_period = CDD_rome.loc[start_year:end_year].sum()
    SH_trondheim_mean = SH_trondheim.loc[start_year:end_year].mean()
    SH_rome_mean = SH_rome.loc[start_year:end_year].mean()

    ED_therm_trondheim = calculate_ed(CDD_trondheim_period, U_value_trondheim)
    ED_therm_rome = calculate_ed(CDD_rome_period, U_value_rome)

    ED_hum_trondheim = calculate_humidity_ed(SH_trondheim_mean)
    ED_hum_rome = calculate_humidity_ed(SH_rome_mean)

    return ED_therm_trondheim + ED_hum_trondheim, ED_therm_rome + ED_hum_rome

# Plotting the results over time for the 50-year period
years = list(range(2015, 2066))
ed_good_trondheim, ed_good_rome = [], []
ed_average_trondheim, ed_average_rome = [], []
ed_bad_trondheim, ed_bad_rome = [], []

# Calculate annual energy demand for plotting
for year in years:
    ed_good_t, ed_good_r = calculate_total_ed_period(CDD_good_trondheim, CDD_good_rome, SH_good_trondheim, SH_good_rome, year, year)
    ed_average_t, ed_average_r = calculate_total_ed_period(CDD_average_trondheim, CDD_average_rome, SH_average_trondheim, SH_average_rome, year, year)
    ed_bad_t, ed_bad_r = calculate_total_ed_period(CDD_bad_trondheim, CDD_bad_rome, SH_bad_trondheim, SH_bad_rome, year, year)
    
    ed_good_trondheim.append(ed_good_t)
    ed_good_rome.append(ed_good_r)
    ed_average_trondheim.append(ed_average_t)
    ed_average_rome.append(ed_average_r)
    ed_bad_trondheim.append(ed_bad_t)
    ed_bad_rome.append(ed_bad_r)

# Plot the energy demand for each scenario
plt.figure(figsize=(14, 10))

# Plot for Good scenario
plt.plot(years, ed_good_trondheim, label="Trondheim (Good)", color="blue")
plt.plot(years, ed_good_rome, label="Rome (Good)", color="lightblue")

# Plot for Average scenario
plt.plot(years, ed_average_trondheim, label="Trondheim (Average)", color="green")
plt.plot(years, ed_average_rome, label="Rome (Average)", color="lightgreen")

# Plot for Bad scenario
plt.plot(years, ed_bad_trondheim, label="Trondheim (Bad)", color="red")
plt.plot(years, ed_bad_rome, label="Rome (Bad)", color="pink")

# Labels and legend
plt.xlabel("Year")
plt.ylabel("Total Energy Demand (kWh)")
plt.title("Annual Total Energy Demand (Thermal + Humidity) from 2015 to 2065 - Method 2")
# Add a red line for the current year 2024
plt.axvline(x=2024, color='red', linestyle='--', linewidth=1.5, label='Current Year 2024')
plt.legend()
plt.grid(True)
plt.show()
