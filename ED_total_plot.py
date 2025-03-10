import numpy as np
import matplotlib.pyplot as plt

# Define the years for the x-axis
years = np.arange(2015, 2066)

# Sample total energy demand data (replace with your actual data)
# These are placeholders. Replace these with your actual calculated values
total_ed_good_trondheim = np.random.uniform(1000, 2000, len(years))  # Replace with actual data
total_ed_good_rome = np.random.uniform(2000, 3000, len(years))  # Replace with actual data
total_ed_average_trondheim = np.random.uniform(1500, 2500, len(years))  # Replace with actual data
total_ed_average_rome = np.random.uniform(2500, 3500, len(years))  # Replace with actual data
total_ed_bad_trondheim = np.random.uniform(2000, 3000, len(years))  # Replace with actual data
total_ed_bad_rome = np.random.uniform(3000, 4000, len(years))  # Replace with actual data

# Create figure and axes for the plots
fig, ax = plt.subplots(3, 1, figsize=(10, 15))

# Plot the Good scenario comparison
ax[0].plot(years, total_ed_good_trondheim, label="Trondheim (Good)", color="blue")
ax[0].plot(years, total_ed_good_rome, label="Rome (Good)", color="orange")
ax[0].set_ylabel('Total Energy Demand (kWh)')
ax[0].set_title('Total Energy Demand (Good Scenario)')
ax[0].grid(True)
ax[0].legend()

# Plot the Average scenario comparison
ax[1].plot(years, total_ed_average_trondheim, label="Trondheim (Average)", color="blue")
ax[1].plot(years, total_ed_average_rome, label="Rome (Average)", color="orange")
ax[1].set_ylabel('Total Energy Demand (kWh)')
ax[1].set_title('Total Energy Demand (Average Scenario)')
ax[1].grid(True)
ax[1].legend()

# Plot the Bad scenario comparison
ax[2].plot(years, total_ed_bad_trondheim, label="Trondheim (Bad)", color="blue")
ax[2].plot(years, total_ed_bad_rome, label="Rome (Bad)", color="orange")
ax[2].set_ylabel('Total Energy Demand (kWh)')
ax[2].set_title('Total Energy Demand (Bad Scenario)')
ax[2].grid(True)
ax[2].legend()

# Display the plots
plt.tight_layout()
plt.show()
