from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pandas import *
import pandas
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import *

def main():
    removeID()

#convert x'y" format to inches
def toInches(x, i):
    ft = int(x[0])
    inOne = x.find("'")
    inTwo = x.find("'", 2)
    #some had '' and some "
    if (inTwo == -1):
        inTwo = x.find('"', 2)
    inch = float(x[inOne+1:inTwo])
    result = ft * 12 + inch
    return result

#preliminary method just to test it out, for first season
def db():
    browser = webdriver.Chrome(ChromeDriverManager().install())

    #path_to_chromedriver = '/Users/victorcai/Downloads/chromedriver-2' # Path to access a chrome driver
    #browser = webdriver.Chrome(executable_path=path_to_chromedriver)

    url = 'https://stats.nba.com/draft/combine-anthro/'
    #url = 'https://www.nba.com/stats/leaders/?Season=2019-20&SeasonType=Regular%20Season'
    browser.get(url)

    #browser.find_element_by_xpath('/html/body/main/div[2]/div/div[2]/div/div/div[1]/div[1]/div/div/label/select/option[1]').click()
    table = browser.find_element_by_class_name('nba-stat-table__overflow')

    player_stats = []

    for line_id, lines in enumerate(table.text.split('\n')):
        if line_id != 0:
            player_stats.append(list(reversed(lines.split(' '))))

    #print(player_stats)

    db = pandas.DataFrame({'name': [' '.join(i[len(i):8:-1]) for i in player_stats],
                           'pos': [i[8] for i in player_stats],
                           'hand len': [i[6] for i in player_stats],
                           'hand wid': [i[5] for i in player_stats],
                           'ht': [toInches(i[4]) for i in player_stats],
                           'wt': [i[1] for i in player_stats],
                           'wingspan': [toInches(i[0]) for i in player_stats],
                           }
                         )

    #print(table.text)
    return db

#gets all the player measurement data from last 17 seasons
def db2():
    #vary based on spaces and if their name had Jr. or III
    validProfileLen = [11,12,15,16]
    maxShortProfileLen = 12

    browser = webdriver.Chrome(ChromeDriverManager().install())
    url = 'https://stats.nba.com/draft/combine-anthro/'
    browser.get(url)
    player_stats = []

    for i in range(17):
        #wait for pages to load otherwise sometimes can't find table
        element = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/main/div/div/div[2]/div/div/div[1]/div[1]/div/div/label/select')))
        path = '/html/body/main/div/div/div[2]/div/div/div[1]/div[1]/div/div/label/select/option[' + str(i+1) + ']'
        browser.find_element_by_xpath(path).click()
        element = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]')))

        table = browser.find_element_by_class_name('nba-stat-table__overflow')

        #lines is full player profile, split by \n so each line is a player
        for line_id, lines in enumerate(table.text.split('\n')):
            #if not in validProfileLen then it would include players with no data
            if line_id != 0 and len(lines.split(' ')) in validProfileLen:
                #append an array of player's numbers
                player_stats.append(list(reversed(lines.split(' '))))
    name = []
    pos = []
    handLen = []
    handWid = []
    ht = []
    wt = []
    wingspan = []
    for i in player_stats: #loops through each player, i is a player profile
        try: #dependent on profile length because of spaces
            name.append(' '.join(i[len(i):8:-1]) if len(i) <= maxShortProfileLen else ' '.join(i[len(i):12:-1]))
            pos.append(i[8] if len(i) <= maxShortProfileLen else i[12])
            handLen.append(i[6] if len(i) <= maxShortProfileLen else i[10])
            handWid.append(i[5] if len(i) <= maxShortProfileLen else i[9])
            ht.append(toInches(i[4], i) if len(i) <= maxShortProfileLen else toInches(' '.join(i[8:6:-1]), i))
            wt.append(i[1] if len(i) <= maxShortProfileLen else i[2])
            wingspan.append(toInches(i[0], i) if len(i) <= maxShortProfileLen else toInches(' '.join(i[1::-1]), i))
        except: #for debugging
            print(i)

    db = pandas.DataFrame({'name': name,
                           'pos': pos,
                           'hand len': handLen,
                           'hand wid': handWid,
                           'ht': ht,
                           'wt': wt,
                           'wingspan': wingspan,
                           }
                         )
    #manually add significant player data that was missing
    db.loc[len(db.index)] = ['RJ Barrett', 'SF', '-', '-', 78.5, 190.0, 82.00]
    db.loc[len(db.index)] = ['Darius Garland', 'SG', '-', '-', 72.5, 175.0, 75.00]
    db.loc[len(db.index)] = ["De'Andre Hunter", 'SF', '-', '-', 79.0, 225.0, 86.00]
    db.loc[len(db.index)] = ['Ja Morant', 'PG', '-', '-', 75.0, 174.0, 79.00]
    db.loc[len(db.index)] = ['Zion Williamson', 'PF', '-', '-', 78.0, 284.0, 82.00]
    db.loc[len(db.index)] = ['Markelle Fultz', 'PG', '-', '-', 75.0, 201.0, 81.00]
    db.loc[len(db.index)] = ['Kris Dunn', 'PG', '-', '-', 75.0, 205.0, 81.50]
    db.loc[len(db.index)] = ['Lebron James', 'SF', 9.00, 9.25, 81.0, 250.0, 84.00]
    db.loc[len(db.index)] = ['Carmelo Anthony', 'SF', '-', '-', 80.0, 235.0, 84.00]

    db.to_csv('NBAData.csv', index = False)

#after downloading data from Basketball-Reference, the player names had IDs after
#the actual name, so I removed them so I could join data from different graphs in SQL
def removeID():
    stl = pandas.read_csv("STL.csv")
    for i, j in stl.iterrows():
        player = stl.iat[i, 1]
        index = player.find('\\')
        stl.iat[i, 1] = player[:index]
    stl.to_csv('STLs.csv', index = False)

    ft = pandas.read_csv("FT.csv")
    for i, j in ft.iterrows():
        player = ft.iat[i, 1]
        index = player.find('\\')
        ft.iat[i, 1] = player[:index]
    ft.to_csv('FTs.csv', index = False)

    dbpm = pandas.read_csv("DBPM.csv")
    for i, j in dbpm.iterrows():
        player = dbpm.iat[i, 1]
        index = player.find('\\')
        dbpm.iat[i, 1] = player[:index]
    dbpm.to_csv('DBPMs.csv', index = False)

    tp = pandas.read_csv("3P.csv")
    for i, j in tp.iterrows():
        player = tp.iat[i, 1]
        index = player.find('\\')
        tp.iat[i, 1] = player[:index]
    tp.to_csv('TPs.csv', index = False)

main()
