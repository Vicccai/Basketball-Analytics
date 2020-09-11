from selenium import webdriver
from pandas import *
import pandas
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import *

path_to_chromedriver = '/Users/victorcai/Downloads/chromedriver-2' # Path to access a chrome driver
browser = webdriver.Chrome(executable_path=path_to_chromedriver)

url = 'https://stats.nba.com/draft/combine-anthro/'
browser.get(url)

browser.find_element_by_xpath('/html/body/main/div[2]/div/div[2]/div/div/div[1]/div[1]/div/div/label/select/option[1]').click()
table = browser.find_element_by_class_name('nba-stat-table__overflow')

#print(table.text.split('\n'))
categories = table.text.split('\n')[1]
player = categories.split(' ')
#print(player)

db = pandas.DataFrame({'hi':[player]})
db
