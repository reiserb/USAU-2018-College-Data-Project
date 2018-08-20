import csv
import pandas as pd
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from tqdm import tqdm
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score

division = "College"
year = "2018"
#gender = "Women"
gender = "Men"

#load rankings from file here
rankingsDict = {} #format: "Teamname" : [rankings file content]

with open("USAU"+division+gender+year+"Ranks.csv","r") as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        if row != []:
            rankingsDict[row[0]] = row

rdates = ["2018-06-03","2018-04-03","2018-03-28","2018-03-21","2018-03-14","2018-03-07"]

gamesplayed = []
rankingpts = []

for team in tqdm(rankingsDict):
    tempdata = rankingsDict[team]
    if "N/A" not in tempdata[-3]:
        gp = int(tempdata[-2])+int(tempdata[-1])
        rk = int(tempdata[-3])
        gamesplayed.append(gp)
        rankingpts.append(rk)

regGP = np.array(gamesplayed)
regRP = np.array(rankingpts)
slope, intercept, rvalue, pvalue, stderror = sp.stats.linregress(regGP,regRP)

print(division + " " + gender + " " + year)
print(len(gamesplayed), "records found")
print("Slope:", slope)
print("Intercept:", intercept)
print("r^2 = ", rvalue**2)
plt.plot(gamesplayed,rankingpts,"r.",gamesplayed,[slope*x+intercept for x in gamesplayed],"b-")
plt.title(division + " " + gender + " " + year + " teams, ranking versus games played")
plt.xlabel("Games played")
plt.ylabel("USAU rankings points")
plt.show()

residuals = [rankingpts[i]-(slope*gamesplayed[i]+intercept) for i in range(len(gamesplayed))]

plt.plot(gamesplayed,residuals,"r.",gamesplayed,[0]*len(gamesplayed),"b-")
plt.title(division + " " + gender + " " + year + " teams, residuals")
plt.xlabel("Games played")
plt.ylabel("Predicted - actual rankings pts")
plt.show()
