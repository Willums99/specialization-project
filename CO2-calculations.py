import pandas as pd
import numpy as np

# Placeholder emission factors (kg CO₂ per kWh)
emission_factor_norway = 0.012  # CoM emission factor Norway (2021)
emission_factor_italy = 0.284   # CoM emission factor Italy (2021)

# Function to calculate CO₂ emissions
def calculate_co2_emissions(ed, emission_factor):
    return ed * emission_factor

# Example data for energy demand (ED) in kWh from the program calculations
ed_results = {
    "Scenario": ["Good", "Average", "Bad"],
    "ED_1y_R": [14533, 9627, 4048],
    "ED_1y_T": [2470, 1018, 125],
    "ED_5y_R": [88726, 58644, 23772],
    "ED_5y_T": [12264, 4786, 557],
    "ED_50y_R": [777560, 528332, 223831],
    "ED_50y_T": [136836, 61510, 10212]
}

# Calculate CO₂ emissions for each ED result using separate factors for Norway and Italy
co2_results = {
    "CO₂_1y_R": [calculate_co2_emissions(ed, emission_factor_italy) for ed in ed_results["ED_1y_R"]],
    "CO₂_1y_T": [calculate_co2_emissions(ed, emission_factor_norway) for ed in ed_results["ED_1y_T"]],
    "CO₂_5y_R": [calculate_co2_emissions(ed, emission_factor_italy) for ed in ed_results["ED_5y_R"]],
    "CO₂_5y_T": [calculate_co2_emissions(ed, emission_factor_norway) for ed in ed_results["ED_5y_T"]],
    "CO₂_50y_R": [calculate_co2_emissions(ed, emission_factor_italy) for ed in ed_results["ED_50y_R"]],
    "CO₂_50y_T": [calculate_co2_emissions(ed, emission_factor_norway) for ed in ed_results["ED_50y_T"]]
}

# Print the results in the desired format
print("Total Energy Demand (Thermal + Humidity) and CO₂ Emissions:")

# Scenarios for 1 Year
print("\nTotal Energy Demand (Thermal + Humidity) for 1 Year (Good Scenario):")
print(f"Norway: {ed_results['ED_1y_T'][0]:.2f} kWh, Italy: {ed_results['ED_1y_R'][0]:.2f} kWh")
print(f"CO₂ Emissions for 1 Year (Good Scenario): Norway: {co2_results['CO₂_1y_T'][0]:.2f} kg CO2, Italy: {co2_results['CO₂_1y_R'][0]:.2f} kg CO2")

print("\nTotal Energy Demand (Thermal + Humidity) for 1 Year (Average Scenario):")
print(f"Norway: {ed_results['ED_1y_T'][1]:.2f} kWh, Italy: {ed_results['ED_1y_R'][1]:.2f} kWh")
print(f"CO₂ Emissions for 1 Year (Average Scenario): Norway: {co2_results['CO₂_1y_T'][1]:.2f} kg CO2, Italy: {co2_results['CO₂_1y_R'][1]:.2f} kg CO2")

print("\nTotal Energy Demand (Thermal + Humidity) for 1 Year (Bad Scenario):")
print(f"Norway: {ed_results['ED_1y_T'][2]:.2f} kWh, Italy: {ed_results['ED_1y_R'][2]:.2f} kWh")
print(f"CO₂ Emissions for 1 Year (Bad Scenario): Norway: {co2_results['CO₂_1y_T'][2]:.2f} kg CO2, Italy: {co2_results['CO₂_1y_R'][2]:.2f} kg CO2")

# Scenarios for 5 Years
print("\nTotal Energy Demand (Thermal + Humidity) for 5 Years (Good Scenario):")
print(f"Norway: {ed_results['ED_5y_T'][0]:.2f} kWh, Italy: {ed_results['ED_5y_R'][0]:.2f} kWh")
print(f"CO₂ Emissions for 5 Years (Good Scenario): Norway: {co2_results['CO₂_5y_T'][0]:.2f} kg CO2, Italy: {co2_results['CO₂_5y_R'][0]:.2f} kg CO2")

