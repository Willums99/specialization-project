'''
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# Constants
R = 8.314  # J/(mol*K), gas constant
A = 1.03e-3  # Pre-exponential factor (example value)
Ea = 70.734e3  # Activation energy in J/mol (example value)

# Initial conditions for concentrations (example values)
ROAc_0 = 13403.6  # Initial concentration of acetyl groups (mol/m^3)
H2O_0 = 2137.2    # Initial concentration of water (mol/m^3)
HOAc_0 = 0.04     # Initial acetic acid concentration (mol/m^3)

# Temperature in Kelvin (example for room temperature)
T = 273.15 + 70  # 20°C

# Calculate the rate constant using the Arrhenius equation
def rate_constant(A, Ea, T):
    return A * np.exp(-Ea / (R * T))

k = rate_constant(A, Ea, T)

# Differential equation
def damage_model(HOAc, t, k, ROAc_0, H2O_0):
    ROAc = ROAc_0 - HOAc
    H2O = H2O_0 - HOAc
    dHOAc_dt = k * ROAc * H2O * HOAc
    return dHOAc_dt

# Time points (0 to 10000 days, for example)
t = np.linspace(0, 10000, 1000)

# Solve the differential equation
HOAc_t = odeint(damage_model, HOAc_0, t, args=(k, ROAc_0, H2O_0))

# Print final and sample concentrations over time
print("Final calculated concentration:", HOAc_t[-1])
print("Sample concentrations over time:", HOAc_t[::1000])  # Print every 1000th value

# Plot the results
plt.plot(t, HOAc_t, label=f'Acetic Acid Concentration at {T-273.15}°C')
plt.xlabel('Time (days)')
plt.ylabel('Concentration of Acetic Acid (mol/m^3)')
plt.title('Degradation of Cellulose Triacetate (CTA) over Time')
plt.legend()
plt.show()
'''
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# Constants
R = 8.314  # J/(mol*K), gas constant
A = 1.03e-3  # Pre-exponential factor for Case A (check paper for exact value)
Ea = 87.864e3  # Activation energy in J/mol for Case A at 50% RH

# Adjust initial concentrations based on Case A from Table 6
ROAc_0 = 13356.8  # mol/m^3
H2O_0 = 2137.2  # mol/m^3
HOAc_0 = 5.2  # Initial acetic acid concentration, mol/m^3

# Define total initial amounts
a = ROAc_0 + HOAc_0
b = H2O_0 + HOAc_0

# Temperature for Case A (35°C converted to Kelvin)
T = 293.15 + 35  

# Calculate the rate constant using the Arrhenius equation
def rate_constant(A, Ea, T):
    return A * np.exp(-Ea / (R * T))

k = rate_constant(A, Ea, T)

# Differential equation
def damage_model(HOAc, t, k, a, b):
    dHOAc_dt = k * (a - HOAc) * (b - HOAc) * HOAc
    return dHOAc_dt

# Time points for the simulation (0 to 547 days for 18 months)
t = np.linspace(0, 547, 548)  # Daily points

# Solve the differential equation
HOAc_t = odeint(damage_model, HOAc_0, t, args=(k, a, b))

# Convert output for graph comparison (assuming density and film thickness for conversion)
density_CTA = 1.4  # g/cm^3
thickness_CTA = 0.01  # cm (example, adjust based on actual film thickness)
volume_CTA = 1.0  # Assume 1 cm^3 for simplicity

# Convert concentration from mol/m^3 to ml of 0.1 M NaOH per g of film
# Molar mass of NaOH is 40 g/mol, thus 0.1 M NaOH is 0.1 mol/L or 0.1 mmol/mL
# 1 mol of acetic acid requires 1 mol of NaOH to neutralize
converted_HOAc = HOAc_t * (1000 / density_CTA) * (1 / 0.1)  # Convert mol/m^3 to ml of 0.1 M NaOH per gram of film

# Plot the results
plt.plot(t / 30, converted_HOAc, label='Case A Acetic Acid Concentration')
plt.xlabel('Time (months)')
plt.ylabel('Free Acidity (ml of 0.1 M NaOH / g film base)')
plt.title('Degradation of Cellulose Triacetate (CTA) in Case A over 18 Months')
plt.legend()
plt.show()

