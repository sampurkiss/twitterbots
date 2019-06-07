# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 10:29:13 2018

@author: Sam Purkiss
"""
import re
import tweepy

def find_and_rt(search_query, api, no_of_results = 75, avoid_list = [], type_of_search = 'recent'):
    ######################################################################        
    #Run query to get list of competition tweets
    ######################################################################
    #type_of_search = 'popular'    
    tweets = tweepy.Cursor(api.search, q=search_query, result_type=type_of_search).items(200)
    
    #Get the tweet ids from above list, avoid any bot spammers included in the avoid list
    all_tweets = []
    counter=0
    for tweet in tweets:
        if counter < no_of_results:
            if tweet.user.name not in avoid_list:
                #Get tweet text so I can check if it's got scammy red flags
                try: #need this in case I'm blocked by poster of tweet
                    tweet_text = api.get_status(tweet.id, tweet_mode = 'extended').full_text               
                    if re.search('When I tweet, take notice and make money', tweet_text) is None: #don't show those scammy bitcoin tweets 
                        all_tweets.append(tweet.id)
                        counter+=1
                except tweepy.error.TweepError:
                    pass
        
    #get the full text of every tweet which will be used to see which ones request I follow them
    tweet_text = []    
    for id in all_tweets:
        #Error 136 happened which appears to be from a user blocking me
        try:
            tweet_text.append(api.get_status(id, tweet_mode= "extended").full_text.lower())    
        except tweepy.error.TweepError:
            pass

    #get the user ids of all tweets from the tweet ids    
    user_ids = []
    for id in all_tweets:
        try:
            user_ids.append(api.get_status(id).user.id)
        except tweepy.error.TweepError:
            pass
    
    ######################################################################        
    #Get list of twitter names from tweets that request I follow someone
    ######################################################################
    regex_pattern = "(?<=@)\w+" #looks for all words following the @ symbol
    regex_test = "follow"
    user_names = []
    tweet_index = 0 #used to index column of user ids and add original tweeter to list
    for line in tweet_text:
        if re.search(regex_test, line) is not None:            
            original_tweeter = api.get_user(user_ids[tweet_index]).screen_name
            user_names.append(original_tweeter)
            #Find if there's a username referenced add the name
            name_iter = re.finditer(regex_pattern, line)
            for screen_name in name_iter:
                user_names.append(screen_name.group())
        tweet_index+=1
                
    #remove duplicates from above link
    user_names_unique = []
    for name in user_names:
        if name not in user_names_unique:
            user_names_unique.append(name)
        

    ######################################################################            
    #detect if I need to tag someone and then tag three names
    ######################################################################
    tag_people = ['@Jeffrey_Bowser',
                  '@rogerkiethhaile',
                  '@rogerkieth']
    
    regex_pattern_2 = "tag " #important that space follows word so it doesn't find words like 'instagram'
    
    tweet_index_ref = 0   
    for line in tweet_text:
        if re.search(regex_pattern_2, line) is not None:
            try:
                post_id = all_tweets[tweet_index_ref]
                text = '@' + api.get_status(post_id).user.screen_name
                #full_text = text + ' omg %s, %s, %s, check this out!' %(tag_people[0], tag_people[1], tag_people[2])
                #api.update_status(full_text, post_id)
            except tweepy.error.TweepError:
                pass
        tweet_index_ref+=1
    
    ######################################################################            
    #Take action on the above tweets
    ######################################################################
    """
    Like, and retweet all tweets
    if there's any error, pass it
    """
    for tweet_id in all_tweets:
        try:
            api.retweet(tweet_id)
            api.create_favorite(tweet_id)
        except tweepy.error.TweepError:
            pass
    """
    For any tweets that requested I follow someone, follow them back
    """    
    for screen_name in user_names:
        try:
            api.create_friendship(screen_name)
        except tweepy.error.TweepError:
            pass
        