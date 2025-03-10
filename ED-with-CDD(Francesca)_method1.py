import pandas as pd
import numpy as np

# Francesca's Method 1 for SH calculation
def calculate_sh_method1(T, RH):
    # Convert T in Celsius and RH in percentage to SH in g/kg
    SH = 38.015 * (10 ** ((7.65 * T) / (243.12 + T)) * RH) / (1013.25 - (0.06112 * 10 ** ((7.65 * T) / (243.12 + T)) * RH))
    return SH  # in g/kg

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

# Define RH values for each scenario
RH_good = 0.30  # 40% for 'Good' scenario
RH_average = 0.50  # 50% for 'Average' scenario
RH_bad = 0.70  # 70% for 'Bad' scenario

# Calculate SH for each scenario using Method 1
df_trondheim['SH_Good'] = calculate_sh_method1(df_trondheim['Tavg[C]'], RH_good)
df_trondheim['SH_Average'] = calculate_sh_method1(df_trondheim['Tavg[C]'], RH_average)
df_trondheim['SH_Bad'] = calculate_sh_method1(df_trondheim['Tavg[C]'], RH_bad)

df_rome['SH_Good'] = calculate_sh_method1(df_rome['Tavg[C]'], RH_good)
df_rome['SH_Average'] = calculate_sh_method1(df_rome['Tavg[C]'], RH_average)
df_rome['SH_Bad'] = calculate_sh_method1(df_rome['Tavg[C]'], RH_bad)

# Calculate CDD for each scenario
df_trondheim['CDD_Good'] = calculate_cdd(df_trondheim, 2)
df_trondheim['CDD_Average'] = calculate_cdd(df_trondheim, 7)
df_trondheim['CDD_Bad'] = calculate_cdd(df_trondheim, 15)

df_rome['CDD_Good'] = calculate_cdd(df_rome, 2)
df_rome['CDD_Average'] = calculate_cdd(df_rome, 7)
df_rome['CDD_Bad'] = calculate_cdd(df_rome, 15)

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
A_over_V = 1
hours_per_year = 8760

# Define function to calculate energy demand
def calculate_ed(CDD, U_value):
    return (A_over_V * hours_per_year * U_value * CDD) / 1000  # kWh

# Define function to calculate humidity energy demand based on SH
def calculate_humidity_ed(SH, ACH=1.0, k=2.78*10**(-7), L_evap=2257, rho_air=1.225):
    return ACH * hours_per_year * k * L_evap * rho_air * SH / 1000  # kWh

# Function to calculate total energy demand
def calculate_total_ed_period(CDD_trondheim, CDD_rome, SH_trondheim, SH_rome, start_year, end_year):
    CDD_trondheim_period = CDD_trondheim.loc[start_year:end_year].sum()
    CDD_rome_period = CDD_rome.loc[start_year:end_year].sum()
    SH_trondheim_sum = SH_trondheim.loc[start_year:end_year].sum()  
    SH_rome_sum = SH_rome.loc[start_year:end_year].sum()  

    ED_therm_trondheim = calculate_ed(CDD_trondheim_period, U_value_trondheim)
    ED_therm_rome = calculate_ed(CDD_rome_period, U_value_rome)

    ED_hum_trondheim = calculate_humidity_ed(SH_trondheim_sum)
    ED_hum_rome = calculate_humidity_ed(SH_rome_sum)

    return ED_therm_trondheim + ED_hum_trondheim, ED_therm_rome + ED_hum_rome


# Calculate energy demands for 1 year (2015), 5 years (2015-2020), and 50 years (2015-2065)
ED_tot_good_1_year = calculate_total_ed_period(CDD_good_trondheim, CDD_good_rome, SH_good_trondheim, SH_good_rome, 2015, 2015)
ED_tot_average_1_year = calculate_total_ed_period(CDD_average_trondheim, CDD_average_rome, SH_average_trondheim, SH_average_rome, 2015, 2015)
ED_tot_bad_1_year = calculate_total_ed_period(CDD_bad_trondheim, CDD_bad_rome, SH_bad_trondheim, SH_bad_rome, 2015, 2015)

ED_tot_good_5_years = calculate_total_ed_period(CDD_good_trondheim, CDD_good_rome, SH_good_trondheim, SH_good_rome, 2015, 2020)
ED_tot_average_5_years = calculate_total_ed_period(CDD_average_trondheim, CDD_average_rome, SH_average_trondheim, SH_average_rome, 2015, 2020)
ED_tot_bad_5_years = calculate_total_ed_period(CDD_bad_trondheim, CDD_bad_rome, SH_bad_trondheim, SH_bad_rome, 2015, 2020)

ED_tot_good_50_years = calculate_total_ed_period(CDD_good_trondheim, CDD_good_rome, SH_good_trondheim, SH_good_rome, 2015, 2065)
ED_tot_average_50_years = calculate_total_ed_period(CDD_average_trondheim, CDD_average_rome, SH_average_trondheim, SH_average_rome, 2015, 2065)
ED_tot_bad_50_years = calculate_total_ed_period(CDD_bad_trondheim, CDD_bad_rome, SH_bad_trondheim, SH_bad_rome, 2015, 2065)

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

