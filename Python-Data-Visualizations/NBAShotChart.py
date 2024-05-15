import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc

# Constants for the dimensions of an NBA court
COURT_LENGTH = 94
COURT_WIDTH = 50

def connect_to_db():
    return psycopg2.connect(host='localhost', database='NBA Data', user='postgres', password='aqwertyuiop', port='5432')

def fetch_data(player_id, season_id):
    query = f"""
    Select "id",
    "SHOT_MADE_FLAG",
    "LOC_X",
    "LOC_Y",
    "SHOT_DISTANCE",
    "SHOT_ZONE_RANGE",
    "SHOT_ZONE_AREA",
    "SHOT_ZONE_BASIC"
    From "Player Shot Data"
    Where "PLAYER_ID" = {player_id}
    AND "SeasonID" = {season_id}
    """
    conn = connect_to_db()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def draw_court(ax=None, color='black', lw=2, outer_lines=False):
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False, zorder=5)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color, zorder=5)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                          fill=False, zorder=5)
    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                          fill=False, zorder=5)

    # Create free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False, zorder=5)
    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed', zorder=5)
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color, zorder=5)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw,
                               color=color, zorder=5)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color, zorder=5)
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the 
    # threes
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color, zorder=5)

    # Center Court
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color, zorder=5)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color, zorder=5)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc, center_outer_arc,
                      center_inner_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                color=color, fill=False, zorder=5)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax

def plot_shots(df):
    plt.figure(figsize=(12, 11))
    ax = plt.gca()
    draw_court(outer_lines=True)

    """# Plot made shots as green circles and missed shots as red Xs
    for i, row in df.iterrows():
        if row['SHOT_MADE_FLAG'] == 1:
            ax.plot(row['LOC_X'], row['LOC_Y'], 'go')
        else:
            ax.plot(row['LOC_X'], row['LOC_Y'], 'rx')"""
    
    ax.hexbin(x='LOC_X',y='LOC_Y',data=df,gridsize=40,edgecolors='Orange',cmap='Blues')
    plt.title('Luka Doncic 2022-23 Shot Chart')
    plt.xlabel('Court Length (feet)')
    plt.ylabel('Court Width (feet)')
    plt.xlim(-250,250)
    plt.ylim(-47.5,422.5)
    plt.show()

def main():
    # Replace 1629029 with the desired player_id and 27 with the season_id you are interested in
    player_id = 1629029
    season_id = 27
    df = fetch_data(player_id, season_id)
    plot_shots(df)

if __name__ == "__main__":
    main()