print("\nTotal Energy Demand (Thermal + Humidity) for 5 Years (Average Scenario):")
print(f"Norway: {ed_results['ED_5y_T'][1]:.2f} kWh, Italy: {ed_results['ED_5y_R'][1]:.2f} kWh")
print(f"CO₂ Emissions for 5 Years (Average Scenario): Norway: {co2_results['CO₂_5y_T'][1]:.2f} kg CO2, Italy: {co2_results['CO₂_5y_R'][1]:.2f} kg CO2")

print("\nTotal Energy Demand (Thermal + Humidity) for 5 Years (Bad Scenario):")
print(f"Norway: {ed_results['ED_5y_T'][2]:.2f} kWh, Italy: {ed_results['ED_5y_R'][2]:.2f} kWh")
print(f"CO₂ Emissions for 5 Years (Bad Scenario): Norway: {co2_results['CO₂_5y_T'][2]:.2f} kg CO2, Italy: {co2_results['CO₂_5y_R'][2]:.2f} kg CO2")

# Scenarios for 50 Years
print("\nTotal Energy Demand (Thermal + Humidity) for 50 Years (Good Scenario):")
print(f"Norway: {ed_results['ED_50y_T'][0]:.2f} kWh, Italy: {ed_results['ED_50y_R'][0]:.2f} kWh")
print(f"CO₂ Emissions for 50 Years (Good Scenario): Norway: {co2_results['CO₂_50y_T'][0]:.2f} kg CO2, Italy: {co2_results['CO₂_50y_R'][0]:.2f} kg CO2")

print("\nTotal Energy Demand (Thermal + Humidity) for 50 Years (Average Scenario):")
print(f"Norway: {ed_results['ED_50y_T'][1]:.2f} kWh, Italy: {ed_results['ED_50y_R'][1]:.2f} kWh")
print(f"CO₂ Emissions for 50 Years (Average Scenario): Norway: {co2_results['CO₂_50y_T'][1]:.2f} kg CO2, Italy: {co2_results['CO₂_50y_R'][1]:.2f} kg CO2")

print("\nTotal Energy Demand (Thermal + Humidity) for 50 Years (Bad Scenario):")
print(f"Norway: {ed_results['ED_50y_T'][2]:.2f} kWh, Italy: {ed_results['ED_50y_R'][2]:.2f} kWh")
print(f"CO₂ Emissions for 50 Years (Bad Scenario): Norway: {co2_results['CO₂_50y_T'][2]:.2f} kg CO2, Italy: {co2_results['CO₂_50y_R'][2]:.2f} kg CO2")

'''
***ED based on SH***
Norway: 31412.20 kWh, Italy: 54254.05 kWh
Total Energy Demand (Thermal + Humidity) for 1 Year (Average Scenario):
Norway: 30685.95 kWh, Italy: 51800.83 kWh
Total Energy Demand (Thermal + Humidity) for 1 Year (Bad Scenario):
Norway: 30239.50 kWh, Italy: 49011.49 kWh

Total Energy Demand (Thermal + Humidity) for 5 Years (Good Scenario):
Norway: 174137.71 kWh, Italy: 395947.31 kWh
Total Energy Demand (Thermal + Humidity) for 5 Years (Average Scenario):
Norway: 170398.44 kWh, Italy: 378399.70 kWh
Total Energy Demand (Thermal + Humidity) for 5 Years (Bad Scenario):
Norway: 168284.11 kWh, Italy: 357760.28 kWh

Total Energy Demand (Thermal + Humidity) for 50 Years (Good Scenario):
Norway: 1635185.62 kWh, Italy: 2935394.56 kWh
Total Energy Demand (Thermal + Humidity) for 50 Years (Average Scenario):
Norway: 1597522.70 kWh, Italy: 2810780.16 kWh
Total Energy Demand (Thermal + Humidity) for 50 Years (Bad Scenario):
Norway: 1571873.72 kWh, Italy: 2658529.64 kWh
'''
