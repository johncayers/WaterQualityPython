import pandas as pd
import numpy as np

# Load the first few rows of each file to inspect
file_names = [
    "StreamPulseData/all_sp_data01.csv",
    "StreamPulseData/all_sp_data02.csv"
   # "StreamPulseData/all_sp_data03.csv",
    # "StreamPulseData/all_sp_data04.csv",
    # "StreamPulseData/all_sp_data05.csv"
]

file_previews = {f"all_sp_data0{i+1}.csv": pd.read_csv(file_names[i], nrows=5) for i in range(len(file_names))}
file_previews

# Concatenate the files vertically
# I need to specify the data type using the dtype option
# If not specified, "value" is 'float64' but every other field has type 'object'
# I still get errors. Should I use "col#" instead of actual field name? No, still doesn't work.
# Try in Anaconda Cloud JupyterLab notebook. Or should I be using numpy instead of Pandas?
#The error occurs because the `dtype` parameter is not a valid argument for the `concat()` function in pandas. The `dtype` parameter is used for specifying the data types of the columns when reading a CSV file using `pd.read_csv()`, not for the `concat()` function.
# merged_records = pd.concat([pd.read_csv(file) for file in file_names], dtype={'regionID': str, 'siteID': str, 'dateTimeUTC': str, 'variable': str, 'value': float, 'flagID': str, 'flagComment': str}, ignore_index=True)
data01 = pd.read_csv('StreamPulseData/all_sp_data01.csv')
data02 = pd.read_csv('StreamPulseData/all_sp_data02.csv')
merged_records = pd.concat(['data01','data02'], ignore_index=True)

# Display the first few rows of the merged dataframe
merged_records.head()

# Filter out the records based on the given conditions
filtered_records = merged_records[~((merged_records['flagID'] == "Questionable") & (merged_records['flagComment'].notna()))]

# Display the first few rows of the filtered dataframe
filtered_records.head()

# Drop the specified columns
filtered_records = filtered_records.drop(columns=['flagID', 'flagComment'])

# Display the first few rows of the dataframe after dropping the columns
filtered_records.head()

# List of variables to select
selected_variables = [
    'DO_mgL', 'Depth_m', 'SpecCond_uScm', 'Turbidity_NTU', 'WaterTemp_C',
    'pH', 'Discharge_m3s', 'Light_PAR', 'Nitrate_mgL', 'Turbidity_FNU',
    'AirPres_kPa', 'Light_lux', 'satDO_mgL', 'AirTemp_C'
]

# Filter the records based on the list of variables
selected_records = filtered_records[filtered_records['variable'].isin(selected_variables)]

# Display the first few rows of the selected dataframe
selected_records.head()

# Pivot the data
pivoted_data = selected_records.pivot_table(index=['dateTimeUTC', 'regionID', 'siteID'],
                                            columns='variable',
                                            values='value',
                                            aggfunc='first').reset_index()

# Display the first few rows of the pivoted dataframe
pivoted_data.head()

# Filter the records based on the specified conditions
filtered_pivoted_data = pivoted_data.dropna(subset=['DO_mgL', 'WaterTemp_C'], how='any')
filtered_pivoted_data = filtered_pivoted_data[filtered_pivoted_data[['Light_PAR', 'Light_lux']].notna().any(axis=1)]

# Display the first few rows of the filtered pivoted dataframe
filtered_pivoted_data.head()

# Create the 'RegionSiteID' field by concatenating 'regionID' and 'siteID'
filtered_pivoted_data['RegionSiteID'] = filtered_pivoted_data['regionID'] + filtered_pivoted_data['siteID']

# Display the first few rows of the dataframe after adding the new field
filtered_pivoted_data.head()

# Load the 'Sites' table
sites = pd.read_csv("StreamPulseData/Sites.csv")

# Create the 'RegionSiteID' field by concatenating 'regionID' and 'siteID'
sites['RegionSiteID'] = sites['regionID'] + sites['siteID']

# Display the first few rows of the 'Sites' dataframe after adding the new field
sites.head()

# Filter out rows with non-finite longitude values
sites = sites[sites['longitude'].notna() & np.isfinite(sites['longitude'])]

