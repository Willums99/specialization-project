import pandas as pd
import numpy as np

# Load the CSV file with semicolon as the delimiter
df_trondheim = pd.read_csv('trondheim_temperature_SSP2-45.csv', delimiter=';')
df_rome = pd.read_csv('rome_temperature_SSP2-45.csv', delimiter=';')

# Rename columns to remove special characters and make them easier to reference
df_trondheim.columns = ['datetime', 'year', 'month', 'day', 'Tmin[K]', 'Tmax[K]']
df_rome.columns = ['datetime', 'year', 'month', 'day', 'Tmin[K]', 'Tmax[K]']

# Replace commas with periods and convert the columns to float
df_trondheim['Tmin[K]'] = df_trondheim['Tmin[K]'].str.replace(',', '.').astype(float)
df_trondheim['Tmax[K]'] = df_trondheim['Tmax[K]'].str.replace(',', '.').astype(float)
df_rome['Tmin[K]'] = df_rome['Tmin[K]'].str.replace(',', '.').astype(float)
df_rome['Tmax[K]'] = df_rome['Tmax[K]'].str.replace(',', '.').astype(float)

# Convert temperature from Kelvin to Celsius
df_trondheim['Tmin[C]'] = df_trondheim['Tmin[K]'] - 273.15
df_trondheim['Tmax[C]'] = df_trondheim['Tmax[K]'] - 273.15
df_rome['Tmin[C]'] = df_rome['Tmin[K]'] - 273.15
df_rome['Tmax[C]'] = df_rome['Tmax[K]'] - 273.15

# Calculate average temperature for each day
df_trondheim['Tavg[C]'] = (df_trondheim['Tmin[C]'] + df_trondheim['Tmax[C]']) / 2
df_rome['Tavg[C]'] = (df_rome['Tmin[C]'] + df_rome['Tmax[C]']) / 2

# Define the CDD calculation based on CISBE conditions
def calculate_cdd(df, T_base):
    CDD = np.zeros(len(df))
    for i in range(len(df)):
        Tmin = df.loc[i, 'Tmin[C]']
        Tmax = df.loc[i, 'Tmax[C]']
        Tavg = df.loc[i, 'Tavg[C]']
        
        # Condition: Tmax <= Tbase
        if Tmax <= T_base:
            CDD[i] = 0
        # Condition: Tavg <= Tbase < Tmax
        elif Tavg <= T_base < Tmax:
            CDD[i] = (Tmax - T_base) / 4
        # Condition: Tmin < Tbase < Tavg
        elif Tmin < T_base < Tavg:
            CDD[i] = ((Tmax - T_base) / 2) - ((T_base - Tmin) / 4)
        # Condition: Tmin >= Tbase
        elif Tmin >= T_base:
            CDD[i] = Tavg - T_base
    
    return CDD

# Apply CDD calculation for Good, Average, and Bad scenarios
df_trondheim['CDD_Good'] = calculate_cdd(df_trondheim, 2)   # Tbase = 2°C for Good scenario
df_trondheim['CDD_Average'] = calculate_cdd(df_trondheim, 7) # Tbase = 7°C for Average scenario
df_trondheim['CDD_Bad'] = calculate_cdd(df_trondheim, 15)    # Tbase = 15°C for Bad scenario

df_rome['CDD_Good'] = calculate_cdd(df_rome, 2)   # Tbase = 2°C for Good scenario
df_rome['CDD_Average'] = calculate_cdd(df_rome, 7) # Tbase = 7°C for Average scenario
df_rome['CDD_Bad'] = calculate_cdd(df_rome, 15)    # Tbase = 15°C for Bad scenario

# Group by year and sum CDD for each scenario
CDD_good_trondheim = df_trondheim.groupby('year')['CDD_Good'].sum()
CDD_average_trondheim = df_trondheim.groupby('year')['CDD_Average'].sum()
CDD_bad_trondheim = df_trondheim.groupby('year')['CDD_Bad'].sum()

CDD_good_rome = df_rome.groupby('year')['CDD_Good'].sum()
CDD_average_rome = df_rome.groupby('year')['CDD_Average'].sum()
CDD_bad_rome = df_rome.groupby('year')['CDD_Bad'].sum()


# Display the CDD results
print("Cooling Degree Days (CDD) for Trondheim:")
print(f"Good Scenario (Tbase = 2°C): {CDD_good_trondheim.sum()} CDD")
print(f"Average Scenario (Tbase = 7°C): {CDD_average_trondheim.sum()} CDD")
print(f"Bad Scenario (Tbase = 15°C): {CDD_bad_trondheim.sum()} CDD")

print("\nCooling Degree Days (CDD) for Rome:")
print(f"Good Scenario (Tbase = 2°C): {CDD_good_rome.sum()} CDD")
print(f"Average Scenario (Tbase = 7°C): {CDD_average_rome.sum()} CDD")
print(f"Bad Scenario (Tbase = 15°C): {CDD_bad_rome.sum()} CDD")
