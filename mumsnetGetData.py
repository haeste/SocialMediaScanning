# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 13:49:51 2022

@author: Christopher Thornton
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import time
import pandas as pd
import logging
from tqdm import tqdm

# function supplied to find the urls of post on the index page
def data_click_id_is_topic_thread(tag):
    return tag.has_attr('data-click-id') and tag.attrs['data-click-id'].startswith('topic-thread')

# function for extracting post text and time
def extractFromCurrentPost(postloc):
    postRequest = Request(postloc, headers={'User-Agent': 'Mozilla/5.0'})
    postbytes = urlopen(postRequest).read()
    posthtml = postbytes.decode('utf8')
    postSoup = BeautifulSoup(posthtml, 'html.parser')
    current_post = postSoup.find_all(name='div', attrs={'class':'p-4 bg-mumsnet-forest dark:bg-mumsnet-forest-dark border-t border-b sm:border border-mumsnet-forest-border sm:rounded mt-4 lg:mt-1.5 py-2.5'})[0].text
    post_time = postSoup.find_all(name='span', attrs={'class':'lg:text-sm font-normal break-normal'})[0].text
    return current_post, post_time

#%% Set up parameters for where and when to scrape 
#specify the URL of the specific mumsnet forum to scrape
url_health = "https://www.mumsnet.com/talk/childrens_health"
#set the location to store the file containing the posts
save_location = "H:/redditProject/mumsnetparentinghealth.feather"
#specify pages to scrape from - if you want all pages look on the website for how many there are
start_page = 1
final_page = 788
#Set up logging file
logging.basicConfig(filename='./mumsnetpull.log',
                    format="%(asctime)s:%(levelname)s:%(message)s",
                    level=logging.INFO)

# Request initial page
r = Request(url_health, headers={'User-Agent': 'Mozilla/5.0'})
mybytes = urlopen(r).read()
MnetParenting = mybytes.decode("utf8")
soup = BeautifulSoup(MnetParenting, 'html.parser')

#lists to store post details
posts = []
post_titles = []
post_dates = []
#%%
#for each page
for p in tqdm(range(start_page, int(final_page)+1)):

    # load the current page and convert to BeautifulSoup object
    pageurl = url_health + '?page=' + str(p)
    currentRequest = Request(pageurl, headers={'User-Agent': 'Mozilla/5.0'})
    currentbytes = urlopen(currentRequest).read()
    currenthtml = currentbytes.decode("utf8")
    currentSoup = BeautifulSoup(currenthtml, 'html.parser')
    
    # find all post urls on the page
    currentLinks = currentSoup.find_all(data_click_id_is_topic_thread)
    
    #for each link to a post
    for l in currentLinks:
        
        postloc = l['href']
        
        trying = True
        #try ten times to load the post, then give up
        count = 0
        while(trying):
            try:
                curr_post, post_time = extractFromCurrentPost(postloc)   
                posts.append(curr_post)
                post_dates.append(post_time)
                post_titles.append(l.text)
                trying=False
            except:
                trying = True
                print('\nproblems scraping post: ' + postloc)
                time.sleep(10)
                count = count +1
                if count==10:
                    trying = False

# create pandas dataframe from post contents lists and save as a feather file.
posts_df = pd.DataFrame({'titles':post_titles, 'date':post_dates, 'post':posts})
posts_df.to_feather(save_location)