import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Constants for specific humidity calculation
P = 1013.25  # Atmospheric pressure in hPa (sea level)

# Function to calculate the saturation vapor pressure (es) in hPa
def calculate_saturation_vapor_pressure(T):
    return 6.112 * np.exp((17.67 * T) / (T + 243.5))

# Function to calculate specific humidity (SH) from T and RH
def calculate_specific_humidity(T, RH):
    es = calculate_saturation_vapor_pressure(T)  # Saturation vapor pressure in hPa
    ea = (RH / 100) * es  # Actual vapor pressure in hPa
    SH = (0.622 * ea) / (P - (0.378 * ea))  # Specific humidity in kg/kg
    return SH

# Define the temperature (T) and RH thresholds for the three scenarios
scenarios = {
    'Good': {'T': 2, 'RH': 40},
    'Average': {'T': 7, 'RH': 50},
    'Bad': {'T': 15, 'RH': 60}
}

# Calculate specific humidity (SH) for each scenario
for scenario, values in scenarios.items():
    T = values['T']
    RH = values['RH']
    SH = calculate_specific_humidity(T, RH)
    scenarios[scenario]['SH'] = SH
    print(f"Specific Humidity for {scenario} scenario: {SH:.6f} kg/kg")

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

# Load the temperature and specific humidity data
df_trondheim = pd.read_csv('trondheim_T_SH_SSP2-45.csv', delimiter=';')
df_rome = pd.read_csv('rome_T_SH_SSP2-45.csv', delimiter=';')

# Preprocess the data to handle commas in the SH field
df_trondheim.columns = ['datetime', 'year', 'month', 'day', 'Tmin[K]', 'Tmax[K]', 'SH[kg/kg]']
df_rome.columns = ['datetime', 'year', 'month', 'day', 'Tmin[K]', 'Tmax[K]', 'SH[kg/kg]']

df_trondheim['Tmin[K]'] = df_trondheim['Tmin[K]'].str.replace(',', '.').astype(float)
df_trondheim['Tmax[K]'] = df_trondheim['Tmax[K]'].str.replace(',', '.').astype(float)
df_rome['Tmin[K]'] = df_rome['Tmin[K]'].str.replace(',', '.').astype(float)
df_rome['Tmax[K]'] = df_rome['Tmax[K]'].str.replace(',', '.').astype(float)

# Convert SH to proper float by replacing commas with periods
df_trondheim['SH[kg/kg]'] = df_trondheim['SH[kg/kg]'].str.replace(',', '.').astype(float)
df_rome['SH[kg/kg]'] = df_rome['SH[kg/kg]'].str.replace(',', '.').astype(float)

# Convert Kelvin to Celsius
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
def calculate_humidity_ed(SH_trondheim, SH_rome, start_year, end_year, ACH=1.0, k=0.68, L_evap=2257, rho_air=1.225, GD=5.0):
    # Slicing SH data to the correct period and calculating mean specific humidity
    SH_trondheim_mean = SH_trondheim  # Already averaged in the calling function
    SH_rome_mean = SH_rome

    # Humidity energy demand (use SH data)
    ED_hum_trondheim = ACH * hours_per_year * k * L_evap * rho_air * SH_trondheim_mean * GD / 1000
    ED_hum_rome = ACH * hours_per_year * k * L_evap * rho_air * SH_rome_mean * GD / 1000

    return ED_hum_trondheim, ED_hum_rome

# Combine thermal and humidification energy demand
def calculate_total_ed_period(CDD_trondheim, CDD_rome, SH_trondheim, SH_rome, start_year, end_year):
    # Slice the data for the given years
    CDD_trondheim_period = CDD_trondheim.loc[start_year:end_year].sum()  # Sum the CDDs over the period
    CDD_rome_period = CDD_rome.loc[start_year:end_year].sum()

    # Sum the SH (specific humidity) values over the period
    SH_trondheim_period = SH_trondheim.loc[start_year:end_year].mean()  # Take the average SH for the period
    SH_rome_period = SH_rome.loc[start_year:end_year].mean()

    # Calculate thermal energy demand separately for Trondheim and Rome
    ED_therm_trondheim = calculate_ed(CDD_trondheim_period, U_value_trondheim)
    ED_therm_rome = calculate_ed(CDD_rome_period, U_value_rome)

    # Calculate humidity energy demand separately for Trondheim and Rome
    # Pass start_year and end_year as arguments
    ED_hum_trondheim, ED_hum_rome = calculate_humidity_ed(SH_trondheim_period, SH_rome_period, start_year, end_year)

    # Total energy demand = thermal energy + humidity energy
    return ED_therm_trondheim + ED_hum_trondheim, ED_therm_rome + ED_hum_rome


