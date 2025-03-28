import requests
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from unidecode import unidecode


#Function for connecting to postgres SQL Database
def connect_to_db():
    return psycopg2.connect(
        host='localhost',
        database='NBA Data',
        user='postgres',
        password='1234',
        port='5432'
    )

def create_table(conn, df):
    cursor = conn.cursor()
    # Check if the table already exists
    cursor.execute("SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename  = 'Player Shot Data');")
    if cursor.fetchone()[0]:
        print("Table already exists. Skipping creation.")
        return  # If table exists, skip the creation logic
    # If the table does not exist, proceed with creation
    else:
        # Generate SQL column definitions based on DataFrame dtypes
        columns = ",\n".join([f'"{col}" {infer_sql_type(df[col].dtype)}' for col in df.columns])
        sql_command = f"""
        CREATE TABLE "Player Shot Data" (
            id SERIAL PRIMARY KEY,
            {columns}
        );
        """
        print("Creating table with command:", sql_command)  # Debug print
        cursor.execute(sql_command)
        conn.commit()
        print("Table created successfully.")

def infer_sql_type(pd_type):
    #Map pandas dtype to SQL type
    if pd.api.types.is_integer_dtype(pd_type):
        return 'INTEGER'
    elif pd.api.types.is_float_dtype(pd_type):
        return 'FLOAT'
    elif pd.api.types.is_datetime64_dtype(pd_type):
        return 'TIMESTAMP'
    elif pd.api.types.is_string_dtype(pd_type):
        return 'TEXT'
    return 'TEXT'  # Default to TEXT for unexpected types

def preprocess_dataframe(df):
    """
    Preprocess the dataframe to remove accent marks from player names
    """
    # Remove accent marks from player names
    df['PLAYER_NAME'] = df['PLAYER_NAME'].apply(unidecode)
    return df

def insert_data(conn, df):
    # Preprocess the dataframe before insertion
    df = preprocess_dataframe(df)
    cursor = conn.cursor()
    # Ensure column names are properly quoted to handle any special characters or cases
    columns = ', '.join([f'"{col}"' for col in df.columns])
    # Prepare the SQL command template for execute_values
    sql_command = f'INSERT INTO "Player Shot Data" ({columns}) VALUES %s;'
    # Prepare data tuples from the DataFrame
    data_tuples = [tuple(x) for x in df.to_numpy()]
    # Use execute_values to insert multiple rows
    execute_values(cursor, sql_command, data_tuples)
    conn.commit()

# Function to generate season strings and IDs
def generate_seasons(start_year):
    seasons = []
    for year in range(start_year, 2024):
        season = f"{year}-{str(year + 1)[-2:]}"
        season_id = year - start_year + 1
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

conn = connect_to_db()
table_created = False

for season, season_id in generate_seasons(2023):
    for season_type in ['Regular Season', 'Playoffs']:
        params = {**static_params, 'Season': season, 'SeasonType': season_type}
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        result_set = data['resultSets'][0]
        df_headers = result_set['headers']
        rows = result_set['rowSet']
        df = pd.DataFrame(rows, columns=df_headers)
        df['Season'] = season
        df['SeasonID'] = season_id
        df['SeasonType'] = season_type
        # Create table on first successful data fetch
        if not table_created:
            create_table(conn, df)
            table_created = True
        insert_data(conn, df)

conn.close()
print("Data for all seasons has been successfully parsed and saved to the database.")
