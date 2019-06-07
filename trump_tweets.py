# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 10:03:40 2019

@author: Sam Purkiss
"""

#Get Trump tweets by time he was spending doing things

#"https://docs.google.com/spreadsheets/d/1oITCuVsYdhNXtY7GElLelsrbjRRIPJ1ce-_v-8J1X_A/edit#gid=0"


import tweepy
import pandas as pd
import numpy as np
from datetime import timezone, datetime, timedelta
import os
os.chdir("C:/Users/sam purkiss/Documents/Code/Twitter")
import credentials

auth = tweepy.OAuthHandler(credentials.consumer_key_contest, credentials.consumer_secret_contest)
auth.set_access_token(credentials.access_token_contest, credentials.access_token_secret_contest)
api = tweepy.API(auth)

account = "realDonaldTrump"


private_schedule = pd.read_csv('Axios _ President Donald Trump Private Schedules, Nov. 7, 2018 to Feb. 2, 2019 - data.csv')
    
twitter_deets = tweepy.Cursor(api.user_timeline, id=account, tweet_mode='extended').items(1000)
#Create start and end time columns
private_schedule['start_date'] = pd.to_datetime(private_schedule['date'] + ' ' + private_schedule['time_start'])
private_schedule['end_date'] = pd.to_datetime(private_schedule['date'] + ' ' + private_schedule['time_end'])
private_schedule = private_schedule.drop(columns=['date', 'time_start','time_end'])
#private_schedule['unassigned_time'] = np.where((private_schedule['end_date'] not in private_schedule['start_date']),True,False )

all_tweets = pd.DataFrame()
for i in twitter_deets:
    temp=pd.DataFrame()
    temp['tweet_timestamp'] = [i.created_at]
    temp['tweet_text'] = [i.full_text]
    temp['from_source'] = [i.source]
    all_tweets = all_tweets.append(temp)

#Convert date variable to datetime
all_tweets['tweet_timestamp'] = (all_tweets['tweet_timestamp']
                                    .astype(str)
                                    .apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S')))
#Subtract five hours to adjust for timezone
all_tweets['tweet_timestamp'] = all_tweets['tweet_timestamp'].apply(lambda x: x - timedelta(hours=5))



#Allocate tweet to appropriate time
private_schedule= private_schedule.assign(keys=1)
all_tweets = all_tweets.assign(keys=1)

tweets_and_schedule = (pd.merge(private_schedule, all_tweets, on = 'keys', how='outer')
                .query('start_date < tweet_timestamp and end_date> tweet_timestamp')
                .reset_index())
tweets_and_schedule[tweets_and_schedule['top_category']=='executive_time']['tweet_text']
tweets_and_schedule = tweets_and_schedule.drop(columns=['keys'])

tweets_and_schedule[['tweet_text','top_category']].head()
#Save database
tweets_and_schedule.to_csv('tweets and schedule.csv', index=False)
timezone.fromutc(all_tweets['tweet_timestamp'].iloc[0])

datetime.fromtimestamp(temp['tweet_timestamp'].iloc[0])
