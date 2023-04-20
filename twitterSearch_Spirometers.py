# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 17:22:57 2022

@author: Christopher Thornton
"""
from twarc import Twarc2, expansions
import datetime
import pickle

#specify the location of the bearer token for the API and a location to save results to
token_location = './BearerToken.txt'
save_location = r'./spirometers.pkl'
with open(token_location, 'r') as file:
    token = file.read()
    
client = Twarc2(bearer_token=token)

# Specify the start time in UTC for the time period you want Tweets from
start_time = datetime.datetime(2010, 1, 1, 0, 0, 0, 0, datetime.timezone.utc)

# Specify the end time in UTC for the time period you want Tweets from
end_time = datetime.datetime(2021, 12, 30, 0, 0, 0, 0, datetime.timezone.utc)


# This is where we specify our query 
query = " spirometer at home -is:nullcast lang:en -is:retweet"

# The search_all method call the full-archive search endpoint to get Tweets based on the query, start and end times
search_results = client.search_all(query=query)

alltweets = []

for p in search_results:
    result = expansions.flatten(p)
    for tweet in result:
        alltweets.append(tweet)

with open(save_location, 'wb') as f:
    pickle.dump(alltweets, f)
