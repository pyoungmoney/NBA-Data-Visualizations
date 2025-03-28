import psycopg2
import pandas as pd
import numpy as np
import matplotlib as mpb
import matplotlib.pyplot as plt
from matplotlib import  offsetbox as osb
from matplotlib.patches import RegularPolygon

#Choose the player and season for the shot chart
player_name = "'LeBron James'"
season_id = "'2012-13'"
season_type = "'Regular Season'"

# Set our color map
mymap = mpb.cm.coolwarm

# Setup local database connection
def connect_to_db():
    return psycopg2.connect(host='localhost', database='NBA Data', user='postgres', password='1234', port='5432')

# Query shot data and store into a dataframe
def fetch_player_shot_data(player_name, season_id, season_type):
    query = f"""
    With Player_Counts as(
    Select distinct "SHOT_ZONE_RANGE",
    "SHOT_ZONE_AREA",
    "SHOT_ZONE_BASIC",
    (COUNT("id") * 1.0) as "# of Shots",
    (SUM ("SHOT_MADE_FLAG") * 1.0) as "Shots Made",
	(SUM ("SHOT_MADE_FLAG") * 1.0) / (COUNT("id") * 1.0) as "Player %"
    from "Player Shot Data"
    Where "PLAYER_NAME" = {player_name}
    and "Season" = {season_id}
    and "SeasonType" = {season_type}
	and "SHOT_ZONE_RANGE" <> 'Back Court Shot'
    GROUP BY "SHOT_ZONE_RANGE","SHOT_ZONE_AREA","SHOT_ZONE_BASIC"),

    Season_Counts as(
    Select distinct "SHOT_ZONE_RANGE",
    "SHOT_ZONE_AREA",
    "SHOT_ZONE_BASIC",
	(SUM ("SHOT_MADE_FLAG") * 1.0) / (COUNT("id") * 1.0) as "Season %"	
    from "Player Shot Data"
    Where "Season" = {season_id}
    and "PLAYER_NAME" <> {player_name}
    and "SeasonType" = {season_type}
	and "SHOT_ZONE_RANGE" <> 'Back Court Shot'
    GROUP BY "SHOT_ZONE_RANGE","SHOT_ZONE_AREA","SHOT_ZONE_BASIC"),

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
    b."Player %"
    from "Player Shot Data" a
	JOIN Player_Counts b
    ON  a."SHOT_ZONE_RANGE" = b."SHOT_ZONE_RANGE"
    And a."SHOT_ZONE_AREA" = b."SHOT_ZONE_AREA"
    And a."SHOT_ZONE_BASIC" = b."SHOT_ZONE_BASIC" 
    Where a."PLAYER_NAME" = {player_name}
    AND a."Season" = {season_id}
    AND a."SeasonType" = {season_type}
	and a."SHOT_ZONE_RANGE" <> 'Back Court Shot'	
	),

    Player_Season_Shots as(
	Select a."id",
    a."SHOT_MADE_FLAG",
    a."LOC_X",
    a."LOC_Y",
    a."SHOT_DISTANCE",
    a."SHOT_ZONE_RANGE",
    a."SHOT_ZONE_AREA",
    a."SHOT_ZONE_BASIC",
    c."Season %"
    from "Player Shot Data" a
	JOIN Season_Counts c
	ON  a."SHOT_ZONE_RANGE" = c."SHOT_ZONE_RANGE"
    And a."SHOT_ZONE_AREA" = c."SHOT_ZONE_AREA"
    And a."SHOT_ZONE_BASIC" = c."SHOT_ZONE_BASIC"
    Where a."PLAYER_NAME" = {player_name}
    AND a."Season" = {season_id}
    AND a."SeasonType" = {season_type}
	and a."SHOT_ZONE_RANGE" <> 'Back Court Shot'
)

	Select a."id", 
    a."SHOT_MADE_FLAG",
    a."LOC_X",
    a."LOC_Y",
    a."SHOT_DISTANCE",
    a."SHOT_ZONE_RANGE",
    a."SHOT_ZONE_AREA",
    a."SHOT_ZONE_BASIC",
    a."Shots from Zone",
    a."Shots Made from Zone",
    a."Player %",
	d."Season %",
	Round(a."Player %" - d."Season %", 2) as "Player % vs League Avg"
    from Player_Shots a
	JOIN Player_Season_Shots d
	ON a.id = d.id
	and a."SHOT_ZONE_RANGE" = d."SHOT_ZONE_RANGE"
    And a."SHOT_ZONE_AREA" = d."SHOT_ZONE_AREA"
    And a."SHOT_ZONE_BASIC" = d."SHOT_ZONE_BASIC"
    """
    conn = connect_to_db()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Plot shots
