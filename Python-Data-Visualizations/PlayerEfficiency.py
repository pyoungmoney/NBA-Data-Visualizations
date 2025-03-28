import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
from sqlalchemy import create_engine
import seaborn as sns
from adjustText import adjust_text

# Database connection parameters
db_params = {'host': 'localhost', 'database': 'NBA Data', 'user': 'postgres', 'password': '1234', 'port': '5432'}

# SQL query
query = """
With League_Avg as(
Select  "Season",
		avg("E_OFF_RATING") as "Avg E Off Rating",
		avg("OFF_RATING") as   "Avg Off Rating",
		avg("E_DEF_RATING") as "Avg E Def Rating",
		avg("DEF_RATING") as   "Avg Def Rating",
		avg("NET_RATING") as   "Avg Net Rating",
		avg("USG_PCT") as "Avg Usage Rate",
		Max("USG_PCT") as "Max Usage Rate"
From "Player Advanced Stats"
Where "Season" = '2022-23'
and "SeasonType" = 'Regular Season'
and "GP" > 55
Group By "Season"
),
Player_Data as(
Select  "PLAYER_ID",
		"PLAYER_NAME",
		"GP",
		"E_OFF_RATING",
		"OFF_RATING",
		"E_DEF_RATING",
		"DEF_RATING",
		"NET_RATING",
		"USG_PCT",
		"Season"
From "Player Advanced Stats"
Where "Season" = '2022-23'
and "SeasonType" = 'Regular Season'
and "GP" > 55)
Select  a."PLAYER_ID",
		a."PLAYER_NAME",
		a."Season",
		a."GP",
		a."E_OFF_RATING",
		a."OFF_RATING",
		a."E_DEF_RATING",
		a."DEF_RATING",
		a."NET_RATING",
		a."USG_PCT",
		b."Avg E Off Rating",
		b."Avg Off Rating",
		b."Avg E Def Rating",
		b."Avg Def Rating",
		b."Avg Net Rating",
		b."Avg Usage Rate",
		b."Max Usage Rate"
From Player_Data a
Join League_Avg b
on a."Season" = b."Season"
"""

