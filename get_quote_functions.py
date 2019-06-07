# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 19:09:38 2018

@author: Sam Purkiss
"""
import random
import lxml.html
from lxml.cssselect import CSSSelector
from requests import get
import pandas as pd
import re

from twitter_quotes.credentials import consumer_key, consumer_secret, access_token, access_token_secret
import tweepy

auth = tweepy.OAuthHandler(consumer_key, 
                           consumer_secret)
auth.set_access_token(access_token, 
                      access_token_secret)
api = tweepy.API(auth)


def pick_random_author(author_list, header = True):
    #Note: lists only work if formatted as data frame
    rand_number = random.randint(0, len(author_list)-1)
    author = author_list['Authors'].iloc[rand_number]
    
    return author


def get_link(author_list):
    """ This function takes a list of names (or just one name), selects
     a name at random and appends the name onto a generic link so 
     that brainy quote can find all the authors quotes.
     The function returns a link to the authors page and the name 
     of the selected author to be used in the 'get_quote' function
     """
    generic_link = "https://www.brainyquote.com/authors/"
#    picks a random number to be used to pull from the index
#    if the index has a header than it starts at position 1
    if type(author_list)==pd.core.frame.DataFrame:
        author = pick_random_author(author_list)
    else:
        author = str(author_list).strip().title()
    #find number of spaces
    no_of_spaces = author.count(" ")
    
    #Takes author names and makes it ready to be appended to generic link
    author_fixed = author.lower().replace(" ","_", no_of_spaces)
    
    #If author name has a period (eg. an initial), remove period
    #However if there is a period before another letter eg. J.K. Rowling
    #I need to replace the first period with an underscore
    author_fixed = re.sub('(\.)(?=[a-zA-Z])','_',author_fixed)
    no_of_periods = author.count(".")
    if no_of_periods > 0:
        author_fixed = author_fixed.replace(".", "", no_of_periods)
    #Creates link that goes to generic page
    author_link = generic_link + author_fixed    
    return author_link, author


def get_quote(url, author_name):
    """ logic is from here: https://lxml.de/cssselect.html
    This function takes a url of website page that has quotes 
    and returns a random quote"""
    html_text = get(url)
    if html_text.status_code==404:
        return "404 error, retry author name"
    else:
        try:
            tree = lxml.html.fromstring(html_text.text)
            # select random quote
            selection = str('#qpos_1_%d .oncl_q' % random.randint(1,30))
            sel = CSSSelector(selection)
            results = sel(tree)
            try: #need to add this in for case in which there are quotes with no pictures
                match = results[1]
            except IndexError:
                match = results[0]
        #In case the selection process comes up with a number outside of possible range,
        #rerun program
        except IndexError:
            return get_quote(url, author_name)
        full_quote = match.text +"\n\n- " + author_name
            #Check to make sure if quote is right length for twitter
        if len(full_quote) <= 280:
            return full_quote
        else:
            return get_quote(url, author_name)
    

def post_quote(quote):
    details = api.update_status(quote) 
    return details

    