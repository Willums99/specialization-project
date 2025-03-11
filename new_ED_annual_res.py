import pandas as pd
import numpy as np

# Francesca's Method 1 for SH calculation
def calculate_sh_method1(T, RH):
    SH = 38.015 * (10 ** ((7.65 * T) / (243.12 + T)) * RH) / (1013.25 - (0.06112 * 10 ** ((7.65 * T) / (243.12 + T)) * RH))
    return SH  # in g/kg

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

def calculate_ed(CDD, U_value):
    A_over_V = 1
    hours_per_year = 8760
    return (A_over_V * hours_per_year * U_value * CDD) / 1000  # kWh

def calculate_humidity_ed(SH, ACH=1.0, k=2.78*10**(-7), L_evap=2257, rho_air=1.225):
    hours_per_year = 8760
    return ACH * hours_per_year * k * L_evap * rho_air * SH / 1000  # kWh

def calculate_cumulative_ed(CDD_trondheim, CDD_rome, SH_trondheim, SH_rome, U_value_trondheim, U_value_rome):
    cumulative_ed = {
        "Year": [],
        "Good_Norway": [], "Good_Italy": [],
        "Average_Norway": [], "Average_Italy": [],
        "Bad_Norway": [], "Bad_Italy": []
    }
    
    for year in range(2015, 2066):
        cumulative_ed["Year"].append(year)
        
        for scenario in ["Good", "Average", "Bad"]:
            CDD_tr = CDD_trondheim[f'CDD_{scenario}'].loc[2015:year].sum()
            CDD_rm = CDD_rome[f'CDD_{scenario}'].loc[2015:year].sum()
            SH_tr = SH_trondheim[f'SH_{scenario}'].loc[2015:year].sum()
            SH_rm = SH_rome[f'SH_{scenario}'].loc[2015:year].sum()
            
            ED_therm_tr = calculate_ed(CDD_tr, U_value_trondheim)
            ED_therm_rm = calculate_ed(CDD_rm, U_value_rome)
            ED_hum_tr = calculate_humidity_ed(SH_tr)
            ED_hum_rm = calculate_humidity_ed(SH_rm)
            
            cumulative_ed[f"{scenario}_Norway"].append(ED_therm_tr + ED_hum_tr)
            cumulative_ed[f"{scenario}_Italy"].append(ED_therm_rm + ED_hum_rm)
    
    return pd.DataFrame(cumulative_ed)

# Load and preprocess data
df_trondheim = pd.read_csv('trondheim_temperature_SSP2-45.csv', delimiter=';')
df_rome = pd.read_csv('rome_temperature_SSP2-45.csv', delimiter=';')
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

RH_values = {"Good": 0.30, "Average": 0.50, "Bad": 0.70}
for scenario, RH in RH_values.items():
    df_trondheim[f'SH_{scenario}'] = calculate_sh_method1(df_trondheim['Tavg[C]'], RH)
    df_rome[f'SH_{scenario}'] = calculate_sh_method1(df_rome['Tavg[C]'], RH)
    df_trondheim[f'CDD_{scenario}'] = calculate_cdd(df_trondheim, {"Good": 2, "Average": 7, "Bad": 15}[scenario])
    df_rome[f'CDD_{scenario}'] = calculate_cdd(df_rome, {"Good": 2, "Average": 7, "Bad": 15}[scenario])

U_value_trondheim = 0.18
U_value_rome = 0.32
cumulative_ed_df = calculate_cumulative_ed(df_trondheim, df_rome, df_trondheim, df_rome, U_value_trondheim, U_value_rome)
# Save results to a CSV file
cumulative_ed_df.to_csv("cumulative_energy_demand_50_years.csv", index=False)

# Print results to the terminal
print(cumulative_ed_df)
