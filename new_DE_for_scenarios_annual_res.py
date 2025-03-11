import numpy as np
from scipy.integrate import solve_ivp
import pandas as pd

# Constants for the model
R = 8.314  # Ideal gas constant (J/(mol·K))
A = 0.00103  # Pre-exponential factor (mol^-2 m^6 s^-1)
Ea = 70734  # Activation energy (J/mol)

# Initial concentrations (mol/m^3)
ROAc0 = 13403.6
H2O0 = 2137.2
HOAc0 = 52  # Starting acetic acid concentration

# Time span for simulation (50 years in seconds)
years = np.arange(0, 51, 1)  # From year 0 to 50
time_span = (0, 50 * 365.25 * 24 * 60 * 60)  # 50 years in seconds
time_eval = years * 365.25 * 24 * 60 * 60  # Convert years to seconds

# Define the ODE function
def acetic_acid_concentration(t, HOAc, k):
    ROAc = ROAc0 - HOAc
    H2O = H2O0 - HOAc
    dHOAc_dt = k * ROAc * H2O * HOAc
    return dHOAc_dt

# Define scenarios
cases = {
    "2°C": {"HOAc0": HOAc0, "T": 275.15},  # 2°C
    "7°C": {"HOAc0": HOAc0, "T": 280.15},  # 7°C
    "15°C": {"HOAc0": HOAc0, "T": 288.15}  # 15°C
}

# Store results in a dictionary
data = {"Year": years}

for case, params in cases.items():
    HOAc0 = params["HOAc0"]
    T = params["T"]
    k = A * np.exp(-Ea / (R * T))
    
    # Solve the ODE
    solution = solve_ivp(
        acetic_acid_concentration, time_span, [HOAc0],
        args=(k,), method='RK45', t_eval=time_eval
    )
    
    # Store results
    data[case] = solution.y[0]

# Convert results to DataFrame
results_df = pd.DataFrame(data)

# Save results to a CSV file
results_df.to_csv("acetic_acid_concentration_over_50_years.csv", index=False)

# Print results
print(results_df)