# Determine approximate time zone based on longitude
sites['ApproxTimeZone'] = (sites['longitude'] // 15).astype(int) * -1

# Display the first few rows of the 'Sites' dataframe after adding the approximate time zone
sites[['regionID', 'siteID', 'longitude', 'ApproxTimeZone']].head()

# Compute the static UTC offset based on the approximate time zones
sites['UTC_Offset'] = sites['ApproxTimeZone'].apply(lambda x: f"{x:03d}:00")

# Display the first few rows of the 'Sites' dataframe after adding the UTC offset
sites[['regionID', 'siteID', 'longitude', 'ApproxTimeZone', 'UTC_Offset']].head()

# Perform a left join between 'filtered_pivoted_data' and 'Sites' using the 'RegionSiteID' field
joined_data = pd.merge(filtered_pivoted_data, sites, on='RegionSiteID', how='left', suffixes=('', '_sites'))

# Display the first few rows of the joined dataframe
joined_data.head()

# Convert 'dateTimeUTC' to datetime object
joined_data['dateTimeUTC'] = pd.to_datetime(joined_data['dateTimeUTC'], errors='coerce')

# Extract hours from 'UTC_Offset' and convert to timedelta
joined_data['Offset'] = pd.to_timedelta(joined_data['UTC_Offset'].str.extract('(-?\d+):')[0].astype(float), unit='h')

# Calculate 'LocalDateTime' by adding the offset to 'dateTimeUTC'
joined_data['LocalDateTime'] = joined_data['dateTimeUTC'] + joined_data['Offset']

# Display the first few rows of the dataframe after adding the 'LocalDateTime' field
joined_data[['dateTimeUTC', 'UTC_Offset', 'LocalDateTime']].head()

def adjust_for_dst(row):
    # Define DST start and end for Northern Hemisphere
    dst_start_north = pd.Timestamp(year=row['LocalDateTime'].year, month=3, day=8 + (6 - pd.Timestamp(year=row['LocalDateTime'].year, month=3, day=8).weekday()))
    dst_end_north = pd.Timestamp(year=row['LocalDateTime'].year, month=11, day=1 + (6 - pd.Timestamp(year=row['LocalDateTime'].year, month=11, day=1).weekday()))

    # Define DST start and end for Southern Hemisphere
    dst_start_south = pd.Timestamp(year=row['LocalDateTime'].year, month=10, day=1 + (6 - pd.Timestamp(year=row['LocalDateTime'].year, month=10, day=1).weekday()))
    dst_end_south = pd.Timestamp(year=row['LocalDateTime'].year, month=4, day=1 + (6 - pd.Timestamp(year=row['LocalDateTime'].year, month=4, day=1).weekday()))

    # Adjust for DST based on hemisphere and date
    if row['longitude'] > 0:  # Northern Hemisphere
        if dst_start_north <= row['LocalDateTime'] < dst_end_north:
            return row['LocalDateTime'] + pd.Timedelta(hours=1)
    else:  # Southern Hemisphere
        if dst_start_south <= row['LocalDateTime'] < dst_end_south:
            return row['LocalDateTime'] + pd.Timedelta(hours=1)

    return row['LocalDateTime']

# Apply the DST adjustment function
joined_data['LocalDateTimeAdj'] = joined_data.apply(adjust_for_dst, axis=1)

# Display the first few rows of the dataframe after adding the 'LocalDateTimeAdj' field
joined_data[['dateTimeUTC', 'LocalDateTime', 'LocalDateTimeAdj']].head()

# Extract 'Date' and 'Time' from 'LocalDateTimeAdj'
joined_data['Date'] = joined_data['LocalDateTimeAdj'].dt.date
joined_data['Time'] = joined_data['LocalDateTimeAdj'].dt.time

# Display the first few rows of the dataframe after adding the 'Date' and 'Time' fields
joined_data[['LocalDateTimeAdj', 'Date', 'Time']].head()

# Filter out records where 'embargoDaysRemaining' is greater than 0
filtered_data = joined_data[joined_data['embargoDaysRemaining'] <= 0]

# Display the first few rows of the filtered dataframe
filtered_data.head()

# Save the filtered joined data to a new CSV file
file_path = "StreamPulseData/JoinedData.csv"
filtered_data.to_csv(file_path, index=False)

file_path