# Mobile Game Analytics with Yandex AppMetrica Data
This script is designed to work with data exported from Yandex AppMetrica, following the event integration recommendations of mobile game publisher Azur Games. The data is exported in CSV format from the Yandex AppMetrica website, from the data export section.
</br>
# Description
The script calculates the winrate and the funnel of level starts for each level of a mobile game, for selected versions of the game. The winrate is calculated as the number of successful level finishes (wins) divided by the number of level starts. The funnel of level starts is calculated as the number of unique users who started each level, as a percentage of the number of users who started the first level. The script also calculates the delta between levels, which is the difference in the percentage of users who started the current level and the previous level.
</br>
# Required Columns
The script requires the following columns to be included in the data export:
</br>
+ application_id: Identifier of the game. All rows are the same.
+ app_package_name: Package name. All rows are the same.
+ app_version_name: Version of the game. Can take different values.
+ event_name: Name of the event in the game. The main events of interest are level_finish and level_start.
+ event_json: Contains a JSON record of the event. This column needs to be expanded and the data normalized.
+ event_datetime: Time when the event occurred.
+ country_iso_code: Country of the player.
+ appmetrica_device_id: Personal unique identifier of the player. If there are multiple events with the same appmetrica_device_id, it means they come from the same player.
+ os_name: Operating system of the player's device (optional).
</br>
# Usage
Export your data from Yandex AppMetrica, making sure to include the required columns.
Run the script, specifying the maximum level, the versions of the game to compare, the number of first days of the game to consider, and the operating system (if applicable).
The script will output a CSV file named funnel_and_winrate.csv, containing the winrate, the funnel of level starts, and the delta between levels for each level of the game, for each selected version of the game.