def create_scatter_plot(data):
    # Get list of MVP vote recipients from 2022-23 season
    mvp_vote_recipients = [
        'Joel Embiid', 'Nikola Jokic', 'Giannis Antetokounmpo', 'Jayson Tatum',
        'Shai Gilgeous-Alexander', 'Donovan Mitchell', 'Domantas Sabonis',
        'Luka Doncic', 'Stephen Curry', 'Jimmy Butler', "De'Aaron Fox",
        'Jalen Brunson', 'Ja Morant'
    ]
    
    # Calculate the differences from league average
    data['OFF_RATING_DIFF'] = data['OFF_RATING'] - data['Avg Off Rating']
    data['DEF_RATING_DIFF'] = -(data['DEF_RATING'] - data['Avg Def Rating'])  # Negative because lower defensive rating is better

    # Create the plot
    plt.figure(figsize=(12, 8))
    
    # Set style to a valid theme
    plt.style.use('seaborn-v0_8')
    
    texts = []
    
    # Scale the usage rates relative to league average
    avg_usg = data['Avg Usage Rate'].iloc[0]  # Get league average usage rate
    min_usg = data['USG_PCT'].min()
    max_usg = data['Max Usage Rate'].iloc[0]  # Get league max usage rate
    
    # Set bubble size scaling
    min_size = 20
    max_size = 500
    
    # Function to determine color based on usage rate
    def get_usage_color(usg_pct):
        if usg_pct < 0.15:  # Under 15%
            return 'blue'
        elif usg_pct <= 0.30:  # 15-25%
            return 'green'
        else:  # Over 30%
            return 'red'
    
    # Create scatter plot with different styles based on MVP voting
    for idx, row in data.iterrows():
        player_name = row['PLAYER_NAME']
        usg_pct = row['USG_PCT']
        
        # Calculate size relative to league average
        size_factor = (usg_pct - min_usg) / (max_usg - min_usg)
        point_size = min_size + (size_factor * (max_size - min_size))
        
        # Get color based on usage rate
        color = get_usage_color(usg_pct)
        
        # Plot point
        plt.scatter(row['OFF_RATING_DIFF'], 
                   row['DEF_RATING_DIFF'],
                   s=point_size,
                   color=color,
                   alpha=0.3)
                   
        # Add text annotation if MVP or meets threshold
        if player_name in mvp_vote_recipients:
            texts.append(plt.text(row['OFF_RATING_DIFF'], 
                                row['DEF_RATING_DIFF'],
                                player_name,
                                weight='bold',
                                fontsize=8))
        elif abs(row['OFF_RATING_DIFF']) > 5 or abs(row['DEF_RATING_DIFF']) > 5:
            texts.append(plt.text(row['OFF_RATING_DIFF'], 
                                row['DEF_RATING_DIFF'],
                                player_name,
                                fontsize=8))
    
    # Update legend to show both size and color
    legend_elements = [
        plt.scatter([], [], s=min_size + (0.15 * max_size), color='blue', alpha=0.3, label='< 15% Usage'),
        plt.scatter([], [], s=min_size + (0.25 * max_size), color='green', alpha=0.3, label='15-30% Usage'),
        plt.scatter([], [], s=min_size + (0.35 * max_size), color='red', alpha=0.3, label='> 30% Usage')
    ]
    plt.legend(handles=legend_elements, title='Usage Rate', 
              loc='upper left', bbox_to_anchor=(1, 1))
    
    # Adjust text positions to minimize overlaps
    adjust_text(texts,
               arrowprops=dict(arrowstyle='->', color='black', lw=0.5),
               expand_points=(1.5, 1.5),
               force_points=(0.5, 0.5))
    
    # Add quadrant lines
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    plt.axvline(x=0, color='k', linestyle='--', alpha=0.3)
    
    # Get the axis limits to help position the labels in the corners
    x_min, x_max = plt.xlim()
    y_min, y_max = plt.ylim()
    
    # Add labels for quadrants - moved to corners with adjusted padding
    plt.text(x_max * 0.85, y_max * 0.85, 'Two-Way Stars\n(Good Offense, Good Defense)', 
             horizontalalignment='right', verticalalignment='top')
    plt.text(x_min * 0.85, y_max * 0.85, 'Defensive Specialists\n(Poor Offense, Good Defense)', 
             horizontalalignment='left', verticalalignment='top')
    plt.text(x_max * 0.85, y_min * 0.85, 'Offensive Specialists\n(Good Offense, Poor Defense)', 
             horizontalalignment='right', verticalalignment='bottom')
    plt.text(x_min * 0.85, y_min * 0.85, 'Below Average\n(Poor Offense, Poor Defense)', 
             horizontalalignment='left', verticalalignment='bottom')
    
    # Add labels and title
    plt.xlabel('Offensive Rating (Relative to League Average)')
    plt.ylabel('Defensive Rating (Relative to League Average)')
    plt.title('NBA Player Performance Quadrants (2022-23 Season)\nPlayers with 55+ Games Played', 
              pad=20)
    
    # Add note about bold names - adjusted positioning
    plt.text(0.02, -0.12, 
             'Note: Players in bold received MVP votes in 2022-23 season',
             transform=plt.gca().transAxes,  # Use axes coordinates
             ha='left',
             fontsize=8)
    
    # Add grid
    plt.grid(True, alpha=0.3)
    
    # Adjust layout with extra space for legend
    plt.tight_layout(rect=[0, 0.05, 1, 1])  # Leave space at right for legend
    
    return plt

def main():
    try:
        # Create database connection
        engine = create_engine(f'postgresql://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}/{db_params["database"]}')
        
        # Read data from database
        data = pd.read_sql_query(query, engine)
        
        # Create and save plot
        plt = create_scatter_plot(data)
        plt.savefig('nba_performance_quadrants.png', dpi=300, bbox_inches='tight')
        print("Plot has been saved as 'nba_performance_quadrants.png'")
        
        # Show plot
        plt.show()
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
if __name__ == "__main__":
    main()