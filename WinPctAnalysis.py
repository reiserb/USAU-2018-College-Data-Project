import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import random

# Next goal: build a database of games tagged with rankings of teams at the time they played the games. Explore this data to try to figure out win probability based on USAU rankings number.

# Step 1: create methods to attach rankings for each team when the game was played to the game.

rdates = ["2018-06-03","2018-04-03","2018-03-28","2018-03-21","2018-03-14","2018-03-07"][::-1]

# Return the index of the most recent entry of rdates so that inputdate is in (rdate[i],rdate[i+1]]. Return -1 if there is no such index.
def previous_rankdate(inputdate,rdates):
    if inputdate < rdates[0] or inputdate > rdates[-1]:
        return -1
    for i in range(len(rdates)-1):
        if rdates[i+1] >= inputdate > rdates[i]:
            return i
    return -1

# Given a game formatted as [date,tournament,team1,team2,score1,score2], append [rank1,rank2] where ranki was the current rank of teami at the time the game took place.
def decorate_rankings(game,rdates,team1rankings,team2rankings):
    date = game[0]
    dateindex = previous_rankdate(date,rdates)
    if dateindex == -1:
        decorator = ["N/A","N/A"]
    else:
        decorator = [team1rankings[8+5*dateindex],team2rankings[8+5*dateindex]]
    return game + decorator

# Step 2: import games and rankings from file.

division = "College"
year = "2018"
gender = "Women"
#gender = "Men"

#load rankings from file here
rankingsDict = {} #format: "Teamname" : [rankings file content]

with open("USAU"+division+gender+year+"Ranks.csv","r") as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        if row != []:
            rankingsDict[row[0]] = row
            #Leftover from old version which didn't fix newlines. Keeping here just in case.
            #BTW, newline fix is use newline='' in writer. Eliminated issue here. Probably Windows-based.

#load games from file here
games = [] #format: [date,tournament,team1,team2,score1,score2]

with open("USAU"+division+gender+year+"Games.csv","r") as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        if row != []:
            games.append(row)
            #Leftover from old version which didn't fix newlines. Keeping here just in case.
            #BTW, newline fix is use newline='' in writer. Eliminated issue here. Probably Windows-based.

#put decorated games here
dec_games = [] #format: [date,tournament,team1,team2,score1,score2,rank1,rank2], cleaned to be valid
errornames = set()
scoreless = set()

#Things to watch out for: 0-0, n/,/a, a participant being N/A, cancelled tournaments, W/L, W/F
#Other things to watch out for: games records B teams as "Northwestern[B]"", while ranks has them as "Northwestern B"
#Some teams in games are not in rankings.
for game in tqdm(games):
    date, tournament, team1, team2, score1, score2 = game
    if date == "N/A" or team1 == "N/A" or team2 == "N/A" or "(Cancelled)" in tournament:
        continue
    if score1 in {"","W","L","F","n/"} or score2 in {"","W","L","F","/a"}:
        continue
    if team1[-3:] == "[B]":
        team1 = team1[:-3] + " B"
    if team2[-3:] == "[B]":
        team2 = team2[:-3] + " B"
    if team1[-3:] == "[C]":
        team1 = team1[:-3] + " C"
    if team2[-3:] == "[C]":
        team2 = team2[:-3] + " C"
    if team1 not in rankingsDict:
        errornames.add(team1)
        continue
    if team2 not in rankingsDict:
        errornames.add(team2)
        continue
    if score1==score2:#=="0":
        scoreless.add(tuple(game))
        continue
    team1rankings, team2rankings = rankingsDict[team1], rankingsDict[team2]
    rankedgame = decorate_rankings(game,rdates,team1rankings,team2rankings)
    if rankedgame[-1] != "N/A" and rankedgame[-2] != "N/A":
        dec_games.append(rankedgame)

#print(dec_games[:20])
print(len(dec_games))
#print(scoreless)

#print(dec_games[-20:])
#print(errornames)
#print(scoreless)

"""plottablegames = []
for game in dec_games:
    temp = [int(x) for x in game[-4:]]
    if temp[0] < temp[1]:
        temp[0],temp[1],temp[2],temp[3] = temp[1],temp[0],temp[3],temp[2]
    if temp[0] == temp[1]:
        continue
    plottablegames.append(temp)

print(len(plottablegames),plottablegames[:20])

#cool, now I have all the decorated games in plottable games listed as [win score,loss score,win rating,loss rating]. Time to figure out how to plot this!

windata = [game[2] for game in plottablegames]
lossdata = [game[3] for game in plottablegames]

plt.plot(lossdata,windata,"r.")
plt.plot([min(windata+lossdata),max(windata+lossdata)],[min(windata+lossdata),max(windata+lossdata)])
plt.show()
"""

"""
for i in range(100):
    n = random.randint(0,len(windata)-1)
    if windata[n] >= lossdata[n]:
        print(str(windata[n])+","+str(lossdata[n])+",1")
    else:
        print(str(lossdata[n])+","+str(windata[n])+",0")
    #print(str(windata[n]-lossdata[n])+","+str(int(windata[n]-lossdata[n]>=0)))
"""

# Here's a potentially stupid worry: what format do I want to submit the data to the regressor in?
# Should be Team1 rating, Team2 rating, Team1Win?
# Or should it be higherrating, lowerrating, higherteamwin?
# I think the second is right, because we're asking for a function which takes two ratings and produces win probability
# and we think there may be a bias towards or away from the higher rating.

# So we need to prepare our data as highrank,lowrank and our outcomes as highrankwin
def prep_game(game):
    #goal: return [higherrank,lowerrank,higherrankwin]
    temp = [int(x) for x in game[-4:]] # format [team1score,team2score,team1rank,team2rank]
    #if temp[3] > temp[2]:
        #temp[0],temp[1],temp[2],temp[3] = temp[1],temp[0],temp[3],temp[2]
        # format now [higherrankscore,lowerrankscore,higherrank,lowerrank]
    #returnable = [temp[2]-temp[3],int(temp[0]>temp[1])]
    returnable = [temp[2],temp[3],int(temp[0]>temp[1])]
    return returnable

#for game in dec_games:
#    print(str(prep_game(game)[0])+", "+str(prep_game(game)[1]) + ", " + str(prep_game(game)[2]))



npgames = np.array([prep_game(game)[:-1] for game in dec_games])
npresults = np.array([prep_game(game)[-1] for game in dec_games])
print(npgames,npresults)

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(npgames, npresults, test_size=0.25, random_state=0)

#print(x_train,x_train.shape,y_train,y_train.shape)
#print(x_test,x_test.shape,y_test,y_test.shape)

from sklearn.linear_model import LogisticRegression
# all parameters not specified are set to their defaults
logisticRegr = LogisticRegression()

logisticRegr.fit(x_train, y_train)
score = logisticRegr.score(x_test, y_test)
print(score)

from sklearn import metrics

predictions = logisticRegr.predict(x_test)
cm = metrics.confusion_matrix(y_test, predictions)
print(cm)


print(logisticRegr.coef_)
print(logisticRegr.intercept_)
