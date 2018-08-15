from bs4 import BeautifulSoup
import urllib
import csv
import time
import datetime
import re
import pandas as pd
from tqdm import tqdm

# Goal: build a reference table of all the previous rankings from the past USAU college season.
# Save all expanded rankings pages to rawdata/ as collegegenderdate.html, date formatted as in dates below.

dates = ["2018final","20180403","20180328","20180321","20180314","20180307"]
rdates = ["2018-06-03","2018-04-03","2018-03-28","2018-03-21","2018-03-14","2018-03-07"]
genders = ["Men","Women"]

for gender in genders:
    teamdict = {}
    for date in dates:
        if date == dates[0]:
            rdate = "2018-06-03"
        else:
            rdate = date[:4]+"-"+date[4:6]+"-"+date[6:]

        with open("rawdata/college"+gender.lower()+date+".html") as r:
            soup = BeautifulSoup(r, "lxml")
        rawlinks = soup.find_all('a', {"id" : re.compile('CT_Main_0_gvList.*')})
        ranktable = [link.parent.parent for link in rawlinks] # This contains all information available in the rankings table on this page.

        # Format is [Rank,name,ranking,level,gender,division,region,section,wins,losses,link]
        # Assemble in to dictionary to put off possibility of appearing in some ranking sets and not others.

        for info in ranktable:
            found = info.find_all('td')
            temp = [x.text.strip() for x in found]# + [found[1].a['href']]
            rank, name, ranking, level, rgender, division, region, section, wins, losses = temp
            if name in teamdict:
                teamdict[name][rdate] = {"Rank":rank, "Ranking":ranking,"Wins":wins,"Losses":losses}
            else:
                teamdict[name] = {rdate:{"Rank":rank, "Ranking":ranking,"Wins":wins,"Losses":losses},"Level":level,"Gender":rgender,"Division":division,"Region":region,"Section":section}
    #print(teamdict)
    #Now, go through dictionary and write to file.
    with open("USAUCollege"+ gender +"2018Ranks.csv","w+", newline='') as csv_file:
        writer = csv.writer(csv_file)
        for team in tqdm(teamdict):
            writable = [team,teamdict[team]["Level"],teamdict[team]["Gender"],teamdict[team]["Division"],teamdict[team]["Region"],teamdict[team]["Section"]]
            for rdate in rdates[::-1]:
                if rdate in teamdict[team]:
                    writable += [rdate,teamdict[team][rdate]["Rank"],teamdict[team][rdate]["Ranking"],teamdict[team][rdate]["Wins"],teamdict[team][rdate]["Losses"]]
                else:
                    writable += [rdate,"N/A","N/A","N/A","N/A"]
            writer.writerow(writable)

# csv files now contain rows in the following format:
# Teamname,Level,Gender,Division,Region,Section,[Date,Rank,Ranking,Wins,Losses]
# where [] indicates repeated a few times. Rank means #1,#2,#3,etc, Ranking means ranking points.
