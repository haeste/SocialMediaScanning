# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 13:49:51 2022

@author: nct76
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import re
import time
import pandas as pd
import logging
from tqdm import tqdm

def data_click_id_is_topic_thread(tag):
    return tag.has_attr('data-click-id') and tag.attrs['data-click-id'].startswith('topic-thread')



def extractFromCurrentPost(postloc):
    postRequest = Request(postloc, headers={'User-Agent': 'Mozilla/5.0'})
    postbytes = urlopen(postRequest).read()
    posthtml = postbytes.decode('utf8')
    postSoup = BeautifulSoup(posthtml, 'html.parser')
    current_post = postSoup.find_all(name='div', attrs={'class':'p-4 bg-mumsnet-forest dark:bg-mumsnet-forest-dark border-t border-b sm:border border-mumsnet-forest-border sm:rounded mt-4 lg:mt-1.5 py-2.5'})[0].text
    post_time = postSoup.find_all(name='span', attrs={'class':'lg:text-sm font-normal break-normal'})[0].text
    return current_post, post_time
    
logging.basicConfig(filename='./mumsnetpull.log',
                    format="%(asctime)s:%(levelname)s:%(message)s",
                    level=logging.INFO)
r = Request('https://www.mumsnet.com/Talk/parenting', headers={'User-Agent': 'Mozilla/5.0'})
mybytes = urlopen(r).read()

MnetParenting = mybytes.decode("utf8")

soup = BeautifulSoup(MnetParenting, 'html.parser')
first = re.compile("\\-*\\d+\\.*\\d*")
# for each page of posts
#firstpage, lastpage = first.findall(soup.find_all(name='li', attrs={'class':'first'})[0].text)

#382 + 463
posts = []
post_titles = []
post_dates = []
#%%
for p in tqdm(range(1, int(2)+1)):

    #print('Scraping page ' + str(p) + ' of ' + str(lastpage))
    pageurl = 'https://www.mumsnet.com/Talk/parenting?pg=' + str(p)
    #print('loading: ' + pageurl)
    currentRequest = Request(pageurl, headers={'User-Agent': 'Mozilla/5.0'})
    currentbytes = urlopen(currentRequest).read()

    currenthtml = currentbytes.decode("utf8")

    currentSoup = BeautifulSoup(currenthtml, 'html.parser')
    
    currentLinks = currentSoup.find_all(data_click_id_is_topic_thread)
    
    for l in currentLinks:
        
        postloc = l['href']
        
        trying = True
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
    
posts_df = pd.DataFrame({'titles':post_titles, 'date':post_dates, 'post':posts})
posts_df.to_feather('H:/redditProject/mumsnetparentinghealth.feather')