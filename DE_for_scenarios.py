import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Constants for the model
R = 8.314  # Ideal gas constant (J/(mol·K))
A = 0.00103  # Pre-exponential factor (mol^-2 m^6 s^-1)
Ea = 70734  # Activation energy (J/mol)

# Initial concentrations (mol/m^3)
ROAc0 = 13403.6
H2O0 = 2137.2
HOAc0 = 52  # Starting acetic acid concentration

# Time span for simulation (50 years in seconds)
time_span = (0, 50 * 365.25 * 24 * 60 * 60)  # 50 years

# Define the ODE function
def acetic_acid_concentration(t, HOAc, k):
    ROAc = ROAc0 - HOAc
    H2O = H2O0 - HOAc
    dHOAc_dt = k * ROAc * H2O * HOAc
    return dHOAc_dt

# Define scenarios
'''
cases = {
    "Good Scenario (2°C)": {"HOAc0": HOAc0, "T": 275.15, "color": "green"},  # 2°C
    "Average Scenario (7°C)": {"HOAc0": HOAc0, "T": 280.15, "color": "black"},  # 7°C
    "Bad Scenario (15°C)": {"HOAc0": HOAc0, "T": 288.15, "color": "red"}  # 15°C
}
'''
cases = {
    "2°C": {"HOAc0": HOAc0, "T": 275.15, "color": "green"},  # 2°C
    "7°C": {"HOAc0": HOAc0, "T": 280.15, "color": "black"},  # 7°C
    "15°C": {"HOAc0": HOAc0, "T": 288.15, "color": "red"}  # 15°C
}

results = {}
for case, params in cases.items():
    # Update constants for the case
    HOAc0 = params["HOAc0"]
    T = params["T"]
    k = A * np.exp(-Ea / (R * T))
    
    # Solve the ODE
    solution = solve_ivp(
        acetic_acid_concentration, time_span, [HOAc0],
        args=(k,), method='RK45', t_eval=np.linspace(time_span[0], time_span[1], 100)
    )
    results[case] = solution

# Plot the results
plt.figure(figsize=(10, 6))
for case, solution in results.items():
    time_years = solution.t / (365.25 * 24 * 3600)  # Convert time to years
    plt.plot(time_years, solution.y[0], label=case, color=cases[case]["color"])  # Apply specific color from cases

# Add a horizontal line for the starting point
plt.axhline(y=HOAc0, color='blue', linestyle='--', label='Starting Point (52 mol/m³)')

# Font size of tick labels
plt.xticks(fontsize=14)
plt.yticks(np.arange(0, np.max([sol.y[0].max() for sol in results.values()]) + 500, 500), fontsize=14)

# Add labels, title, and legend
# plt.title("Increase in Acetic Acid Concentration in CTA Over 50 Years")
plt.xlabel("Time (years)", fontsize=14)
plt.ylabel("Acetic Acid Concentration (mol/m³)", fontsize=14)
plt.legend()
plt.grid(True)
plt.show()
