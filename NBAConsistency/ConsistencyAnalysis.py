# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pandas import *
import pandas as pd


# %%
measurements = pd.read_csv('NBAMeasurements/RawData/NBAData.csv')
measurements


# %%
#get opponent points from score
def oppPts(score):
    dash = score.find('-')
    return int(score[dash+1:])
    


# %%
browser = webdriver.Chrome(ChromeDriverManager().install())
url = 'https://www.foxsports.com/nba/philadelphia-76ers-team-game-log?season=2019&category=SCORING&seasonType=1'
browser.get(url)
team_stats = []
#teams in alphatbetical order
teams = ['76ers','Bucks','Bulls','Cavaliers','Celtics','Clippers','Grizzlies','Hawks','Heat','Hornets','Jazz','Kings','Knicks','Lakers','Magic','Mavericks','Nets','Nuggets','Pacers','Pelicans','Pistons','Raptors','Rockets','Spurs','Suns','Thunder','Timberwolves','Trail Blazers','Warriors','Wizards']

for i in range(30):
    element = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/section[1]/div/section[1]/div/div[2]/div[1]/div[2]/div[1]/select')))
    path = '/html/body/section[1]/div/section[1]/div/div[2]/div[1]/div[2]/div[1]/select/option[' + str(i+1) + ']'
    browser.find_element_by_xpath(path).click()
    element = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/section[1]/div/section[2]/div/div[1]/table')))

    table = browser.find_element_by_xpath('/html/body/section[1]/div/section[2]/div/div[1]/table')


    for line_id, lines in enumerate(table.text.split('\n')):
        if line_id != 0 and len(lines.split(' ')) == 15:
            #append an array of a game's stats. Put team name at beginning.
            team_stats.append([teams[i]]+lines.split(' '))


# %%
db = pandas.DataFrame({ 'team': [ i[0] for i in team_stats ],
                        'result': [ i[4] for i in team_stats ],
                        'pts': [ i[15] for i in team_stats ],
                        'oppPts': [ oppPts(i[5]) for i in team_stats ],
                        'FGA': [ i[7] for i in team_stats ],
                        'FG%': [ i[8] for i in team_stats ],
                        '3PA': [ i[13] for i in team_stats ],
                        '3P%': [ i[14] for i in team_stats ],
                        }
                        )
#convert the data to proper type
db['pts']=db['pts'].astype('int64')
db['FGA']=db['FGA'].astype('int64')
db['3PA']=db['3PA'].astype('int64')
db['3P%']=db['3P%'].astype('float64')
db['FG%']=db['FG%'].astype('float64')
db['team']=db['team'].astype(str)
db['result']=db['result'].astype(str)


# %%
#create list of win pct of teams in alphabetical order
win_pct = []
for i in teams:
    #wins is a series of an individual team's results (W,L)
    wins = db.loc[db.team == i]['result'].reset_index(drop = True)
    count = 0
    for j in range(wins.size):
        if wins[j] == 'W': 
            count += 1
    #count wins and divide by total
    win_pct.append(count / wins.size)
win_pct


# %%
#win_df is dataframe w 1 row (win pct). Each column is a diff team. 
win_df = pd.DataFrame([win_pct], columns = teams)
# sorts values then returns indices. We want the teams sorted so that when we make graphs, 
# they're organized by wins. We want to see how their performance affects winning.
sorted_index = win_df.iloc[0].sort_values().index
sorted_index


# %%
#3P%. tp_pct_df is a dataframe where each column is a team's 3P% in each of its games
tp_pct_df = pd.DataFrame()
for i in teams:
    #column is a series of an individual team's 3P% in each of its games
    column = db.loc[db.team == i]['3P%'].reset_index(drop = True)
    #add is a dataframe consisting of one column
    add = pd.DataFrame({i: column})
    #now concatenate add to the dataframe, axis = 1 to add columnwise
    tp_pct_df = pd.concat([tp_pct_df, add], axis = 1)

#sorted version to be used for violin plot
tp_pct_df_sorted = tp_pct_df[sorted_index]

#returns a Series of each team's mean 3P%, the indices are teams
means = tp_pct_df.mean()
win_pct = pd.Series(win_pct)
#temp is a dataframe with team, 3P%, and win pct. Reset means index so it matches with win_pct
temp = pd.concat([means.reset_index(), win_pct], axis = 1)
#rename columns
temp.columns = ['team', '3P%', 'win%']
temp.plot.scatter(x='3P%',y='win%',title='3P% vs win%')


# %%
#what we did with the means, this time with variance
var = tp_pct_df.var()
temp = pd.concat([var.reset_index(), win_pct], axis = 1)
temp.columns = ['team', 'var_3p%', 'win%']
temp.plot.scatter(x='var_3p%',y='win%',title='var_3p% vs win%')
#correlation of variance of 3 pointers with win pct
print(temp['var_3p%'].corr(temp['win%']))


