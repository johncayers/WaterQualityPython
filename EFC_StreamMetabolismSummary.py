import pandas as pd

# Load the data
data = pd.read_csv("EFC_StreamMetabolismSummary.csv")

# Display the first few rows of the dataframe
data.head()

# Make a plot of GPP.mean versus ER.mean with error bars defined by GPP.sd
# and ER.sd. Add a reference line with a slope of 1 and intercept of zero.

import matplotlib.pyplot as plt
import numpy as np

# Extract relevant data
x = data['GPP.mean']
y = data['ER.mean']
x_err = data['GPP.sd']
y_err = data['ER.sd']

# Define colorblind-friendly palette
colorblind_palette = ['#0173B2', '#DE8F05', '#029E73', '#D55E00', '#CC78BC', '#CA9161', '#FBAFE4']

# Ensure we have enough colors in our palette
devices = data['Device'].unique()
colors = plt.cm.viridis(np.linspace(0, 1, len(devices)))
if len(devices) > len(colorblind_palette):
    # If not, we will cycle the palette
    colorblind_palette = colorblind_palette * (len(devices) // len(colorblind_palette) + 1)

# Plotting
plt.figure(figsize=(10, 8))

# Plotting data points colored by device
for device, color in zip(devices, colorblind_palette):
    mask = data['Device'] == device
    plt.errorbar(x[mask], y[mask], xerr=x_err[mask], yerr=y_err[mask], fmt='o', label=device, color=color, capsize=5)

# Add reference line with slope of 1 and intercept of 0
xlims = plt.gca().get_xlim()
ylims = plt.gca().get_ylim()
max_limit = max(max(xlims), max(ylims))
plt.plot([0, max_limit], [0, max_limit], 'r--', label='y=x Reference Line')

plt.title('GPP.mean vs ER.mean with Error Bars (Colorblind-friendly)')
plt.xlabel('GPP.mean')
plt.ylabel('ER.mean')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Make a time series plot of GPP.mean, ER.mean, and NEP.mean with error bars
# defined by GPP.sd, ER.sd, and NEP.sd. x = "Date". Save the plot as a svg file.

# Convert "Date" column to datetime format
data['Date'] = pd.to_datetime(data['Date'])

# Verify the conversion
data['Date'].head()

# Define series and their respective errors
series = {
    "GPP.mean": "GPP.sd",
    "ER.mean": "ER.sd",
    "NEP.mean": "NEP.sd"
}

import seaborn as sns
sns.set()

plt.figure(figsize=(12, 8))

# Plot each series with error bars
for i, (key, value) in enumerate(series.items()):
    sns.lineplot(x=data['Date'], y=data[key], label=key, color=colors[i])
    plt.fill_between(data['Date'], data[key] - data[value], data[key] + data[value], color=colors[i], alpha=0.2)

plt.title('Time Series of GPP.mean, ER.mean, and NEP.mean with Error Bars')
plt.xlabel('Date')
plt.ylabel('Value')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Save the plot as an SVG file
output_path_ts_simple = "Time_Series_Plot.svg"
plt.savefig(output_path_ts_simple, format="svg")
plt.close()