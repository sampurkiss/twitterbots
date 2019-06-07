# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 20:53:01 2018

@author: Sam Purkiss
"""

from bs4 import BeautifulSoup
import pandas as pd
import re
import urllib
import matplotlib.pyplot as plt

unique_code = 'tt0108778'
url = 'https://www.imdb.com/title/%s/episodes?season=%s' % (unique_code, "%s")

main_url = 'https://www.imdb.com/title/%s/' %(unique_code)


table = pd.DataFrame()


for season in range(1, 10000):
    url_current = url %(season)
     
    episode_page = urllib.request.urlopen(url_current)

    episode_page_html = BeautifulSoup(episode_page, 'html.parser')
    
    current_season = episode_page_html.select('#episode_top')
    #find out which season the program is currently finding info for. 
    #If the season number on the webpage does not match the season number in the loop,
    #the loop is out of range and must stop
    for szn in current_season:
        current_season = szn.text
        current_season = re.findall('([\d]+)',current_season)
        current_season = int(current_season[0])
    
    if current_season != season:
        break
        
    episode_names_html = episode_page_html.select('#episodes_content strong a')
    episode_names = []
    for name in episode_names_html:
           episode_names.append(name['title'])                                           
                                                  
    ratings_html = episode_page_html.select('.ipl-rating-widget > .ipl-rating-star .ipl-rating-star__rating')
    ratings = []
    for i in ratings_html:
        ratings.append(float(i.text))

    temp_table = pd.DataFrame()
    
    temp_table['episode_name'] = episode_names
    #in the case of new seasons, there won't be ratings, need to set to None or 
    #won't be able to merge columns
    #If the season is partially completed, it needs to add 'None' to non-released episode ratings
    for i in range(0, len(episode_names)):
        try: 
            ratings[i] == []
        except IndexError:
            ratings.append(None)
            
    temp_table['ratings'] = ratings
    temp_table['season'] = season
        
    table = table.append(temp_table)

    
plt.scatter(table['season'],table['ratings'])
