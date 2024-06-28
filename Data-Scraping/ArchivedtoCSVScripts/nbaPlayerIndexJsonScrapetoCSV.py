import requests
import pandas as pd


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

params = {
    "LeagueID": "00",
    "Season": "2023-24",
    "Historical": "1",
    "TeamID": "0",
    "Country":"",
    "College": "",
    "DraftYear": "",
    "DraftPick": "",
    "PlayerPosition": "",
    "Height": "",
    "Weight": "",
    "Active": "",
    "AllStar": "",

}


# Send GET request
response = requests.get('https://stats.nba.com/stats/playerindex', headers=headers, params=params)

# Parse JSON response
data = response.json()

# Define function to extract nested data
def extract_data(data):
    headers = data['resultSets'][0]['headers']
    rows = data['resultSets'][0]['rowSet']
    return pd.DataFrame(rows, columns=headers)

# Extract data and convert to DataFrame
df = extract_data(data)

# Save DataFrame to CSV
df.to_csv('nba_player_index.csv', index=False)
print("Data has been successfully parsed and saved to 'nba_player_index.csv'")