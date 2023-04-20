# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 15:33:52 2022

@author: Christopher Thornton
"""

import requests
import datetime
import time
import pandas as pd
import numpy as np

# get posts for specified day, if rejected try again in 60s
def getPostsFromReq(url,day):
        print(url)
        response = requests.get(url)
        while response.status_code != 200:
            print("Response error with code: " + str(response.status_code))
            time.sleep(60)
            response = requests.get(url)
        
        print("Completed with code: " + str(response.status_code))
        submissionlist = response.json()['data']
        titles = getFromJSONList(submissionlist, ['title', 'selftext', 'num_comments', 'score'])
        titles['date'] = [day]*len(titles['score'])
        day_df = pd.DataFrame(titles)
        return day_df, submissionlist

# get a list of submissions with only the fields specified
def getFromJSONList(submissionlist, fields):
    output = {}
    for f in fields:
        output[f] = []
    for sub in submissionlist:
        noblanks = True
        for f in fields:
            if f not in sub:
                noblanks = False
        if noblanks:
            for f in fields:
                    output[f].append(sub[f])
    return output
#%%
# specify the URL to the api for the subreddit of interest - see pushshift for details
api_url = 'https://api.pushshift.io/reddit/search/submission/?subreddit=Parenting'
api_url = api_url + '&size=100'
# specify the save location for the posts
save_location = './reddit_posts.feather'
# specify date range 
start_date = datetime.date(2010,1,1)
end_date = datetime.date(2022,2,1)
today = datetime.date.today()
day = start_date

all_df = pd.DataFrame()

# pull posts from each day
while day <= end_date:
    print('Collecting data for: ' + str(day))
    before = (today - day).days # get current day in days since epoch
    after = before + 1 # next day is plus 1
    beforehr = before*24 # convert to hours
    afterhr = after*24

    day_url = api_url+'&before='+str(beforehr) + 'h&after=' + str(afterhr) + 'h'

    firsthalf_df, submissionlist = getPostsFromReq(day_url,day)
    print(str(len(submissionlist)) + " posts")
    
    # if there are more submissions in a day than the api will return in one request
    if len(submissionlist)>99:
        # split into an appropriate number of requests
        numdivs = np.ceil(len(submissionlist)/99.0)
        times = np.floor(np.arange(0,1,1/numdivs)*24)
        print("Splitting into " + str(int(numdivs)))
        for i in range(0,int(numdivs)):
            b = int(times[i])
            a = int(times[i+1]) if i+1<len(times) else 24
            first_url = api_url+'&before='+str(beforehr+b) + 'h&after=' + str(beforehr+a) + 'h'
            firsthalf_df, _ = getPostsFromReq(first_url,day)
            all_df = all_df.append(firsthalf_df)

    # on to the next day
    day = day + datetime.timedelta(1)

all_df = all_df.reset_index().drop(columns='index')
all_df.to_feather(save_location)

#%%