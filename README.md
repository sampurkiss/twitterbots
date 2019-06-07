# twitterbots
A series of functions for building and controlling a twitterbot.

Note that most functions require passing an API as an argument. API can be set as follows:
```
import tweepy

auth = tweepy.OAuthHandler(consumer_key, 
                           consumer_secret)
auth.set_access_token(access_token, 
                      access_token_secret)
api = tweepy.API(auth)
```

Once set, all the functions are basically just plug and play. For example, to create a simple bot that generates a quote by webscraping brainyquotes.com and tweets it using the set api you can followt the below code:

```
import pandas as pd
from get_quote_functions import get_link, get_quote

url, name = get_link(author_list)      
quote = get_quote(url, name)   
api.update_status(quote)   
```
