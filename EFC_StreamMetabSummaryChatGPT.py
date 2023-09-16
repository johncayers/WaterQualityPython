import pandas as pd

# Now that the file has been uploaded, let's read the CSV file using pandas
data = pd.read_csv('EFC_StreamMetabolismSummary.csv', parse_dates=["Date"], dayfirst=False)

# Display the first few rows of the dataset as a summary (similar to skim in R)
data.head()

import matplotlib.pyplot as plt

# Calculate error bars for plotting
data['xlow'] = data['GPP.mean'] - data['GPP.sd']
data['xhigh'] = data['GPP.mean'] + data['GPP.sd']
data['ylow'] = data['ER.mean'] - data['ER.sd']
data['yhigh'] = data['ER.mean'] + data['ER.sd']

# Plotting using matplotlib
plt.figure(figsize=(10, 8))
colors = {'MiniDOT': 'blue', 'Exo2': 'orange'}
for device, color in colors.items():
    subset = data[data['Device'] == device]
    plt.errorbar(subset['GPP.mean'], subset['ER.mean'],
                 xerr=[subset['GPP.mean'] - subset['xlow'], subset['xhigh'] - subset['GPP.mean']],
                 yerr=[subset['ER.mean'] - subset['ylow'], subset['yhigh'] - subset['ER.mean']],
                 fmt='o', color=color, label=device)

plt.plot([0, 40], [0, 40], color='gray', linestyle='--')  # Add line with slope 1
plt.xlim(0, 40)
plt.ylim(0, 40)
plt.xlabel("GPP mean (mg O2 L-1 d-1)")
plt.ylabel("ER mean (mg O2 L-1 d-1)")
plt.legend()
plt.title("GPP vs ER with Error Bars")
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.tight_layout()
# plt.show()

# Save the plot
plt.savefig('EFC_GPPvsER_ErrorBars.svg', format='svg')

# Make a time series plot of GPP.mean, ER.mean, and NEP.mean with error bars
# defined by GPP.sd, ER.sd, and NEP.sd. x = "Date". Save the plot as a svg file.

import seaborn as sns

# Set up the colorblind-friendly palette
sns.set_palette("colorblind")

# Plotting the time series
plt.figure(figsize=(14, 8))
plt.errorbar(data['Date'], data['GPP.mean'], yerr=data['GPP.sd'], label='GPP.mean', capsize=5, fmt='-o')
plt.errorbar(data['Date'], data['ER.mean'], yerr=data['ER.sd'], label='ER.mean', capsize=5, fmt='-o')
plt.errorbar(data['Date'], data['NEP.mean'], yerr=data['NEP.sd'], label='NEP.mean', capsize=5, fmt='-o')

# Formatting the plot
plt.title('Time Series Plot of GPP.mean, ER.mean, and NEP.mean with Error Bars')
plt.xlabel('Date')
plt.ylabel('Value')
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.xticks(rotation=45)
# plt.show()

plt.savefig('Time_Series_Plot.svg', format="svg")
plt.close()