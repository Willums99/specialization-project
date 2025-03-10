import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load temperature data for Trondheim and Rome
df_trondheim = pd.read_csv('trondheim_temperature_SSP2-45.csv', delimiter=';')
df_rome = pd.read_csv('rome_temperature_SSP2-45.csv', delimiter=';')

# Rename columns for easier reference
df_trondheim.columns = ['datetime', 'year', 'month', 'day', 'Tmin[K]', 'Tmax[K]']
df_rome.columns = ['datetime', 'year', 'month', 'day', 'Tmin[K]', 'Tmax[K]']

# Convert Tmin and Tmax columns to numeric, coercing invalid entries to NaN
df_trondheim['Tmin[K]'] = pd.to_numeric(df_trondheim['Tmin[K]'].str.replace(',', '.'), errors='coerce')
df_trondheim['Tmax[K]'] = pd.to_numeric(df_trondheim['Tmax[K]'].str.replace(',', '.'), errors='coerce')
df_rome['Tmin[K]'] = pd.to_numeric(df_rome['Tmin[K]'].str.replace(',', '.'), errors='coerce')
df_rome['Tmax[K]'] = pd.to_numeric(df_rome['Tmax[K]'].str.replace(',', '.'), errors='coerce')

# Drop rows with NaN values
df_trondheim.dropna(subset=['Tmin[K]', 'Tmax[K]'], inplace=True)
df_rome.dropna(subset=['Tmin[K]', 'Tmax[K]'], inplace=True)

# Convert temperature from Kelvin to Celsius
df_trondheim['Tmin[C]'] = df_trondheim['Tmin[K]'] - 273.15
df_trondheim['Tmax[C]'] = df_trondheim['Tmax[K]'] - 273.15
df_rome['Tmin[C]'] = df_rome['Tmin[K]'] - 273.15
df_rome['Tmax[C]'] = df_rome['Tmax[K]'] - 273.15

# Calculate average temperature for each day
df_trondheim['Tavg[C]'] = (df_trondheim['Tmin[C]'] + df_trondheim['Tmax[C]']) / 2
df_rome['Tavg[C]'] = (df_rome['Tmin[C]'] + df_rome['Tmax[C]']) / 2

# Set the target storage temperature for each scenario
target_temp_good = 2  # Good scenario: target inside temperature < 2°C
target_temp_average = 7  # Average scenario: target inside temperature < 7°C
target_temp_bad = 15  # Bad scenario: target inside temperature < 15°C

# Adjust the degree days calculation based on the difference between outside and inside temperatures
def calculate_degree_days_adjusted(df, target_temp_good, target_temp_average, target_temp_bad):
    df['DegreeDays_Good'] = (target_temp_good - df['Tavg[C]']).clip(lower=0)  # Only calculate cooling days
    df['DegreeDays_Average'] = (target_temp_average - df['Tavg[C]']).clip(lower=0) - df['DegreeDays_Good']  # Subtract from Good
    df['DegreeDays_Bad'] = (target_temp_bad - df['Tavg[C]']).clip(lower=0) - df['DegreeDays_Average'] - df['DegreeDays_Good']  # Subtract from Average and Good
    return df

# Apply the new calculation for degree days based on target inside temperature
df_trondheim = calculate_degree_days_adjusted(df_trondheim, target_temp_good, target_temp_average, target_temp_bad)
df_rome = calculate_degree_days_adjusted(df_rome, target_temp_good, target_temp_average, target_temp_bad)

# Energy demand calculations (Norway and Italy)
U_value_trondheim = 0.18  # Norway U-value
U_value_rome = 0.32  # Italy U-value (Zone D)

A_over_V = 0.5  # External surface area to volume ratio
hours_per_year = 24 * 365  # 8760 hours in a year

# Calculate Thermal Energy Demand (ED_therm)
def calculate_thermal_energy(df, U_value):
    df['ED_therm_Good'] = (A_over_V * hours_per_year * U_value * df['DegreeDays_Good']) / 1000
    df['ED_therm_Average'] = (A_over_V * hours_per_year * U_value * df['DegreeDays_Average']) / 1000
    df['ED_therm_Bad'] = (A_over_V * hours_per_year * U_value * df['DegreeDays_Bad']) / 1000
    return df

