import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Method 1 for SH calculation
def calculate_sh_method1(T, RH):
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

# Define years list for plotting
years = list(range(2015, 2066))

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
RH_good = 0.30
RH_average = 0.50
RH_bad = 0.70

# Calculate SH for each scenario
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

# Define function to calculate energy demand
def calculate_ed(CDD, U_value):
    A_over_V = 1
    hours_per_year = 8760
    return (A_over_V * hours_per_year * U_value * CDD) / 1000  # kWh

# Lists to store the total energy demand for each year in each scenario
ed_good_trondheim, ed_good_rome = [], []
ed_average_trondheim, ed_average_rome = [], []
ed_bad_trondheim, ed_bad_rome = [], []

# Calculate the total energy demand for each year
for year in years:
    CDD_trondheim = df_trondheim[df_trondheim['year'] == year]
    CDD_rome = df_rome[df_rome['year'] == year]

    ed_good_trondheim.append(calculate_ed(CDD_trondheim['CDD_Good'].sum(), 0.18))
    ed_good_rome.append(calculate_ed(CDD_rome['CDD_Good'].sum(), 0.32))
    
    ed_average_trondheim.append(calculate_ed(CDD_trondheim['CDD_Average'].sum(), 0.18))
    ed_average_rome.append(calculate_ed(CDD_rome['CDD_Average'].sum(), 0.32))
    
    ed_bad_trondheim.append(calculate_ed(CDD_trondheim['CDD_Bad'].sum(), 0.18))
    ed_bad_rome.append(calculate_ed(CDD_rome['CDD_Bad'].sum(), 0.32))

plt.figure(figsize=(16, 10))  # Increase figure width

# Plot for Good scenario
plt.plot(years, ed_good_trondheim, label="Trondheim ED", color="green")
plt.plot(years, ed_good_rome, label="Rome ED", color="green", linestyle ='--')

# Plot for Average scenario
plt.plot(years, ed_average_trondheim, label="Trondheim ED", color="black")
plt.plot(years, ed_average_rome, label="Rome ED", color="black", linestyle='--')

# Plot for Bad scenario
plt.plot(years, ed_bad_trondheim, label="Trondheim ED", color="red")
plt.plot(years, ed_bad_rome, label="Rome ED", color="red", linestyle='--')

plt.xlabel("Year", fontsize=16)
plt.ylabel("Total Energy Demand (kWh)", fontsize=16)
# plt.title("Annual Total Energy Demand from 2015 to 2065")

# Font size of tick labels
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.axvline(x=2024, color='blue', linestyle='--', linewidth=1.5, label='Current Year 2024')

# Move the legend outside and prevent cutoff
plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0)
plt.grid(True)

# Ensure layout prevents clipping
plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust the right boundary
plt.show()


