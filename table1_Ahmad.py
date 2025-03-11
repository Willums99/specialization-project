import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# Constants
R = 8.314  # J/(mol*K), gas constant
A = 1.03e5  # Adjusted pre-exponential factor
Ea = 87e3  # Adjusted activation energy in J/mol

# Initial concentrations (mol/m^3)
ROAc_0 = 13403.6
H2O_0 = 2137.2
HOAc_0 = 5.2

# High temperature for simulation
high_temp = 273.15 + 70  # 70°C in Kelvin

# Time points for 114 days
t_high_temp = np.linspace(0, 114, 1000)  # Higher resolution

# Differential equation for degradation
def damage_model(HOAc, t, ROAc_0, H2O_0):
    k = A * np.exp(-Ea / (R * high_temp))
    ROAc = ROAc_0 - HOAc
    H2O = H2O_0 - HOAc
    dHOAc_dt = k * ROAc * H2O * HOAc
    return dHOAc_dt

# Solve the ODE
HOAc_t = odeint(damage_model, HOAc_0, t_high_temp, args=(ROAc_0, H2O_0))

# Convert to free acidity (mL of 0.1 M NaOH/g)
free_acidity = HOAc_t.flatten() / 130

# Define experimental points from Table 1
time_points = [0, 30, 60, 75, 90, 114]
experimental_free_acidity = [0.04, 0.1, 0.25, 0.6, 1.3, 4.6]

# Plot simulation vs. experimental data
plt.figure(figsize=(10, 6))
plt.plot(t_high_temp, free_acidity, label="Simulated Free Acidity", color="blue")
plt.scatter(time_points, experimental_free_acidity, color="red", label="Experimental Data")
plt.xlabel("Time (days)")
plt.ylabel("Free Acidity (mL of 0.1 M NaOH/g)")
plt.title("Degradation of Cellulose Triacetate at 70°C")
plt.legend()
plt.grid()
plt.show()
