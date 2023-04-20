# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 16:09:16 2022

@author: nct76
"""

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

url_health = "https://www.ndcs.org.uk/your-community/threads/thread-details/?thread="


posts = []
post_titles = []
post_dates = []
#%%
for p in tqdm(range(1, int(200)+1)):

    #print('Scraping page ' + str(p) + ' of ' + str(lastpage))
    pageurl = url_health + str(p)
    #print('loading: ' + pageurl)
    currentRequest = Request(pageurl, headers={'User-Agent': 'Mozilla/5.0'})
    currentbytes = urlopen(currentRequest).read()

    currenthtml = currentbytes.decode("utf8")

    currentSoup = BeautifulSoup(currenthtml, 'html.parser')

    currentLinks = currentSoup.find_all(name='div', attrs={'class':'thread-post-item__body'})
    for p in currentLinks:
        posts.append(p.text)

pd.DataFrame(pd.Series(posts)).to_csv('NDCS_posts.csv')
