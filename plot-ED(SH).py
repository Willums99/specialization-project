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
    gram_days = df['SH[kg/kg]'] * 1000  # Convert to grams
    return gram_days

# Load the temperature and SH data
df_trondheim = pd.read_csv('trondheim_T_SH_SSP2-45.csv', delimiter=';')
df_rome = pd.read_csv('rome_T_SH_SSP2-45.csv', delimiter=';')

# Preprocess the data
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
    return ACH * hours_per_year * k * L_evap * rho_air * (gram_days / 1000) / 1000  # kWh

# Calculate annual energy demand for each scenario
def calculate_annual_total_ed(CDD_trondheim, CDD_rome, GD_trondheim, GD_rome):
    ED_therm_trondheim = calculate_ed(CDD_trondheim, U_value_trondheim)
    ED_therm_rome = calculate_ed(CDD_rome, U_value_rome)
    ED_hum_trondheim = calculate_humidity_ed(GD_trondheim)
    ED_hum_rome = calculate_humidity_ed(GD_rome)
    return ED_therm_trondheim + ED_hum_trondheim, ED_therm_rome + ED_hum_rome

# Lists to store the total energy demand for each year in each scenario
years = list(range(2015, 2066))
ed_good_trondheim, ed_good_rome = [], []
ed_average_trondheim, ed_average_rome = [], []
ed_bad_trondheim, ed_bad_rome = [], []

# Calculate the total energy demand for each year
for year in years:
    # Check if the year exists in all relevant data series
    if year in CDD_good_trondheim.index and year in CDD_good_rome.index and year in Gram_Days_trondheim.index and year in Gram_Days_rome.index:
        ed_good_t, ed_good_r = calculate_annual_total_ed(CDD_good_trondheim.loc[year], CDD_good_rome.loc[year], Gram_Days_trondheim.loc[year], Gram_Days_rome.loc[year])
        ed_average_t, ed_average_r = calculate_annual_total_ed(CDD_average_trondheim.loc[year], CDD_average_rome.loc[year], Gram_Days_trondheim.loc[year], Gram_Days_rome.loc[year])
        ed_bad_t, ed_bad_r = calculate_annual_total_ed(CDD_bad_trondheim.loc[year], CDD_bad_rome.loc[year], Gram_Days_trondheim.loc[year], Gram_Days_rome.loc[year])
        
        ed_good_trondheim.append(ed_good_t)
        ed_good_rome.append(ed_good_r)
        ed_average_trondheim.append(ed_average_t)
        ed_average_rome.append(ed_average_r)
        ed_bad_trondheim.append(ed_bad_t)
        ed_bad_rome.append(ed_bad_r)
    else:
        print(f"Data for the year {year} is missing in one of the datasets, skipping this year.")

# Plot the energy demand for each scenario
plt.figure(figsize=(14, 10))

# Plot for Good scenario
plt.plot(years[:len(ed_good_trondheim)], ed_good_trondheim, label="Trondheim (Good)", color="blue")
plt.plot(years[:len(ed_good_rome)], ed_good_rome, label="Rome (Good)", color="lightblue")

# Plot for Average scenario
plt.plot(years[:len(ed_average_trondheim)], ed_average_trondheim, label="Trondheim (Average)", color="green")
plt.plot(years[:len(ed_average_rome)], ed_average_rome, label="Rome (Average)", color="lightgreen")

# Plot for Bad scenario
plt.plot(years[:len(ed_bad_trondheim)], ed_bad_trondheim, label="Trondheim (Bad)", color="red")
plt.plot(years[:len(ed_bad_rome)], ed_bad_rome, label="Rome (Bad)", color="pink")

# Labels and legend
plt.xlabel("Year")
plt.ylabel("Total Energy Demand (kWh)")
plt.title("Annual Total Energy Demand (Thermal + Humidity) from 2015 to 2065 - SH only")
# Add a red line for the current year 2024
plt.axvline(x=2024, color='red', linestyle='--', linewidth=1.5, label='Current Year 2024')
plt.legend()
plt.grid(True)
plt.show()