def shooting_plot(shot_df, player_name, season_id, plot_size=(12,12), gridNum=30):

    (numShots, shotNumber), shot_count_all, hexbin_data = find_shootingPcts(shot_df, gridNum)

    color_hexes = shot_df['Player % vs League Avg']

    fig = plt.figure(figsize=plot_size)

    cmap = mymap

    ax = plt.axes([0.05, 0.15, 0.81, 0.775]) 

    ax.set_facecolor('#0C232E')

    draw_court(ax, outer_lines=False)

    plt.xlim(-250,250)
    plt.ylim(370, -30)
    
             
    max_radius_perc = 1.0
    max_rad_multiplier = 100.0/max_radius_perc

    area_multiplier = (3./4.)

    color_values = []

    # i is the bin#, and shots is the number of shots for that bin
    for i, shots in enumerate(numShots): 
        x,y = shotNumber.get_offsets()[i]
        color_value = hexbin_data.get((x, y), 0)
        

        color_value_norm = (color_value + 0.15) / 0.3  # Normalize for colormap ranging from -0.15 to 0.15
        color_value_norm = max(min(color_value_norm, 1.0), 0.0)
        color_values.append((x, y, color_value, color_value_norm))

        hexes = RegularPolygon(
            shotNumber.get_offsets()[i], #x/y coords
            numVertices=6, 
            radius=(295/gridNum)*((max_rad_multiplier*((shotNumber.get_array()[i]))/shot_count_all)**(area_multiplier)), 
            color=cmap(color_value_norm),
            alpha=0.95, 
            fill=True)

        # setting a maximum radius for our bins at 295 (personal preference)
        if hexes.radius > 295/gridNum: 
            hexes.radius = 295/gridNum
        ax.add_patch(hexes)

        # Save the color values to a CSV file
        color_values_df = pd.DataFrame(color_values, columns=['X','Y','Color Value %', 'Color Value'])
        color_values_df.to_csv('color_values.csv', index=False)

    
    # we want to have 4 ticks in this legend so we iterate through 4 items
    for i in range(0,4):
        base_rad = max_radius_perc/4

        # the x,y coords for our patch (the first coordinate is (-205,415), and then we move up and left for each addition coordinate)
        patch_x = -205-(10*i)
        patch_y = 365-(14*i)

        # specifying the size of our hexagon in the frequency legend
        patch_rad = (299.9/gridNum)*((base_rad+(base_rad*i))**(area_multiplier))
        patch_perc = base_rad+(i*base_rad)

        # the x,y coords for our text
        text_x = patch_x + patch_rad + 2
        text_y = patch_y

        patch_axes = (patch_x, patch_y)

        # the text will be slightly different for our maximum sized hexagon,
        if i < 3:
            text_text = ' %s%% of Attempted Shots' % ('%.2f' % patch_perc)
        else:
            text_text = '$\geq$%s%% of Attempted Shots' %(str(patch_perc))
        
        # draw the hexagon. the color=map(eff_fg_all_float/100) makes the hexagons in the legend the same color as the player's overall eFG%
        patch = RegularPolygon(patch_axes, numVertices=6, radius=patch_rad, color=cmap(0.5), alpha=0.95, fill=True)
        ax.add_patch(patch)

        # add the text for the hexagon
        ax.text(text_x, text_y, text_text, fontsize=12, horizontalalignment='left', verticalalignment='center', family='DejaVu Sans', color='white', fontweight='bold')

    # Add a title to our frequency legend (the x/y coords are hardcoded).
    # Again, the color=map(eff_fg_all_float/100) makes the hexagons in the legend the same color as the player's overall eFG%
    ax.text(-235, 310, 'Zone Frequencies', fontsize = 15, horizontalalignment='left', verticalalignment='bottom', family='DejaVu Sans', color='white', fontweight='bold')

    # Add a title to our chart (just the player's name)
    chart_title = player_name + " Shot Chart " + season_id
    ax.text(31.25,-40, chart_title, fontsize=29, horizontalalignment='center', verticalalignment='bottom', family='DejaVu Sans', color='white', fontweight='bold')

    # adding a color bar for reference
    ax2 = fig.add_axes([0.875, 0.15, 0.04, 0.775])
    cb = mpb.colorbar.ColorbarBase(ax2,cmap=cmap, orientation='vertical')
    cbytick_obj = plt.getp(cb.ax.axes, 'yticklabels')
    plt.setp(cbytick_obj, color='white', fontweight='bold')
    cb.set_label('Shooting Percentahe Compared to League Avg', family='DejaVu Sans', color='white', fontweight='bold', labelpad=-4, fontsize=14)
    cb.set_ticks([0.0, 0.25, 0.5, 0.75, 1.0])
    cb.set_ticklabels(['$\mathbf{\leq}$-15%', '-7.5%', '0%', '7.5%', '$\mathbf{\geq}$15%'])

    plt.savefig('ShotChart.png', facecolor='#26373F', edgecolor='black')
    plt.clf()

