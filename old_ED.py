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

# Define the temperature ranges for the three scenarios
def classify_scenario(temp):
    if temp < 2:
        return 'Good'
    elif 2 <= temp <= 7:
        return 'Average'
    elif 7 < temp < 15:
        return 'Bad'
    else:
        return None

# Apply the scenario classification
df_trondheim['Scenario'] = df_trondheim['Tavg[C]'].apply(classify_scenario)
df_rome['Scenario'] = df_rome['Tavg[C]'].apply(classify_scenario)

# Energy demand calculations (Norway and Italy)
U_value_trondheim = 0.18  # Norway U-value
U_value_rome = 0.32  # Italy U-value (Zone D)

A_over_V = 0.5  # External surface area to volume ratio
hours_per_year = 24 * 365  # 8760 hours in a year

# Calculate degree days for each scenario
def calculate_degree_days(df):
    df['DegreeDays_Good'] = (2 - df['Tavg[C]']).clip(lower=0)
    df['DegreeDays_Average'] = ((7 - df['Tavg[C]']).clip(lower=0) - df['DegreeDays_Good']).clip(lower=0)
    df['DegreeDays_Bad'] = ((15 - df['Tavg[C]']).clip(lower=0) - df['DegreeDays_Average'] - df['DegreeDays_Good']).clip(lower=0)
    return df

df_trondheim = calculate_degree_days(df_trondheim)
df_rome = calculate_degree_days(df_rome)

# Step 1: Calculate Thermal Energy Demand (ED_therm)
def calculate_thermal_energy(df, U_value):
    df['ED_therm_Good'] = (A_over_V * hours_per_year * U_value * df['DegreeDays_Good']) / 1000
    df['ED_therm_Average'] = (A_over_V * hours_per_year * U_value * df['DegreeDays_Average']) / 1000
    df['ED_therm_Bad'] = (A_over_V * hours_per_year * U_value * df['DegreeDays_Bad']) / 1000
    return df

df_trondheim = calculate_thermal_energy(df_trondheim, U_value_trondheim)
df_rome = calculate_thermal_energy(df_rome, U_value_rome)

# Step 2: Calculate Humidity Energy Demand (ED_hum)
ACH = 1.0  # Air changes per hour
k_humid = 0.68  # Humidification constant
L_evap = 2257  # Latent heat of evaporation for water in kJ/kg
rho_air = 1.225  # Density of air in kg/m³
GD = 5.0  # Gram-days

# Define relative humidity ranges for each scenario
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

# Step 3: Total Energy Demand (ED_tot)
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

# Energy demand for 1 year, 5 years, and 50 years for each scenario and location
def energy_summary(energy_data_trondheim, energy_data_rome, scenario):
    print(f"\nEnergy Demand in Norway (Trondheim) for 1 Year ({scenario} Scenario): {energy_data_trondheim.iloc[0]:.2f} kWh")
    print(f"Energy Demand in Italy (Rome) for 1 Year ({scenario} Scenario): {energy_data_rome.iloc[0]:.2f} kWh")
    
    print(f"\nEnergy Demand in Norway (Trondheim) for 5 Years ({scenario} Scenario): {energy_data_trondheim.head(5).sum():.2f} kWh")
    print(f"Energy Demand in Italy (Rome) for 5 Years ({scenario} Scenario): {energy_data_rome.head(5).sum():.2f} kWh")
    
    print(f"\nEnergy Demand in Norway (Trondheim) for 50 Years ({scenario} Scenario): {energy_data_trondheim.sum():.2f} kWh")
    print(f"Energy Demand in Italy (Rome) for 50 Years ({scenario} Scenario): {energy_data_rome.sum():.2f} kWh")

# Output for Good, Average, and Bad Scenarios
energy_summary(energy_good_50_years_trondheim, energy_good_50_years_rome, 'Good')
energy_summary(energy_average_50_years_trondheim, energy_average_50_years_rome, 'Average')
energy_summary(energy_bad_50_years_trondheim, energy_bad_50_years_rome, 'Bad')

# Plot the results with consistent y-axis for all graphs
fig, ax = plt.subplots(3, 1, figsize=(10, 15))

# Determine the y-axis limits based on the maximum value in all scenarios
max_value = max(energy_good_50_years_trondheim.max(), energy_average_50_years_trondheim.max(), energy_bad_50_years_trondheim.max(),
                energy_good_50_years_rome.max(), energy_average_50_years_rome.max(), energy_bad_50_years_rome.max())

# Good Scenario
ax[0].plot(energy_good_50_years_trondheim.index, energy_good_50_years_trondheim.values, color='red', label='Norway (Good)')
ax[0].plot(energy_good_50_years_rome.index, energy_good_50_years_rome.values, color='green', linestyle='--', label='Italy (Good)')
ax[0].set_title('Energy Demand (Good Scenario) - Norway vs. Italy')
ax[0].set_ylabel('Energy Demand (kWh)')
ax[0].grid(True)
ax[0].set_ylim(0, max_value)
ax[0].legend()

# Average Scenario
ax[1].plot(energy_average_50_years_trondheim.index, energy_average_50_years_trondheim.values, color='red', label='Norway (Average)')
ax[1].plot(energy_average_50_years_rome.index, energy_average_50_years_rome.values, color='green', linestyle='--', label='Italy (Average)')
ax[1].set_title('Energy Demand (Average Scenario) - Norway vs. Italy')
ax[1].set_ylabel('Energy Demand (kWh)')
ax[1].grid(True)
ax[1].set_ylim(0, max_value)
ax[1].legend()

# Bad Scenario
ax[2].plot(energy_bad_50_years_trondheim.index, energy_bad_50_years_trondheim.values, color='red', label='Norway (Bad)')
ax[2].plot(energy_bad_50_years_rome.index, energy_bad_50_years_rome.values, color='green', linestyle='--', label='Italy (Bad)')
ax[2].set_title('Energy Demand (Bad Scenario) - Norway vs. Italy')
ax[2].set_ylabel('Energy Demand (kWh)')
ax[2].grid(True)
ax[2].set_ylim(0, max_value)
ax[2].legend()

# Display the plots
plt.tight_layout()
plt.show()
