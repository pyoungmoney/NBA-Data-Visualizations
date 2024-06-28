# NBA-Data-Visualizations

<h3>The goal of this project is to:</h3>
<b>(1)</b> Use python to scrape the NBA's publically available data\
<b>(2)</b> Save that data into a local SQL database\
<b>(3)</b> Use python and R to create data visualizations from these datasets\

<h3>Currently the repository is broken up into 2 main folders:</h3>
<b>(1) Data-Scraping</b> — This folder contains the python scripts used to access the NBA's public database and then create SQL tables on a locally hosted database to store this data. There is also a folder of python scripts I previously used to save this data into CSV files.\
<b>(2) Python-Data-Visualizations</b> — This folder contains the python scripts used to pull data from the local SQL database and then create various visualizations. The latest visualizations created from these scripts are saved as PNG files within this folder.


<h3>About the data:</h3>
Currently, I have 6 separate SQL tables of NBA data stored within my local database. Those tables are:\
<b>(1) Player Index</b> — This table assigns a unique PERSON_ID to every player in NBA history and also includes various player specific data such as first/last name, jersey number, college, draft year, and seasons played.\
<b>(2) Player Traditional Stats</b> — This table contains season specific per game statistics for every player and every season from 1996-97 to 2022-23. Statistics are limited to counting stats such as points/gm, steals/gm, minutes/gm, etc.\
<b>(3) Player Advanced Stats</b> — This table contains season specific percentages and per game statistics for every player and every season from 1996-97 to 2022-23. Statistics are limited to advanced stats such as assist to turnover ratio, effective field goal percentage, usage rate, etc.\
<b>(4) Team Traditional Stats</b> — This table contains season specific per game statistics for every team and every season from 1996-97 to 2022-23. Statistics are limited to counting stats such as points/gm, steals/gm, turnovers/gm, etc.\
<b>(5) Team Advanced Stats</b> — This table contains season specific percentages and per game statistics for every team and every season from 1996-97 to 2022-23. Statistics are limited to advanced stats such as offensive rating, offensive rebounding rate, pace (possessions per game), etc.\
<b>(6) Player Shot Data</b> — This table contains location data for every shot taken by every player for every season from 1996-97 to 2022-23. Location data includes x/y coordinates on the court, shot zones, shot distance, etc.

<h3>Current python generated visualizations:</h3>
<b>(1) Lebron James Shot Chart Visualization</b> — This visualization maps every location LeBron took ≥4 shots from in the 2012-13 season (his best statistical shooting season). Shots are plotted using hexagons of varying size depending on the volume of shots taken from that location. The hexagons use a colorscale to indicate how well LeBron shot from that location compared to the league average shooting performance from that same location.<br>


<i>Data Source: <a href="https://stats.nba.com/" target="_blank">Stats.NBA</a></i>