# Specific Humidity for each scenario (example, make sure this is calculated earlier in your code)
SH_good_trondheim = df_trondheim['SH[kg/kg]']  # Replace with actual SH data for Good scenario
SH_good_rome = df_rome['SH[kg/kg]']  # Replace with actual SH data for Good scenario

SH_average_trondheim = df_trondheim['SH[kg/kg]']  # Replace with actual SH data for Average scenario
SH_average_rome = df_rome['SH[kg/kg]']  # Replace with actual SH data for Average scenario

SH_bad_trondheim = df_trondheim['SH[kg/kg]']  # Replace with actual SH data for Bad scenario
SH_bad_rome = df_rome['SH[kg/kg]']  # Replace with actual SH data for Bad scenario

# Calculate energy demands for Good scenario
ED_tot_good_1_year = calculate_total_ed_period(CDD_good_trondheim, CDD_good_rome, SH_good_trondheim, SH_good_rome, 2015, 2015)
ED_tot_good_5_years = calculate_total_ed_period(CDD_good_trondheim, CDD_good_rome, SH_good_trondheim, SH_good_rome, 2015, 2020)
ED_tot_good_50_years = calculate_total_ed_period(CDD_good_trondheim, CDD_good_rome, SH_good_trondheim, SH_good_rome, 2015, 2065)

# Calculate energy demands for Average scenario
ED_tot_average_1_year = calculate_total_ed_period(CDD_average_trondheim, CDD_average_rome, SH_average_trondheim, SH_average_rome, 2015, 2015)
ED_tot_average_5_years = calculate_total_ed_period(CDD_average_trondheim, CDD_average_rome, SH_average_trondheim, SH_average_rome, 2015, 2020)
ED_tot_average_50_years = calculate_total_ed_period(CDD_average_trondheim, CDD_average_rome, SH_average_trondheim, SH_average_rome, 2015, 2065)

# Calculate energy demands for Bad scenario
ED_tot_bad_1_year = calculate_total_ed_period(CDD_bad_trondheim, CDD_bad_rome, SH_bad_trondheim, SH_bad_rome, 2015, 2015)
ED_tot_bad_5_years = calculate_total_ed_period(CDD_bad_trondheim, CDD_bad_rome, SH_bad_trondheim, SH_bad_rome, 2015, 2020)
ED_tot_bad_50_years = calculate_total_ed_period(CDD_bad_trondheim, CDD_bad_rome, SH_bad_trondheim, SH_bad_rome, 2015, 2065)

# Print the results for the Good scenario
print(f"Total Energy Demand for 1 Year (Good Scenario):\nNorway: {ED_tot_good_1_year[0]:.2f} kWh, Italy: {ED_tot_good_1_year[1]:.2f} kWh")
print(f"Total Energy Demand for 5 Years (Good Scenario):\nNorway: {ED_tot_good_5_years[0]:.2f} kWh, Italy: {ED_tot_good_5_years[1]:.2f} kWh")
print(f"Total Energy Demand for 50 Years (Good Scenario):\nNorway: {ED_tot_good_50_years[0]:.2f} kWh, Italy: {ED_tot_good_50_years[1]:.2f} kWh")

# Print the results for the Average scenario
print(f"Total Energy Demand for 1 Year (Average Scenario):\nNorway: {ED_tot_average_1_year[0]:.2f} kWh, Italy: {ED_tot_average_1_year[1]:.2f} kWh")
print(f"Total Energy Demand for 5 Years (Average Scenario):\nNorway: {ED_tot_average_5_years[0]:.2f} kWh, Italy: {ED_tot_average_5_years[1]:.2f} kWh")
print(f"Total Energy Demand for 50 Years (Average Scenario):\nNorway: {ED_tot_average_50_years[0]:.2f} kWh, Italy: {ED_tot_average_50_years[1]:.2f} kWh")

# Print the results for the Bad scenario
print(f"Total Energy Demand for 1 Year (Bad Scenario):\nNorway: {ED_tot_bad_1_year[0]:.2f} kWh, Italy: {ED_tot_bad_1_year[1]:.2f} kWh")
print(f"Total Energy Demand for 5 Years (Bad Scenario):\nNorway: {ED_tot_bad_5_years[0]:.2f} kWh, Italy: {ED_tot_bad_5_years[1]:.2f} kWh")
print(f"Total Energy Demand for 50 Years (Bad Scenario):\nNorway: {ED_tot_bad_50_years[0]:.2f} kWh, Italy: {ED_tot_bad_50_years[1]:.2f} kWh")