# %%
import seaborn
from matplotlib import pyplot
fig, ax = pyplot.subplots(figsize = (7, 20))
#violin plot
graph = seaborn.violinplot(data = tp_pct_df_sorted, orient = 'h')


# %%
#what we did before, this time with fg%
fg_pct_df = pd.DataFrame()
for i in teams:
    column = db.loc[db.team == i]['FG%'].reset_index(drop = True)
    add = pd.DataFrame({i: column})
    fg_pct_df = pd.concat([fg_pct_df, add], axis = 1)
fg_pct_df_sorted = fg_pct_df[sorted_index]
means = fg_pct_df.mean()

temp = pd.concat([means.reset_index(), win_pct], axis = 1)
temp.columns = ['team', 'fg%', 'win%']
temp.plot.scatter(x='fg%',y='win%',title='fg% vs win%')


# %%
var = fg_pct_df.var()
temp = pd.concat([var.reset_index(), win_pct], axis = 1)
temp.columns = ['team', 'var_fg%', 'win%']
temp.plot.scatter(x='var_fg%',y='win%',title='var_fg% vs win%')
print(temp['var_fg%'].corr(temp['win%']))


# %%
fig, ax = pyplot.subplots(figsize = (7, 20))
graph = seaborn.violinplot(data = fg_pct_df_sorted, orient = 'h')


# %%
#what we did before, this time with opp pts
opp_df = pd.DataFrame()
for i in teams:
    column = db.loc[db.team == i]['oppPts'].reset_index(drop = True)
    add = pd.DataFrame({i: column})
    opp_df = pd.concat([opp_df, add], axis = 1)
opp_df_sorted = opp_df[sorted_index]
means = opp_df.mean()

temp = pd.concat([means.reset_index(), win_pct], axis = 1)
temp.columns = ['team', 'oppPts', 'win%']
temp.plot.scatter(x='oppPts',y='win%',title='oppPts vs win%')


# %%
var = opp_df.var()
temp = pd.concat([var.reset_index(), win_pct], axis = 1)
temp.columns = ['team', 'var_opp', 'win%']
temp.plot.scatter(x='var_opp',y='win%',title='var_opp vs win%')
print(temp['var_opp'].corr(temp['win%']))
print(temp['var_opp'].corr(means.reset_index(drop = True)))


# %%
fig, ax = pyplot.subplots(figsize = (7, 20))
graph = seaborn.violinplot(data = opp_df_sorted, orient = 'h')

# %% [markdown]
# This project looked into how consistency affected winning. I looked at how FG%, 3P%, and Opponent Points 
# (as a proxy for defense, as a proxy for effort) and their variances (measurement of consistency) affected Win% (winning). 
# I came up with this idea thinking about how certain players, like Danny Green or JR Smith, are very streaky, 
# hot and cold shooters, whereas other players are more consistent, but at the end of the season, 
# they all only have one number for their percentage, which doesn't necessarily tell the full story. 
# I wanted to see if a team with very consistent shooting and defense (as a proxy for effort) was any better than inconsistent teams. 
# In a perfect world, you could add up the individual shooting variances and it would equal the team variance, 
# so team variance would represent how consistent the players are.
# 
# Hypothesis: There is a correlation between consistency and winning. It could go either way, 
# as more consistent teams know their best path to win, but less consistent teams would be harder to game plan for. 
# I think more consistent teams will be better at winning.
# 
# Procedure: I scraped game log data for each team from Fox Sports. I used Pandas to put the data in a dataframe, 
# calculate win pct, extract desired data and separate data for each team, sort the data by team win pct, 
# calculate the variances of data and correlation of the variances with win pct, and visualize data.
# 
# Results: (correlation coefficients)
# Var_3P vs Win%: - -0.10
# Var_FG vs Win% - 0.14
# Var_OppPts vs Win% - -0.32
# 
# Analysis: There was little to no correlation between the shooting variance/consistency and winning. 
# Looking at the violin plots, we can also see that there was really no discernable pattern between higher variance and winning. 
# Variance of opponent points had a low to moderate correlation with win %, meaning teams that consistently defended tended to win more. 
# Curious about this, I went back and calculated the correlation between variance in opponent points and actual opponent points, 
# and found it to be -0.44, an even stronger correlation, suggesting that more consistent teams tended to have better defenses, 
# which makes sense considering more consistency would mean more consistent effort, which is a big part of defense.
# 
# One thing to consider is that if a team has a lot of good players who are streaky, they can assess who is hot and who is cold
# and play the hot shooter more minutes, similar to what the Lakers did last season (2020), 
# thus mitigating negative effects of players' cold shooting, whereas other teams are without the option to go to a different player. 
# Thus, the team variance may not necessarily represent its players' consistency game by game the way we want it to.
# 
# Future: take a look at individual players. Have a metric to rate whether they are consistent or not, 
# and see which teams have the most/least consistent players, and see if the amount has any affect on winning.

