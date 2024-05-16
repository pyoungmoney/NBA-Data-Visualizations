import psycopg2
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import Colormap as cm

def connect_to_db():
    return psycopg2.connect(host='localhost', database='NBA Data', user='postgres', password='aqwertyuiop', port='5432')

def fetch_player_shot_data(player_name, season_id, season_type):
    query = f"""
    With Player_Counts as(
    Select distinct "SHOT_ZONE_RANGE",
    "SHOT_ZONE_AREA",
    "SHOT_ZONE_BASIC",
    (COUNT("id") * 1.0) as "# of Shots",
    (SUM ("SHOT_MADE_FLAG") * 1.0) as "Shots Made"
    from "Player Shot Data"
    Where "PLAYER_NAME" = {player_name}
    and "Season" = {season_id}
    and "SeasonType" = {season_type}	
    GROUP BY "SHOT_ZONE_RANGE","SHOT_ZONE_AREA","SHOT_ZONE_BASIC"),

    Season_Counts as(
    Select distinct "SHOT_ZONE_RANGE",
    "SHOT_ZONE_AREA",
    "SHOT_ZONE_BASIC",
    (COUNT("id") * 1.0) as "# of Shots",
    (SUM ("SHOT_MADE_FLAG") * 1.0) as "Shots Made"
    from "Player Shot Data"
    Where "Season" = {season_id}
    and "PLAYER_NAME" <> {player_name}
    and "SeasonType" = {season_type}
    GROUP BY "SHOT_ZONE_RANGE","SHOT_ZONE_AREA","SHOT_ZONE_BASIC"),

    Aggregate_Percentages as(
    Select Player_Counts."SHOT_ZONE_RANGE",
    Player_Counts."SHOT_ZONE_AREA",
    Player_Counts."SHOT_ZONE_BASIC",
    Player_Counts."# of Shots",	
    Player_Counts."Shots Made",	
    Player_Counts."Shots Made" / Player_Counts."# of Shots" as "Player %",
    Season_Counts."Shots Made" / Season_Counts."# of Shots" as "Season %"
    FROM Player_Counts
    Join Season_Counts
    ON Player_Counts."SHOT_ZONE_RANGE" = Season_Counts."SHOT_ZONE_RANGE"
    And Player_Counts."SHOT_ZONE_AREA" = Season_Counts."SHOT_ZONE_AREA"
    And Player_Counts."SHOT_ZONE_BASIC" = Season_Counts."SHOT_ZONE_BASIC"),

    Player_Shots as(
    Select a."id",
    a."SHOT_MADE_FLAG",
    a."LOC_X",
    a."LOC_Y",
    a."SHOT_DISTANCE",
    a."SHOT_ZONE_RANGE",
    a."SHOT_ZONE_AREA",
    a."SHOT_ZONE_BASIC",
    b."# of Shots" as "Shots from Zone",
    b."Shots Made" as "Shots Made from Zone",
    b."Player %",
    b."Season %",
    (b."Player %" - b."Season %") as "Player % vs League Avg"
    FROM "Player Shot Data" a
    JOIN Aggregate_Percentages b
    ON  a."SHOT_ZONE_RANGE" =b."SHOT_ZONE_RANGE"
    And a."SHOT_ZONE_AREA" = b."SHOT_ZONE_AREA"
    And a."SHOT_ZONE_BASIC" =b."SHOT_ZONE_BASIC"
    Where "PLAYER_NAME" = {player_name}
    AND "Season" = {season_id}
    AND "SeasonType" = {season_type})

    Select *
    From Player_Shots
    """
    conn = connect_to_db()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

#Choose the player and season for the shot chart
player_name = "'Stephen Curry'"
season_id = "'2014-15'"
season_type = "'Regular Season'"
df_player_shot_data = fetch_player_shot_data(player_name, season_id, season_type)

def draw_court(ax, color):
    # Create the various parts of an NBA basketball court
    # Create the basketball hoop
    ax.add_artist(mpl.patches.Circle((0, 60), 15, facecolor='none', edgecolor=color, lw=2))

    # Create backboard
    ax.plot([-30, 30], [40, 40], linewidth=2, color=color)

    # Create the lines of the paint and free throw line
    ax.plot([-80, -80], [0, 190], linewidth=2, color=color)
    ax.plot([80, 80], [0, 190], linewidth=2, color=color)
    ax.plot([-60, -60], [0, 190], linewidth=2, color=color)
    ax.plot([60, 60], [0, 190], linewidth=2, color=color)
    ax.plot([-80, 80], [190, 190], linewidth=2, color=color)
    ax.add_artist(mpl.patches.Circle((0, 190), 60, facecolor='none', edgecolor=color, lw=2))

    # Three point line
    # Create the side 3pt lines
    ax.plot([-220, -220], [0, 140], linewidth=2, color=color)
    ax.plot([220, 220], [0, 140], linewidth=2, color=color)

    # 3pt arc
    ax.add_artist(mpl.patches.Arc((0, 140), 440, 315, theta1=0, theta2=180, facecolor='none', edgecolor=color, lw=2))

    # Remove ticks
    ax.set_xticks([])
    ax.set_yticks([])

    # Set axis limits
    ax.set_xlim(-250, 250)
    ax.set_ylim(0, 470)
    
    return ax

#Plot Shot Chart
#Set plot paramaters
mpl.rcParams['font.family'] = 'Avenir'
mpl.rcParams['font.size'] = 18
mpl.rcParams['axes.linewidth'] = 2

# Create figure and axes
fig = plt.figure(figsize=(10, 10))
ax = fig.add_axes([0, 0, 1, 1])

# Draw court
ax = draw_court(ax, 'black')

# Plot hexbin of shooting percentage difference
hb = ax.hexbin(df_player_shot_data['LOC_X'], df_player_shot_data['LOC_Y'] + 60, C=df_player_shot_data['Player % vs League Avg'], 
               gridsize=60, mincnt=2, cmap='RdYlBu_r', edgecolors='black', zorder=-5, 
               vmin=-0.15, vmax=0.15)

cb = fig.colorbar(hb, ax=ax, orientation='vertical')
cb.set_label('Shooting % Difference (Player - League)')

# Annotate player name and season
ax.text(0, 1.05, player_name + " Shot Chart " + season_id, transform=ax.transAxes, ha='left', va='baseline')

# Save and show figure
plt.style.use('fivethirtyeight')
plt.savefig('ShotChart.png', dpi=300, bbox_inches='tight')
plt.show()

df_player_shot_data.to_csv("Shot Chart Data.csv")