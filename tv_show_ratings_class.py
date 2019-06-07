# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 20:53:01 2018

@author: Sam Purkiss
"""

from bs4 import BeautifulSoup
import pandas as pd
import re
import sys
import urllib
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

#plotly.tools.set_credentials_file(username='sampurkiss', api_key = '63EX6SJ2qchqxIHdE3l9')
titles = pd.read_csv('https://datasets.imdbws.com/title.basics.tsv.gz', sep='\t')



show = get_tv_ratings(show_name= "The Bachelor", titles_data_frame = titles)
#show.get_unique_code()
data_table = show.get_rating_data()
show.plot_ratings()


class get_tv_ratings(object):
    def __init__(self, show_name=None, unique_code=None, titles_data_frame = []):
        """requires inputting the IMDB code for a show or the name of the show.
            You must enter either a show name or unique code. If a unique code is
            entered, the inputted show name will be ignored.
            The titles data set can be downloaded from IMDB here: 
                https://datasets.imdbws.com/title.basics.tsv.gz            
            """        
        self.titles_data_frame = titles_data_frame
        self.unique_code = unique_code
        self.show_name = show_name
        self.table = pd.DataFrame()
        self.averages = pd.DataFrame()
        
    
   
    def get_unique_code(self):
        """This function is used to get the unique code for a show given only a show name was inputted.
        On occasion, there will be more than one show with the same name, if that's the case, 
        the program will ask you to specify the year in which the show started.
        """
        #Convert titles to lower case in order for easier comparisons
        self.titles_data_frame['primaryTitle'] = self.titles_data_frame['primaryTitle'].str.lower()
        #Search for show name in dataset. In case the show can't be found in the set then give user chance to exit
        #or re-input
        self.show_codes = self.titles_data_frame[self.titles_data_frame['primaryTitle']==self.show_name.lower()]\
            [self.titles_data_frame['titleType']=='tvSeries']\
            [['primaryTitle','originalTitle','tconst','startYear']]
#        (l,w) = show_codes.shape
#            if l == 0:
#                print('''You have inputted an incorrect tv show name.
#                      Please try again.''')
#                break
#            else:
#                break
               
        #get length of data set, if it's longer than 1, it means there's more than one show
        #with the same name, need to specify which one is wanted.
        (l,w) = self.show_codes.shape
        if l > 1:
            print('There are %d different shows.'%(l))
            print('Please select the start date of the show you want to confirm it\'s the one you\'re after.')
            print('The different start dates are as follows:')
            for i in self.show_codes['startYear']:
                print(i)
            
            #Get user input for required start date. If an incorrect year is given,
            #the dataframe will have a length of 0 which is used to test if value needs to be 
            #reinputted.
            while True:
                start_year = input('> ')
                (l,w)= self.show_codes[self.show_codes['startYear']==str(start_year)].shape
                if l == 1:
                    self.unique_code = self.show_codes[self.show_codes['startYear']==start_year]['tconst'].iloc[0]    
                    break
                else:
                    print('You have entered an incorrect year. Please try again')
        else:
            try:
                self.unique_code = self.show_codes['tconst'].iloc[0]
            except IndexError:
                print('Error getting IMDB code, check to make sure title is correct')         
                    
        return self.unique_code

 

    def get_rating_data(self):
        """
        This function scrapes IMDB for tv show information.
        It returns a data table with the data it finds.
        """
        if self.show_name != None:
            self.unique_code = self.get_unique_code()

        self.url = 'https://www.imdb.com/title/%s/episodes?season=%s' % (self.unique_code, "%s")

        for season in range(1, 10000):
            temp_table = pd.DataFrame()    
            
            url_current = self.url %(season)             
            
            try:
                episode_page = urllib.request.urlopen(url_current)
            except urllib.error.HTTPError:
                print('HTTPError, the code was incorrect or non-existant.')
                print('Check to make sure title is correct')
                break
                
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
            ###############################################################
            #Get episode names and episode numbers
            ###############################################################
            episode_names_html = episode_page_html.select('#episodes_content strong a')
            episode_names = []
            for name in episode_names_html:
                   episode_names.append(name['title'])
            episode_number_html = episode_page_html.select('.zero-z-index div')
           
            episode_number = []
            for name in episode_number_html:
                episode_number.append(name.text)
            ###############################################################
            #Get episode ratings
            ###############################################################                                              
            ratings_html = episode_page_html.select('.ipl-rating-widget > .ipl-rating-star .ipl-rating-star__rating')
            ratings = []
            for i in ratings_html:
                ratings.append(float(i.text))
        
            #in the case of new seasons, there won't be ratings, need to set to None or 
            #won't be able to merge columns
            #If the season is partially completed, it needs to add 'None' to non-released episode ratings
            temp_table['episode_name'] = episode_names                                           

            for i in range(0, len(episode_names)):
                try: 
                    ratings[i]
                except IndexError:
                    ratings.append(None)
                    
            temp_table['ratings'] = ratings
            temp_table['episode_number'] = episode_number
            temp_table['season'] = season
                
            self.table = self.table.append(temp_table)
        
        #Make additional data table showing average ratings by seasons
        seasons = []
        for season in self.table['season']:
            if season not in seasons:
                seasons.append(season)
        self.averages['average_rating'] = round(self.table.groupby(['season'])['ratings'].mean(),2)
        self.averages['season']  = seasons
            
        return self.table, self.averages
    
    def plot_ratings(self):
        """
        Plots the dataset generated from the tv show.
        Requires plotly to be enabled on your computer.
        """
        all_traces = []
        length, width = self.table.shape
        
        #Create traces for each row
        for i in range(0,length-1):    
            temp= self.table.iloc[i]
            trace0 = go.Scattergl(x = [temp['season']],
                               y = [temp['ratings']],
                               mode = 'markers',
                               marker= dict(size= 14, line= dict(width=1), opacity= 0.3),
                               name = temp['episode_number'],
                               text = [temp['episode_name']])
            all_traces.append(trace0)
        
        averages_trace = go.Scattergl(x= self.averages['season'],
                                      y= self.averages['average_rating'],
                                      name = 'Average rating',
                                      mode = 'lines')
        all_traces.append(averages_trace)
        
        layout= go.Layout(
            title= self.show_name.title() + ' Episode Ratings by Season',
            hovermode= 'closest',
            showlegend= False,
            xaxis= dict(
                title= 'Season',
                ticklen= 5,
                zeroline= False,
                gridwidth= 2),
            yaxis=dict(
                title= 'Rating',
                ticklen= 5,
                gridwidth= 2))
        fig = go.Figure(data = all_traces, layout = layout)
            
        py.iplot(fig, filename='basic-scatter')

