# USAU-2018-College-Data-Project
A beginning data science project analyzing the USAU College season from 2018.

8/14/2018:
So far, I've scraped all the games that occurred during the college season and organized them in to .csv format (see USAUCollegeScraper2018.py for method and USAUCollegeMen2018Games.csv as well as USAUCollegeWomen2018Games.csv for results) and scraped all the USAU rankings over the course of the season (see USAURankingsCollector.py for method and USAUCollegeMen2018Ranks.csv as well as USAUCollegeWomen2018Ranks.csv for results).
My first idea was to look for a way to turn USAU ratings scores into a win-probability predictor. I'm not all the way done with this, and I'm not entirely happy with what I have so far (see WinPctAnalysis.py for methods so far, but it's in progress).

Future ideas include analysis of sections/regions by how many games they played/won/lost, rankings/ratings, and maybe tournament=level stuff (correlation between level of tournaments attended and finish, etc?).

(Don't pay attention to the progress bar up top showing 99.7% HTML - that's all in /rawdata/ .)
