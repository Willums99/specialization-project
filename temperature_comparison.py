import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV files
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

# Convert temperatures from Kelvin to Celsius
df_trondheim['Tmin[C]'] = df_trondheim['Tmin[K]'] - 273.15
df_trondheim['Tmax[C]'] = df_trondheim['Tmax[K]'] - 273.15
df_rome['Tmin[C]'] = df_rome['Tmin[K]'] - 273.15
df_rome['Tmax[C]'] = df_rome['Tmax[K]'] - 273.15

# --- First Graph: Monthly averages for 2015-2020 ---
df_trondheim_filtered_5_years = df_trondheim[(df_trondheim['year'] >= 2015) & (df_trondheim['year'] <= 2020)]
df_rome_filtered_5_years = df_rome[(df_rome['year'] >= 2015) & (df_rome['year'] <= 2020)]

# Group by year and month for monthly averages
df_trondheim_avg_5_years = df_trondheim_filtered_5_years.groupby(['year', 'month'])[['Tmin[C]', 'Tmax[C]']].mean().reset_index()
df_rome_avg_5_years = df_rome_filtered_5_years.groupby(['year', 'month'])[['Tmin[C]', 'Tmax[C]']].mean().reset_index()

# Create a combined "year-month" label for the x-axis
df_trondheim_avg_5_years['year-month'] = df_trondheim_avg_5_years['year'].astype(str) + '-' + df_trondheim_avg_5_years['month'].astype(str).str.zfill(2)
df_rome_avg_5_years['year-month'] = df_rome_avg_5_years['year'].astype(str) + '-' + df_rome_avg_5_years['month'].astype(str).str.zfill(2)
'''
# Plotting the monthly averages for Tmin and Tmax for both cities (2015-2020)
plt.figure(figsize=(14, 6))

# Plot Tmin and Tmax for both Trondheim and Rome
plt.plot(df_trondheim_avg_5_years['year-month'], df_trondheim_avg_5_years['Tmin[C]'], label='Trondheim Tmin [°C]', color='blue')
plt.plot(df_trondheim_avg_5_years['year-month'], df_trondheim_avg_5_years['Tmax[C]'], label='Trondheim Tmax [°C]', color='green')
plt.plot(df_rome_avg_5_years['year-month'], df_rome_avg_5_years['Tmin[C]'], label='Rome Tmin [°C]', color='orange')
plt.plot(df_rome_avg_5_years['year-month'], df_rome_avg_5_years['Tmax[C]'], label='Rome Tmax [°C]', color='red')

# Adding labels and title
plt.xlabel('Year-Month')
plt.ylabel('Temperature (°C)')
plt.title('Monthly Average Tmin and Tmax (2015-2020)')
plt.legend()

# Rotate x-axis labels for better readability
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()
'''

# --- Second Graph: Yearly averages for 2015-2065 ---
df_trondheim_filtered_50_years = df_trondheim[df_trondheim['year'] <= 2065]
df_rome_filtered_50_years = df_rome[df_rome['year'] <= 2065]

# Group by year for yearly averages
df_trondheim_avg_50_years = df_trondheim_filtered_50_years.groupby('year')[['Tmin[C]', 'Tmax[C]']].mean().reset_index()
df_rome_avg_50_years = df_rome_filtered_50_years.groupby('year')[['Tmin[C]', 'Tmax[C]']].mean().reset_index()

# Plotting the yearly averages for Tmin and Tmax for both cities (2015-2065)
plt.figure(figsize=(10, 6))

# Plot yearly averages for both cities
plt.plot(df_trondheim_avg_50_years['year'], df_trondheim_avg_50_years['Tmin[C]'], label='Trondheim Tmin [°C]', color='blue')
plt.plot(df_trondheim_avg_50_years['year'], df_trondheim_avg_50_years['Tmax[C]'], label='Trondheim Tmax [°C]', color='green')
plt.plot(df_rome_avg_50_years['year'], df_rome_avg_50_years['Tmin[C]'], label='Rome Tmin [°C]', color='orange')
plt.plot(df_rome_avg_50_years['year'], df_rome_avg_50_years['Tmax[C]'], label='Rome Tmax [°C]', color='red')

# Adding labels and title
plt.xlabel('Year')
plt.ylabel('Temperature (°C)')
plt.title('Yearly Average Temperature Comparison (2015-2065)')
plt.legend()

plt.show()
