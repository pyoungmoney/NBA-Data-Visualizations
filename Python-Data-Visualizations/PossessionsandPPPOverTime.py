import pandas as pd
import matplotlib.pyplot as plt
import psycopg2

# Setup local database connection
def connect_to_db():
    return psycopg2.connect(host='localhost', database='NBA Data', user='postgres', password='aqwertyuiop', port='5432')

# Query advanced team data and store into a dataframe
def fetch_data():
    query = """
    SELECT AVG("PACE") as "Possessions per game",
           AVG("OFF_RATING" / 100) as "Points per Possession",
           AVG ("EFG_PCT") as "Effective FG %",
           AVG ("TS_PCT") as "True Shooting %",
           "Season",
           "SeasonType"
    FROM "Team Advanced Stats"
    GROUP BY "Season", "SeasonType"
    ORDER BY "Season", "SeasonType";
    """
    conn = connect_to_db()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def plot_data(df):
    # Filter data for Regular Season and Playoffs
    regular_season = df[df['SeasonType'] == 'Regular Season']
    playoffs = df[df['SeasonType'] == 'Playoffs']

    # Plotting Possessions per Game
    plt.figure(figsize=(12, 6))
    plt.plot(regular_season['Season'], regular_season['Possessions per game'], label='Regular Season', marker='o')
    plt.plot(playoffs['Season'], playoffs['Possessions per game'], label='Playoffs', marker='o')
    plt.title('NBA Possessions per Game Over Seasons')
    plt.xlabel('Season')
    plt.ylabel('Possessions per Game')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('PossessionsPerGame.png', bbox_inches='tight')

    # Plotting Points per Possession
    plt.figure(figsize=(12, 6))
    plt.plot(regular_season['Season'], regular_season['Points per Possession'], label='Regular Season', marker='o')
    plt.plot(playoffs['Season'], playoffs['Points per Possession'], label='Playoffs', marker='o')
    plt.title('NBA Points per Possession Over Seasons')
    plt.xlabel('Season')
    plt.ylabel('Points per Possession')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('PointsPerPossession.png', bbox_inches='tight')

    # Plotting Effective FG %
    plt.figure(figsize=(12, 6))
    plt.plot(regular_season['Season'], regular_season['Effective FG %'], label='Regular Season', marker='o')
    plt.plot(playoffs['Season'], playoffs['Effective FG %'], label='Playoffs', marker='o')
    plt.title('NBA Effective FG % Over Seasons')
    plt.xlabel('Season')
    plt.ylabel('Effective FG %')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('EffectiveFG.png', bbox_inches='tight')

    # Plotting True Shooting %
    plt.figure(figsize=(12, 6))
    plt.plot(regular_season['Season'], regular_season['True Shooting %'], label='Regular Season', marker='o')
    plt.plot(playoffs['Season'], playoffs['True Shooting %'], label='Playoffs', marker='o')
    plt.title('True Shooting % Over Seasons')
    plt.xlabel('Season')
    plt.ylabel('True Shooting %')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('TrueShooting.png', bbox_inches='tight')


def main():
    df = fetch_data()
    plot_data(df)

if __name__ == "__main__":
    main()
