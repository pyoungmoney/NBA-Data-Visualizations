import requests
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Function to generate season strings and IDs
def generate_seasons(start_year):
    seasons = []
    for year in range(start_year, 2023):  # Up to the 2022-23 season
        season = f"{year}-{str(year + 1)[-2:]}"
        season_id = year - start_year + 1  # Calculate SeasonID
        seasons.append((season, season_id))
    return seasons

# Base headers and URL
headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Origin': 'https://www.nba.com',
    'Referer': 'https://www.nba.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}
url = 'https://stats.nba.com/stats/leaguedashplayerstats'

# Parameters that stay constant
static_params = {
    'College': '',
    'Conference': '',
    'Country': '',
    'DateFrom': '',
    'DateTo': '',
    'Division': '',
    'DraftPick': '',
    'DraftYear': '',
    'GameScope': '',
    'GameSegment': '',
    'Height': '',
    'ISTRound': '',
    'LastNGames': '0',
    'LeagueID': '00',
    'Location': '',
    'MeasureType': 'Base',
    'Month': '0',
    'OpponentTeamID': '0',
    'Outcome': '',
    'PORound': '0',
    'PaceAdjust': 'N',
    'PerMode': 'PerGame',
    'Period': '0',
    'PlayerExperience': '',
    'PlayerPosition': '',
    'PlusMinus': 'N',
    'Rank': 'N',
    'SeasonSegment': '',
    'ShotClockRange': '',
    'StarterBench': '',
    'TeamID': '0',
    'VsConference': '',
    'VsDivision': '',
    'Weight': '',
}

# DataFrame to store all data
all_data = pd.DataFrame()

# Loop through each season and season type
for season, season_id in generate_seasons(1996):
    for season_type in ['Regular Season', 'Playoffs']:
        params = {**static_params, 'Season': season, 'SeasonType': season_type}
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        result_set = data['resultSets'][0]
        df_headers = result_set['headers']  # Rename to avoid conflict
        rows = result_set['rowSet']
        df = pd.DataFrame(rows, columns=df_headers)
        df['Season'] = season
        df['SeasonID'] = season_id
        df['SeasonType'] = season_type
        all_data = pd.concat([all_data, df], ignore_index=True)


# Save all data to a single CSV file
all_data.to_csv('nba_player_traditional_stats_1996_to_2023.csv', index=False)
print("Data for all seasons from 1996-97 to 2022-23 for both Regular Season and Playoffs has been successfully parsed and saved to 'nba_player_traditional_stats_1996_to_2023.csv'")