df_trondheim = calculate_thermal_energy(df_trondheim, U_value_trondheim)
df_rome = calculate_thermal_energy(df_rome, U_value_rome)

# Calculate Humidity Energy Demand (ED_hum)
ACH = 1.0  # Air changes per hour
k_humid = 0.68  # Humidification constant
L_evap = 2257  # Latent heat of evaporation for water in kJ/kg
rho_air = 1.225  # Density of air in kg/m³
GD = 5.0  # Gram-days

'''
def calculate_humidity_energy(df):
    df['RH_Good'] = np.random.uniform(30, 50, len(df))
    df['RH_Average'] = np.random.uniform(40, 60, len(df))
    df['RH_Bad'] = np.random.uniform(50, 70, len(df))
    df['ED_hum_Good'] = ACH * hours_per_year * k_humid * L_evap * rho_air * (df['RH_Good'] / 100) * GD / 1000
    df['ED_hum_Average'] = ACH * hours_per_year * k_humid * L_evap * rho_air * (df['RH_Average'] / 100) * GD / 1000
    df['ED_hum_Bad'] = ACH * hours_per_year * k_humid * L_evap * rho_air * (df['RH_Bad'] / 100) * GD / 1000
    return df

df_trondheim = calculate_humidity_energy(df_trondheim)
df_rome = calculate_humidity_energy(df_rome)

# Calculate Total Energy Demand (ED_tot)
def calculate_total_energy(df):
    df['ED_tot_Good'] = df['ED_therm_Good'] + df['ED_hum_Good']
    df['ED_tot_Average'] = df['ED_therm_Average'] + df['ED_hum_Average']
    df['ED_tot_Bad'] = df['ED_therm_Bad'] + df['ED_hum_Bad']
    return df

df_trondheim = calculate_total_energy(df_trondheim)
df_rome = calculate_total_energy(df_rome)

# Group the data by year and sum the energy demand for each year
annual_energy_good_trondheim = df_trondheim.groupby('year')['ED_tot_Good'].sum()
annual_energy_average_trondheim = df_trondheim.groupby('year')['ED_tot_Average'].sum()
annual_energy_bad_trondheim = df_trondheim.groupby('year')['ED_tot_Bad'].sum()

annual_energy_good_rome = df_rome.groupby('year')['ED_tot_Good'].sum()
annual_energy_average_rome = df_rome.groupby('year')['ED_tot_Average'].sum()
annual_energy_bad_rome = df_rome.groupby('year')['ED_tot_Bad'].sum()

# Limit to the first 50 years (from 2015 to 2065)
energy_good_50_years_trondheim = annual_energy_good_trondheim.loc[2015:2065]
energy_average_50_years_trondheim = annual_energy_average_trondheim.loc[2015:2065]
energy_bad_50_years_trondheim = annual_energy_bad_trondheim.loc[2015:2065]

energy_good_50_years_rome = annual_energy_good_rome.loc[2015:2065]
energy_average_50_years_rome = annual_energy_average_rome.loc[2015:2065]
energy_bad_50_years_rome = annual_energy_bad_rome.loc[2015:2065]


# Energy demand for 1 year, 5 years, and 50 years for each scenario and location, including separate thermal and humidity demands
def energy_summary_with_components(energy_therm_trondheim, energy_hum_trondheim, energy_therm_rome, energy_hum_rome, scenario):
    print(f"\nEnergy Demand in Norway (Trondheim) for 1 Year ({scenario} Scenario):")
    print(f"  Thermal Energy: {energy_therm_trondheim.iloc[0]:.2f} kWh, Humidity Energy: {energy_hum_trondheim.iloc[0]:.2f} kWh")
    print(f"Energy Demand in Italy (Rome) for 1 Year ({scenario} Scenario):")
    print(f"  Thermal Energy: {energy_therm_rome.iloc[0]:.2f} kWh, Humidity Energy: {energy_hum_rome.iloc[0]:.2f} kWh")

    print(f"\nEnergy Demand in Norway (Trondheim) for 5 Years ({scenario} Scenario):")
    print(f"  Thermal Energy: {energy_therm_trondheim.head(5).sum():.2f} kWh, Humidity Energy: {energy_hum_trondheim.head(5).sum():.2f} kWh")
    print(f"Energy Demand in Italy (Rome) for 5 Years ({scenario} Scenario):")
    print(f"  Thermal Energy: {energy_therm_rome.head(5).sum():.2f} kWh, Humidity Energy: {energy_hum_rome.head(5).sum():.2f} kWh")

    print(f"\nEnergy Demand in Norway (Trondheim) for 50 Years ({scenario} Scenario):")
    print(f"  Thermal Energy: {energy_therm_trondheim.sum():.2f} kWh, Humidity Energy: {energy_hum_trondheim.sum():.2f} kWh")
    print(f"Energy Demand in Italy (Rome) for 50 Years ({scenario} Scenario):")
    print(f"  Thermal Energy: {energy_therm_rome.sum():.2f} kWh, Humidity Energy: {energy_hum_rome.sum():.2f} kWh")

# Separate energy demand calculations for thermal and humidity components
annual_therm_good_trondheim = df_trondheim.groupby('year')['ED_therm_Good'].sum()
annual_hum_good_trondheim = df_trondheim.groupby('year')['ED_hum_Good'].sum()
annual_therm_average_trondheim = df_trondheim.groupby('year')['ED_therm_Average'].sum()
annual_hum_average_trondheim = df_trondheim.groupby('year')['ED_hum_Average'].sum()
annual_therm_bad_trondheim = df_trondheim.groupby('year')['ED_therm_Bad'].sum()
annual_hum_bad_trondheim = df_trondheim.groupby('year')['ED_hum_Bad'].sum()

annual_therm_good_rome = df_rome.groupby('year')['ED_therm_Good'].sum()
annual_hum_good_rome = df_rome.groupby('year')['ED_hum_Good'].sum()
annual_therm_average_rome = df_rome.groupby('year')['ED_therm_Average'].sum()
annual_hum_average_rome = df_rome.groupby('year')['ED_hum_Average'].sum()
annual_therm_bad_rome = df_rome.groupby('year')['ED_therm_Bad'].sum()
annual_hum_bad_rome = df_rome.groupby('year')['ED_hum_Bad'].sum()

# Output for Good, Average, and Bad Scenarios
energy_summary_with_components(annual_therm_good_trondheim, annual_hum_good_trondheim, annual_therm_good_rome, annual_hum_good_rome, 'Good')
energy_summary_with_components(annual_therm_average_trondheim, annual_hum_average_trondheim, annual_therm_average_rome, annual_hum_average_rome, 'Average')
energy_summary_with_components(annual_therm_bad_trondheim, annual_hum_bad_trondheim, annual_therm_bad_rome, annual_hum_bad_rome, 'Bad')
'''
'''
# Print degree days for verification
print("\nDegree Days for 1 Year (Good Scenario):")
print(f"Norway (Trondheim): {df_trondheim['DegreeDays_Good'].sum()}")
print(f"Italy (Rome): {df_rome['DegreeDays_Good'].sum()}")

print("\nDegree Days for 1 Year (Average Scenario):")
print(f"Norway (Trondheim): {df_trondheim['DegreeDays_Average'].sum()}")
print(f"Italy (Rome): {df_rome['DegreeDays_Average'].sum()}")

print("\nDegree Days for 1 Year (Bad Scenario):")
print(f"Norway (Trondheim): {df_trondheim['DegreeDays_Bad'].sum()}")
print(f"Italy (Rome): {df_rome['DegreeDays_Bad'].sum()}")
'''

# Print average outside temperatures for verification
print("\nAverage Outside Temperatures for Norway (Trondheim):")
print(df_trondheim['Tavg[C]'].describe())

print("\nAverage Outside Temperatures for Italy (Rome):")
print(df_rome['Tavg[C]'].describe())
