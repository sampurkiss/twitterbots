# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 16:04:39 2018

@author: Sam Purkiss
"""

import tweepy
import os
from time import sleep
from datetime import datetime
import bs4
import random
from requests import get
import lxml.html
from lxml.cssselect import CSSSelector

#Set directory
os.chdir("C:/Users/sam purkiss/Documents/Code/Twitter")


consumer_key = "pY7c3EoBWXCxsp6Q2jbo1VBUx"
consumer_secret = "QuYXslytBusRBRIE7NJ5pPXySN5R6mDCcCcIhqbHPQSd20w9r5"
access_token = "1043559203460337664-ICpxQIuvBfVj7ZwJeiLS0ZnLPtyZiv"
access_token_secret = "K8iOuqmwtLNYIGvmHmstagjZZaPM2psgTRswUphzZpt5Q"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

#input Twitter name
my_name = "authors_thought"

#Get functions for generating quote
runfile("get_quote_functions")

author_list = [
        "Albert Einstein",
        "Mark Twain",
        "J. K. Rowling",
        "Ernest Hemingway",
        "Paulo Coelho"]

url, name = get_link(author_list)        
quote = get_quote(url, name)   

#Post tweet
api.update_status(quote)    

#Run follow/unfollow function
#runfile("follow_back.py")



#set delay time between running scripts
seconds_per_hour = 3600
hours_delay = 24 * seconds_per_hour

#sleep(hours_delay) 




