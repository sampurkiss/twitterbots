# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 17:15:27 2018

@author: Sam Purkiss
"""
import tweepy
from time import sleep


#Follow back all followers
def follow_back(follower_list, following_list, api): 
    counter = 0
    max_follow_at_once = 75
    for follower in follower_list:
        if follower not in following_list:
            try:
                #Error Code 160 if it tries to follow someone again who has private settings
                api.create_friendship(follower)
                print("Now following " + api.get_user(follower).screen_name)
            #Error Code 160 happens if you try to request to follow a private account for second time
            except tweepy.error.TweepError:
                pass
            counter +=1
            if counter == max_follow_at_once:
                print("followed %d people, taking a pause" %(counter))
                sleep(3600) #sleep for an hour once follow back limit is hit
        else:
            pass
                

def unfollow_haters(follower_list, 
                    following_list, 
                    api, 
                    unfollow_at_once = 75, 
                    total_to_unfollow=None,
                    hours_delay = 1):
        """Unfollow function, 
        unfollow those who don't follow back by identifying lack of overlap in follow/unfollow list.
        The counter checks how many loops the function needs to go through based off
        the number of people to unfollow at once. It has a limit so as to not overwhelm
		the API. If you unfollow too many accounts, Twitter will block the function or worse.
        Uses the inverse of the list in order to unfollow oldest unfollowers first"""
        
        #used to measure how many have been unfollowed in each loop
        count_of_unfollowed_at_once=0
        
        #used to measure how many total have been unfollowed
        count_of_unfollowed = 0
        
        following_list.reverse() #Unfollow oldest bunch first 
        
        # If the max number of people to unfollow isn't set, just use the total length 
        # of following list as the max number to unfollow
        if total_to_unfollow == None:
            total_to_unfollow = len(following_list)                      
        
        for hater in following_list:
            if hater not in follower_list:
                try:#error handling for case where user can't be found
                    #Only select a few at once so as not overload twitter with requests
                    print(str(count_of_unfollowed+1) + ". " + api.get_user(hater).screen_name + " is being unfollowed")
                    api.destroy_friendship(hater)
                    count_of_unfollowed_at_once += 1
                    count_of_unfollowed +=1
                    #test to see if I've hit the number of unfollows defined
                    if count_of_unfollowed >= total_to_unfollow:
                        break
                    if count_of_unfollowed_at_once == unfollow_at_once:
                        count_of_unfollowed_at_once = 0
                        print("Quick pause to not overload Twitter with unfollows")
                        sleep(3600*hours_delay)
                except tweepy.error.TweepError:
                    sleep(3600) #Pause for an hour to reset API limit
               
        print("The haters have been unfollowed")

   

def follow_account_followers(account_name, api, max_number_to_follow = 75):
	"""
	This function follows users of any account, you just need to 
	put the account name in. The idea is that you can target accounts similar
	to yours and if you follow people who follow that account, they will
	be more likely to follow you back.
	"""
    the_followers = api.followers_ids(account_name)[0:max_number_to_follow]
    counter = 0
    for follower in the_followers:
        try:
            api.create_friendship(follower)
            counter+=1
        except tweepy.error.TweepError:
            pass
    print("You've just followed (or requested to follow) %d new people" %counter)
    
    
#Follow back people who have retweeted a specific tweet
def follow_rtrs(tweet_id, api):
	"""
	This function follows users that have retweeted a tweet, you just need to 
	put the tweet id in. The idea is that you can target tweets similar
	to yours and if you follow people who follow that account, they will
	be more likely to follow you back. You can also target tweets that 
	connect follow backs as a quick way to build your follower count.
	"""
    rtrs = tweepy.cursor(api.retweeters, id =tweet_id, max_follows = 75)
    user_ids =[]
    counter = 0
    tweets = tweepy.Cursor(api.search, q='follow all rt OR retweet').items(2)
    
    while counter < max_follows:
        for user_id in rtrs:
            user_ids.append(user_id)
        counter+=1
        
        
        
        