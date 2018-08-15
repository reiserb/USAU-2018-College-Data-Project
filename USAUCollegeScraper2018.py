from bs4 import BeautifulSoup
import urllib
import csv
import time
import datetime
import re
import pandas as pd
from tqdm import tqdm

# Step 1: obtain links for each individual team page from rankings website.
# Rankings website: https://play.usaultimate.org/teams/events/team_rankings/?RankSet=College-Men
# Team pages format: https://play.usaultimate.org/teams/events/Eventteam/?TeamId= IDENTIFIER where IDENTIFIER is some long complicated string.
# Example: https://play.usaultimate.org/teams/events/Eventteam/?TeamId=07w4ZM%2buwH3CMfiMsFNpjjsRxwOklStysrZ6PcakvGY%3d (Carleton CUT 2018)

# Unfortunately, USAU uses Javascript to toggle pagination. Unless you're willing to upgrade to Selenium, making this work requires saving the rankings page in View-All mode locally. Yuck.

# Top 20, live version:
#r = urllib.request.urlopen("https://play.usaultimate.org/teams/events/team_rankings/?RankSet=College-Men").read()
#soup = BeautifulSoup(r, "lxml")

# All teams, stored version - save the rankings page after clicking the "View All" link as the file seen below in this directory.
with open("rawdata/collegemen2018final.html") as r:
#with open("rawdata/collegewomen2018final.html") as r:
    soup = BeautifulSoup(r, "lxml")

# Use regex matching to find the appropriate links
rawlinks = soup.find_all('a', {"id" : re.compile('CT_Main_0_gvList.*')})
ranktable = [link.parent.parent for link in rawlinks] # This contains all information available in the rankings table on this page.

baseurl = "https://play.usaultimate.org"
year = "2018"

# We'll store the results of the ranking table in records.
# Format is [Rank,name,ranking,level,gender,division,region,section,wins,losses,link]

records = []

for info in ranktable:
    found = info.find_all('td')
    temp = [x.text.strip() for x in found] + [found[1].a['href']]
    #should use baseurl as a prefix for last entry if doing live version
    records.append(temp)

# Step 2: build database of games. Follow each link to each teampage, record the relevant data, store it to file
objection = []

with open("USAUCollegeMen2018Games.csv","w+",newline='') as csv_file:
#with open("USAUCollegeWomen2018Games.csv","w+",newline='') as csv_file:
    writer = csv.writer(csv_file)
    for record in tqdm(records):
        games = []
        teamname = record[1]
        r = urllib.request.urlopen(record[-1]).read()
        subsoup = BeautifulSoup(r,"lxml")
        schedtab = subsoup.find("table", {"class":"schedule_table", "id":"CT_Right_0_gvEventScheduleScores"})
        if schedtab == None: #There's one of these, not sure how it happened, but error handling is important.
            print("Error, records for ", record[1], " are blank")
            continue
        entries = schedtab.find_all("tr",{"valign":"top"})

        tournament = ""
        for entry in entries:
            if "class" in entry.td.attrs:
                # If "class" is present in the tag attributes, it's a row that tells us the tournament heading.
                # Set tournament to be the name of the tournament so we can sort by that later.
                tournament = entry.text.strip()
            else:
                # Otherwise it's a specific game from that tournament
                date = entry.td.text.strip() # formatted as fullmonth date
                if date == "N/A": #format to YYYY-MM-DD, should exclude weird cases. Can't get accurate timestamps without scraping tournament pages, would also need timezone ID probably, seems bad.
                    #print(record,entry)
                    objection.append([record,entry])
                else:
                    date = datetime.datetime.strptime(date+", "+year,"%B %d, %Y").strftime("%Y-%m-%d")
                score = entry.td.next_sibling.text.strip() # this is formatted as us - them
                t1score = score[:2].strip() #Preserves possibility of W/F or W/L - can deal with those later in data, don't want to just discard now.
                t2score = score[-2:].strip()
                opponent = entry.td.next_sibling.next_sibling.text.strip()
                if teamname < opponent: # Avoid duplicating games by only adding games where teamname is lexicographically first
                    #writer.writerow([date,tournament,teamname,opponent,t1score,t2score])
                    games.append([date,tournament,teamname,opponent,t1score,t2score])
        for game in games:
            writer.writerow(game)

#print(objection)

# Now USAUCollegeMen2018Games.csv contains all games played, formatted as YYYY-MM-DD,Tournament,Team1,Team2,Score1,Score2
# Still some cleaning left to do before getting it ready to get picked up by Pandas.
# Need to remove games ending 0-0, scores of n/,/a, games where one participant is N/A, any tournament marked (Cancelled), make determination about what to do with W/L and W/F
# Pawn this off to analysis scripts, since thqt data might actually be useful for looking at forfeit rates or something.
# Full run takes about 30m on college men's dataset, 15m on college women's dataset
# Note: women's data from Humboldt State at Flat Tail Womens was messed up, fixed manually.

"""
2018-01-27,Flat Tail Women's Tournament 2018,Humboldt State,Oregon,1,13
2018-01-28,Flat Tail Women's Tournament 2018,Humboldt State,Portland,12,9
2018-01-27,Flat Tail Women's Tournament 2018,Humboldt State,Puget Sound,7,8
2018-01-27,Flat Tail Women's Tournament 2018,Humboldt State,Oregon State,5,13
2018-01-28,Flat Tail Women's Tournament 2018,Humboldt State,Lewis & Clark,9,14
2018-01-27,Flat Tail Women's Tournament 2018,Humboldt State,Lewis & Clark,7,8
"""