def find_shootingPcts(shot_df, gridNum):
    x = shot_df.LOC_X[shot_df['LOC_Y']<425.1]
    y = shot_df.LOC_Y[shot_df['LOC_Y']<425.1]
    
    # Grabbing the x and y coords, for all made shots
    x_made = shot_df.LOC_X[(shot_df['SHOT_MADE_FLAG']==1) & (shot_df['LOC_Y']<425.1)]
    y_made = shot_df.LOC_Y[(shot_df['SHOT_MADE_FLAG']==1) & (shot_df['LOC_Y']<425.1)]
    
    #compute number of shots made and taken from each hexbin location
    hb_shot = plt.hexbin(x, y, gridsize=gridNum, mincnt= 4, extent=(-250,250,425,-50));
    plt.close()
    
    #compute number of shots
    numShots = hb_shot.get_array()

    # Create a dictionary to map hexbin to shot zone info
    hexbin_data = {}
    for i, (x, y) in enumerate(hb_shot.get_offsets()):
        # Find all shots within this hexbin
        hexbin_shots = shot_df[(shot_df.LOC_X.between(x - 7.5, x + 7.5)) & (shot_df.LOC_Y.between(y - 7.5, y + 7.5))]
        if not hexbin_shots.empty:
            # Get the most common SHOT_ZONE_AREA and SHOT_ZONE_BASIC
            shot_zone_area = hexbin_shots['SHOT_ZONE_AREA'].mode().iloc[0]
            shot_zone_basic = hexbin_shots['SHOT_ZONE_BASIC'].mode().iloc[0]
            # Get the corresponding Player % vs League Avg
            color_value = shot_df[(shot_df['SHOT_ZONE_AREA'] == shot_zone_area) & (shot_df['SHOT_ZONE_BASIC'] == shot_zone_basic)]['Player % vs League Avg'].iloc[0]
        else:
            color_value = 0
        hexbin_data[(x, y)] = color_value

    shot_count_all = len(shot_df.index)

    # Returning all values
    return (numShots, hb_shot), shot_count_all, hexbin_data

def draw_court(ax=None, color='white', lw=2, outer_lines=False):
    from matplotlib.patches import Circle, Rectangle, Arc
    if ax is None:
        ax = plt.gca()
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                          fill=False)
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                          fill=False)
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color)
    corner_three_a = Rectangle((-220, -50.0), 0, 140, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((219.75, -50.0), 0, 140, linewidth=lw, color=color)
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color)
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc, center_outer_arc,
                      center_inner_arc]
    if outer_lines:
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    for element in court_elements:
        ax.add_patch(element)
    
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.set_yticks([])
    return ax 

df_player_shot_data = fetch_player_shot_data(player_name, season_id, season_type)
shooting_plot(df_player_shot_data, player_name, season_id)