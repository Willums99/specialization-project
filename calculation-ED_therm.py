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

# Calculate energy demand for each scenario
def calculate_ed_period(CDD_trondheim, CDD_rome, start_year, end_year):
    # Slice the data for the given years
    CDD_trondheim_period = CDD_trondheim.loc[start_year:end_year].sum()
    CDD_rome_period = CDD_rome.loc[start_year:end_year].sum()
    
    # Calculate thermal energy demand
    ED_trondheim = calculate_ed(CDD_trondheim_period, U_value_trondheim)
    ED_rome = calculate_ed(CDD_rome_period, U_value_rome)
    
    return ED_trondheim, ED_rome

# Calculate energy demands for 1 year (2015), 5 years (2015-2020), and 50 years (2015-2065)
ED_good_1_year = calculate_ed_period(CDD_good_trondheim, CDD_good_rome, 2015, 2015)
ED_average_1_year = calculate_ed_period(CDD_average_trondheim, CDD_average_rome, 2015, 2015)
ED_bad_1_year = calculate_ed_period(CDD_bad_trondheim, CDD_bad_rome, 2015, 2015)

ED_good_5_years = calculate_ed_period(CDD_good_trondheim, CDD_good_rome, 2015, 2020)
ED_average_5_years = calculate_ed_period(CDD_average_trondheim, CDD_average_rome, 2015, 2020)
ED_bad_5_years = calculate_ed_period(CDD_bad_trondheim, CDD_bad_rome, 2015, 2020)

ED_good_50_years = calculate_ed_period(CDD_good_trondheim, CDD_good_rome, 2015, 2065)
ED_average_50_years = calculate_ed_period(CDD_average_trondheim, CDD_average_rome, 2015, 2065)
ED_bad_50_years = calculate_ed_period(CDD_bad_trondheim, CDD_bad_rome, 2015, 2065)

# Align the Rome and Trondheim datasets between 2015 and 2065
df_trondheim = df_trondheim.loc[df_trondheim['year'].between(2015, 2065)]
df_rome = df_rome.loc[df_rome['year'].between(2015, 2065)]

# Print results for comparison
print(f"Energy Demand for 1 Year (Good Scenario):\nNorway: {ED_good_1_year[0]:.2f} kWh, Italy: {ED_good_1_year[1]:.2f} kWh")
print(f"Energy Demand for 1 Year (Average Scenario):\nNorway: {ED_average_1_year[0]:.2f} kWh, Italy: {ED_average_1_year[1]:.2f} kWh")
print(f"Energy Demand for 1 Year (Bad Scenario):\nNorway: {ED_bad_1_year[0]:.2f} kWh, Italy: {ED_bad_1_year[1]:.2f} kWh")

print(f"\nEnergy Demand for 5 Years (Good Scenario):\nNorway: {ED_good_5_years[0]:.2f} kWh, Italy: {ED_good_5_years[1]:.2f} kWh")
print(f"Energy Demand for 5 Years (Average Scenario):\nNorway: {ED_average_5_years[0]:.2f} kWh, Italy: {ED_average_5_years[1]:.2f} kWh")
print(f"Energy Demand for 5 Years (Bad Scenario):\nNorway: {ED_bad_5_years[0]:.2f} kWh, Italy: {ED_bad_5_years[1]:.2f} kWh")

print(f"\nEnergy Demand for 50 Years (Good Scenario):\nNorway: {ED_good_50_years[0]:.2f} kWh, Italy: {ED_good_50_years[1]:.2f} kWh")
print(f"Energy Demand for 50 Years (Average Scenario):\nNorway: {ED_average_50_years[0]:.2f} kWh, Italy: {ED_average_50_years[1]:.2f} kWh")
print(f"Energy Demand for 50 Years (Bad Scenario):\nNorway: {ED_bad_50_years[0]:.2f} kWh, Italy: {ED_bad_50_years[1]:.2f} kWh")

# Plotting the results
# Create years array for plotting (ensuring it matches the available data)
years_trondheim = CDD_good_trondheim.loc[2015:2065].index
years_rome = CDD_good_rome.loc[2015:2065].index

# Calculate thermal energy demand per year for both Norway and Italy
def calculate_annual_ed(CDD_trondheim, CDD_rome):
    ED_trondheim = calculate_ed(CDD_trondheim, U_value_trondheim)
    ED_rome = calculate_ed(CDD_rome, U_value_rome)
    return ED_trondheim, ED_rome

# Calculate the thermal energy demand for each year between 2015-2065
annual_ed_good_trondheim, annual_ed_good_rome = calculate_annual_ed(CDD_good_trondheim.loc[2015:2065], CDD_good_rome.loc[2015:2065])
annual_ed_average_trondheim, annual_ed_average_rome = calculate_annual_ed(CDD_average_trondheim.loc[2015:2065], CDD_average_rome.loc[2015:2065])
annual_ed_bad_trondheim, annual_ed_bad_rome = calculate_annual_ed(CDD_bad_trondheim.loc[2015:2065], CDD_bad_rome.loc[2015:2065])

# Create figure and axes for the plots
fig, ax = plt.subplots(3, 1, figsize=(10, 15))

# Plot the Good scenario comparison
ax[0].plot(years_trondheim, annual_ed_good_trondheim, label="Trondheim (Good)", color="blue")
ax[0].plot(years_rome, annual_ed_good_rome, label="Rome (Good)", color="orange")
ax[0].set_ylabel('Thermal Energy Demand (kWh)')
ax[0].set_title('Thermal Energy Demand (Good Scenario)')
ax[0].grid(True)
ax[0].legend()

# Plot the Average scenario comparison
ax[1].plot(years_trondheim, annual_ed_average_trondheim, label="Trondheim (Average)", color="blue")
ax[1].plot(years_rome, annual_ed_average_rome, label="Rome (Average)", color="orange")
ax[1].set_ylabel('Thermal Energy Demand (kWh)')
ax[1].set_title('Thermal Energy Demand (Average Scenario)')
ax[1].grid(True)
ax[1].legend()

# Plot the Bad scenario comparison
ax[2].plot(years_trondheim, annual_ed_bad_trondheim, label="Trondheim (Bad)", color="blue")
ax[2].plot(years_rome, annual_ed_bad_rome, label="Rome (Bad)", color="orange")
ax[2].set_ylabel('Thermal Energy Demand (kWh)')
ax[2].set_title('Thermal Energy Demand (Bad Scenario)')
ax[2].grid(True)
ax[2].legend()

# Display the plots
plt.tight_layout()
plt.show()
