import requests
import pandas as pd

# Function to generate season strings and IDs
def generate_seasons(start_year):
    seasons = []
    for year in range(start_year, 2023):  # Up to the 2022-23 season
        season = f"{year}-{str(year + 1)[-2:]}"
        season_id = year - start_year + 1  # Calculate SeasonID
        seasons.append((season, season_id))
    return seasons

# Define headers and parameters for the request as specified
headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
    'Connection': 'keep-alive',
    'Origin': 'https://www.nba.com',
    'Referer': 'https://www.nba.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}

url = 'https://stats.nba.com/stats/shotchartdetail'

static_params = {
    "AheadBehind": "",
    "CFID": "",
    "CFPARAMS": "",
    "ClutchTime": "",
    "Conference": "",
    "ContextFilter": "",
    "ContextMeasure": "FGA",
    "DateFrom": "",
    "DateTo": "",
    "Division": "",
    "EndPeriod": "0",
    "EndRange": "0",
    "GROUP_ID": "",
    "GameEventID": "",
    "GameID": "",
    "GameSegment": "",
    "GroupID": "",
    "GroupMode": "",
    "GroupQuantity": "5",
    "LastNGames": "0",
    "LeagueID": "00",
    "Location": "",
    "Month": "0",
    "OnOff": "",
    "OppPlayerID": "",
    "OpponentTeamID": "0",
    "Outcome": "",
    "PORound": "0",
    "Period": "0",
    "PlayerID": "0",
    "PlayerID1": "",
    "PlayerID2": "",
    "PlayerID3": "",
    "PlayerID4": "",
    "PlayerID5": "",
    "PlayerPosition": "",
    "PointDiff": "",
    "Position": "",
    "RangeType": "0",
    "RookieYear": "" ,
    "SeasonSegment": "",
    "ShotClockRange": "",
    "StartPeriod": "0",
    "StartRange": "0",
    "StarterBench": "",
    "TeamID": "0",
    "VsConference": "",
    "VsDivision": "",
    "VsPlayerID1": "",
    "VsPlayerID2": "",
    "VsPlayerID3": "",
    "VsPlayerID4": "",
    "VsPlayerID5": "",
    "VsTeamID": "",

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
all_data.to_csv('nba_shot_data_1996_to_2023.csv', index=False)
print("Data for all shots from 1996-97 to 2022-23 for both Regular Season and Playoffs has been successfully parsed and saved to 'nba_shot_data_1996_to_2023.csv'")


# Send GET request
response = requests.get('https://stats.nba.com/stats/shotchartdetail', headers=headers, params=params)