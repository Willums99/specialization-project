import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Constants for the model
R = 8.314  # Ideal gas constant (J/(mol·K))
A = 0.00103  # Pre-exponential factor (mol^-2 m^6 s^-1)
Ea = 70734  # Activation energy (J/mol)

# Time span for simulation (18 months in seconds)
time_span = (0, 18 * 30 * 24 * 3600)  # 18 months in seconds

# Define the ODE for the model
def acetic_acid_concentration(t, HOAc, ROAc0, H2O0, k):
    ROAc = ROAc0 - HOAc
    H2O = H2O0 - HOAc
    dHOAc_dt = k * ROAc * H2O * HOAc
    return dHOAc_dt

# Define the cases with their specific parameters
cases = {
    "Case A": {"HOAc0": 52, "T": 308.15, "ROAc0": 13356.8, "H2O0": 2137.2},
    "Case B": {"HOAc0": 59.8, "T": 308.15, "ROAc0": 13349.0, "H2O0": 1605.2},
    "Case C": {"HOAc0": 52, "T": 308.15, "ROAc0": 13356.8, "H2O0": 1010.0}
}

results = {}
for case, params in cases.items():
    # Extract parameters for the case
    HOAc0 = params["HOAc0"]
    T = params["T"]
    ROAc0 = params["ROAc0"]
    H2O0 = params["H2O0"]
    
    # Calculate the rate constant
    k = A * np.exp(-Ea / (R * T))
    
    # Solve the ODE
    solution = solve_ivp(
        acetic_acid_concentration, time_span, [HOAc0],
        args=(ROAc0, H2O0, k), method='RK45', t_eval=np.linspace(time_span[0], time_span[1], 100)
    )
    results[case] = solution

# Plot the results
plt.figure(figsize=(10, 6))
for case, solution in results.items():
    time_months = solution.t / (30 * 24 * 3600)  # Convert time to months
    plt.plot(time_months, solution.y[0], label=case)

# Add labels, title, and legend
plt.title("Increase in Acetic Acid Concentration in CTA Over Time")
plt.xlabel("Time (months)")
plt.ylabel("Acetic Acid Concentration (mol/m³)")
plt.legend()
plt.grid()
plt.show()

