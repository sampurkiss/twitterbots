# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 20:18:39 2018

@author: Sam Purkiss
"""
import tweepy
import csv
from time import sleep


def dm_new_followers(recent_follower_list, file_location, api, send_dms = True):
    """
    This formula takes a list of all your most recent followers 
    and compares it to a recent list of followers. By doing so, 
    it can determine if there any followers in the new list, that aren't
    in the old list. These are assumed to be new followers. The function
    then DMs the new followers and resaves the old list with the new followers.
	It works by assuming followers not in the saved file are new followers.
	In order for this to work, you need to make a few changes to the tweepy
	package. 
	params:
		recent_follower_list: a list of follower ids
		file_location: a file that has your previous follower ids
		api: tweepy api details
		send_dms: whether you just want the list to be updated
    """
    #Open list of previous followers
    with open(file_location, 'r') as id_list:
        previous_followers = csv.reader(id_list)
        #create list based off followers, the 0 cleans up and only selects first column
        previous_followers = list(previous_followers)[0]               
    
    #Define the event which will be used to send the message. This hack is thanks to
    #https://github.com/tweepy/tweepy/issues/1081#issuecomment-423486837
    event = {
        "event": {
            "type": "message_create",
            "message_create": {
              "target": {
                "recipient_id": 'ID GOES HERE'
              },
              "message_data": {"text": "TEXT GOES HERE"
              }
            }
          }
        }
              
    #break out individual text lines for readability
    line_1 =    "Hi [NAME], thanks for following me! " 
    line_2 =    "I hope you enjoy my collection of quotes. " 
    line_3 =    "I\'m still building a list of inspiring authors, musicians and celebrities, " 
    line_4 =    "so if you think of someone you\'d like me to include, " 
    line_5 =    "please let me know. I\'d love to get your suggestions." 
    
    #Compare old list of followers to new, DM new ones    
    while send_dms: #Include this so I can update the list of followers without sending dms
        count = 0
        no_to_message = 30                
        for new_follower in recent_follower_list:  
            if new_follower not in previous_followers:
                dm_event = event
                user_name = api.get_user(new_follower).name #get followers name
                user_name = user_name.split(sep=" ")[0] #take only the first name                   
                line_1_mod = line_1.replace('[NAME]', user_name) #insert name of user into message
                full_text = str(line_1_mod + line_2 + line_3 + line_4 + line_5) # combine all text into one variable
                dm_event['event']['message_create']['message_data']['text'] =  full_text 
                dm_event['event']['message_create']['target']['recipient_id'] = new_follower
                try:
                    print("Now messaging " + user_name)
                    #print(count + dm_event['event']['message_create']['message_data']['text'])
                    api.send_direct_message_new(dm_event)                    
                except tweepy.error.TweepError:
                    pass
                count+=1
                #sleep between messages so twitter doesn't think it's a bot sending messages
                sleep(10) #delay between messages to stop twitter from think it's autmomated
                if count == no_to_message:
                    sleep_time = 1800
                    print("now taking a quick break for %d minutes" %(sleep_time/60))
                    count = 0
                    sleep(sleep_time ) #30 minutes sleep after messaging specified number of people
        send_dms = False
                              
    #Overwrite previous list of followers with new list for DM purposes
    with open(file_location, 'w') as csv_file:
        current_followers = csv.writer(csv_file, delimiter = ",")
        current_followers.writerow(recent_follower_list)