import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def connect_to_db():
    return psycopg2.connect(host='localhost', database='NBA Data', user='postgres', password='aqwertyuiop', port='5432')

def fetch_data(season_id):
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
    WHERE "SeasonID" = {season_id}
    """
    conn = connect_to_db()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

shot_data = fetch_data(27)

# Function to draw a basketball court
def draw_court(ax=None, color='black', lw=2):
    from matplotlib.patches import Circle, Rectangle, Arc

    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    # Create the paint
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False)
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color, fill=False)

    # Create free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180, linewidth=lw, color=color, fill=False)

    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color)

    # Restricted Zone
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw, color=color)

    # Three-point line
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw, color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color)

    # Center Court
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0, linewidth=lw, color=color)

    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw, bottom_free_throw,
                      restricted, corner_three_a, corner_three_b, three_arc, center_outer_arc, center_inner_arc]

    for element in court_elements:
        ax.add_patch(element)

    return ax

# Create the shot chart
plt.figure(figsize=(12, 11))
plt.scatter(shot_data['LOC_X'], shot_data['LOC_Y'], c=shot_data['SHOT_MADE_FLAG'], cmap='coolwarm', s=100, alpha=0.6)
draw_court(plt.gca())
plt.xlim(-250, 250)
plt.ylim(422.5, -47.5)
plt.title('NBA Shot Chart')
plt.show()
