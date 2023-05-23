import pandas as pd
import json
import os
from tqdm import tqdm
from datetime import timedelta
tqdm.pandas()

# Variables for levels, versions, and first days of the game
max_level = 80
versions = [8, 9]
first_days = 5
os_name = 'android'

# Check if the normalized file already exists
if os.path.exists('events_norm.csv'):
    df = pd.read_csv('events_norm.csv')
else:
    # Load data
    df = pd.read_csv('events.csv')

    # Parse JSON in 'event_json' column
    df['event_json'] = df['event_json'].progress_apply(json.loads)

    # Normalize data from 'event_json' into separate columns
    json_df = pd.json_normalize(df['event_json'])
    df = pd.concat([df, json_df], axis=1)

    # Save the normalized file
    df.to_csv('events_norm.csv', index=False)

# Convert 'event_datetime' to datetime
df['event_datetime'] = pd.to_datetime(df['event_datetime'])

# Filter by platform, if 'os_name' column exists
if 'os_name' in df.columns:
    df = df[df['os_name'] == os_name]

# Keep only the selected versions
df = df[df['app_version_name'].isin(versions)]

# Limit 'level_number' to the selected value
df = df[df['level_number'] <= max_level]

# Filter unique 'level_start' events for each user
df_unique_starts = df.drop_duplicates(subset=['appmetrica_device_id', 'event_name', 'level_number'])

# Filter users who started playing in the first 'first_days' days
start_date = df['event_datetime'].min()
end_date = start_date + timedelta(days=first_days)
df_unique_starts = df_unique_starts[(df_unique_starts['event_datetime'] >= start_date) & (df_unique_starts['event_datetime'] <= end_date)]

# Filter users who started the first level
df_unique_starts = df_unique_starts[df_unique_starts.groupby('appmetrica_device_id')['level_number'].transform('min') == 1]

# Count the number of users who started each level, for each version of the game
funnel_df = df_unique_starts[df_unique_starts['event_name'] == 'level_start'].groupby(['app_version_name', 'level_number']).size().reset_index(name='users')

# Transform DataFrame so that each version of the game is in its own column
funnel_df = funnel_df.pivot(index='level_number', columns='app_version_name', values='users').reset_index()

# Create dynamic column names
funnel_df.columns = ['level_num'] + [f'users_v{version}' for version in versions]

# Add columns with percentages
for version in versions:
    funnel_df[f'users_v{version}_percent'] = funnel_df[f'users_v{version}'] / funnel_df[f'users_v{version}'].loc[0] * 100

# Calculate winrate
level_start_df = df[df['event_name'] == 'level_start'].groupby(['app_version_name', 'level_number']).size().reset_index(name='starts')
level_finish_df = df[(df['event_name'] == 'level_finish') & (df['result'] == 'win')].groupby(['app_version_name', 'level_number']).size().reset_index(name='wins')
winrate_df = pd.merge(level_start_df, level_finish_df, on=['app_version_name', 'level_number'])
winrate_df['winrate'] = winrate_df['wins'] / winrate_df['starts']
winrate_df = winrate_df.pivot(index='level_number', columns='app_version_name', values='winrate').reset_index()
winrate_df.columns = ['level_num'] + [f'winrate_v{version}' for version in versions]

# Merge funnel and winrate dataframes
result_df = pd.merge(funnel_df, winrate_df, on='level_num')

# Calculate delta between levels
for version in versions:
    result_df[f'delta_v{version}'] = result_df[f'users_v{version}_percent'].shift() - result_df[f'users_v{version}_percent']
    result_df.loc[0, f'delta_v{version}'] = 0  # set delta for the first level to 0

# Save data to file
result_df.to_csv('funnel_and_winrate.csv', index=False)

print(result_df)
