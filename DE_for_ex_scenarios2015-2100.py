import numpy as np
from datetime import datetime, timedelta
from scipy.integrate import solve_ivp

# Constants
R = 8.314  # Ideal gas constant (J/(mol·K))
A = 0.00103  # Pre-exponential factor (mol^-2 m^6 s^-1)
Ea = 70734  # Activation energy (J/mol)
ROAc0 = 13403.6  # Initial acetyl concentration (mol/m³)
H2O0 = 2137.2  # Initial water concentration (mol/m³)
HOAc0 = 52  # Initial acetic acid concentration (mol/m³)
start_date = datetime(2015, 1, 1)
end_date = datetime(2100, 1, 1)  # Updated to 2100
cold_storage_temp = 275.15  # Cold storage temperature (K)
season_temps = {"winter": 273.15 + 20, "summer": 273.15 + 25, "spring/autumn": 273.15 + 18} # Italy temp

# Exhibition and storage durations
exhibition_lengths = [7, 14, 21, 28]  # In days
cold_storage_lengths = [6, 12, 18, 24, 36]  # In months

# Determine the season based on the date
def get_season(date):
    month = date.month
    if month in [12, 1, 2]:
        return "winter"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "spring/autumn"

# Define the rate constant
def rate_constant(T):
    return A * np.exp(-Ea / (R * T))

# Differential equation for acetic acid concentration
def acetic_acid_concentration(t, HOAc, k):
    ROAc = ROAc0 - HOAc
    H2O = H2O0 - HOAc
    dHOAc_dt = k * ROAc * H2O * HOAc
    return dHOAc_dt

# Simulate degradation
def simulate_degradation(exhibition_days, cold_storage_months):
    date = start_date
    HOAc = HOAc0
    while date < end_date:
        # Exhibition phase
        season = get_season(date)
        T_exhibition = season_temps[season]
        k_exhibition = rate_constant(T_exhibition)
        exhibition_duration = exhibition_days * 24 * 3600  # Convert days to seconds
        solution_exhibition = solve_ivp(
            acetic_acid_concentration, [0, exhibition_duration], [HOAc],
            args=(k_exhibition,), method='RK45', max_step=1e5
        )
        HOAc = solution_exhibition.y[0][-1]
        date += timedelta(days=exhibition_days)

        # Cold storage phase
        k_cold_storage = rate_constant(cold_storage_temp)
        storage_duration = cold_storage_months * 30 * 24 * 3600  # Convert months to seconds
        solution_storage = solve_ivp(
            acetic_acid_concentration, [0, storage_duration], [HOAc],
            args=(k_cold_storage,), method='RK45', max_step=1e5
        )
        HOAc = solution_storage.y[0][-1]
        date += timedelta(days=cold_storage_months * 30)
    return HOAc

# Run simulations and populate the matrix
results = np.zeros((len(cold_storage_lengths), len(exhibition_lengths)))

for i, cold_months in enumerate(cold_storage_lengths):
    for j, exhibition_days in enumerate(exhibition_lengths):
        print(f"Simulating for {cold_months} months cold storage and {exhibition_days} days exhibition...")
        results[i, j] = simulate_degradation(exhibition_days, cold_months)

# Output the results as a matrix
print("\t" + "\t".join([f"{days//7} week(s)" for days in exhibition_lengths]))
for i, cold_months in enumerate(cold_storage_lengths):
    print(f"{cold_months} months\t" + "\t".join(f"{results[i, j]:.6f}" for j in range(len(exhibition_lengths))))

