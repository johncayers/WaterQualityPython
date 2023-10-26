import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point

# Load the CSV file into a pandas DataFrame
data = pd.read_csv('Survey.csv', encoding='ISO-8859-1')

# Display the first few rows of the DataFrame
data.head()

# Convert DataFrame to a GeoDataFrame
geometry = [Point(xy) for xy in zip(data['Longitude'], data['Latitude'])]
gdf = gpd.GeoDataFrame(data, geometry=geometry)

# Plot the map
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# Plotting
fig, ax = plt.subplots(figsize=(10, 10))
world.plot(ax=ax, color='lightgrey')
gdf.plot(ax=ax, markersize=5)
ax.set_title("Survey Data Points")
plt.show()

# import numpy as np

# Normalize the ODOmgPerL values for color mapping and sizing
norm = plt.Normalize(data['ODOmgPerL'].min(), data['ODOmgPerL'].max())

# Create a colormap
cmap = plt.get_cmap('viridis')

# Plotting
fig, ax = plt.subplots(figsize=(10, 10))
world.plot(ax=ax, color='lightgrey')

gdf.plot(ax=ax, markersize=data['ODOmgPerL']*10,
         color=cmap(norm(data['ODOmgPerL'].values)),
         legend=True)

# Add colorbar
cax = fig.add_axes([0.9, 0.1, 0.03, 0.8])
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
fig.colorbar(sm, cax=cax, orientation='vertical')

ax.set_title("Survey Data Points - ODOmgPerL")
plt.show()

# Determine the bounding box using the maximum and minimum values of latitude and longitude
minx, miny, maxx, maxy = (data['Longitude'].min(), data['Latitude'].min(),
                          data['Longitude'].max(), data['Latitude'].max())

# Plotting the zoomed-in map
fig, ax = plt.subplots(figsize=(10, 10))
world.plot(ax=ax, color='lightgrey')
gdf.plot(ax=ax, markersize=data['ODOmgPerL']*10,
         color=cmap(norm(data['ODOmgPerL'].values)),
         legend=True)

# Set the axis limits to the bounding box coordinates to zoom in
ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy)

# Add colorbar
cax = fig.add_axes([0.9, 0.1, 0.03, 0.8])
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
fig.colorbar(sm, cax=cax, orientation='vertical')

ax.set_title("Zoomed-in Survey Data Points - ODOmgPerL")
plt.show()
