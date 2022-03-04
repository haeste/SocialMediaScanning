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

logging.basicConfig(filename='./mumsnetpull.log',
                    format="%(asctime)s:%(levelname)s:%(message)s",
                    level=logging.INFO)
def extractFromCurrentPost(postloc):
    postRequest = Request(postloc, headers={'User-Agent': 'Mozilla/5.0'})
    postbytes = urlopen(postRequest).read()
    posthtml = postbytes.decode('utf8')
    postSoup = BeautifulSoup(posthtml, 'html.parser')
    current_post = postSoup.find_all(name='div', attrs={'class':'talk-post'})[0].text
    post_time = postSoup.find_all(name='span', attrs={'class':'post_time'})[0].text
    return current_post, post_time
    
r = Request('https://www.mumsnet.com/Talk/parenting', headers={'User-Agent': 'Mozilla/5.0'})
mybytes = urlopen(r).read()

MnetParenting = mybytes.decode("utf8")

soup = BeautifulSoup(MnetParenting, 'html.parser')
first = re.compile("\\-*\\d+\\.*\\d*")
# for each page of posts
firstpage, lastpage = first.findall(soup.find_all(name='li', attrs={'class':'first'})[0].text)
posts = []
post_titles = []
post_dates = []
#382
for p in tqdm(range(int(firstpage), int(lastpage))):
    #print('Scraping page ' + str(p) + ' of ' + str(lastpage))
    pageurl = 'https://www.mumsnet.com/Talk/parenting?pg=' + str(p)
    #print('loading: ' + pageurl)
    currentRequest = Request(pageurl, headers={'User-Agent': 'Mozilla/5.0'})
    currentbytes = urlopen(currentRequest).read()

    currenthtml = currentbytes.decode("utf8")

    currentSoup = BeautifulSoup(currenthtml, 'html.parser')
    
    currentTable = BeautifulSoup(str(soup.find_all(name='table', attrs={'id':'threads'})[0]), 'html.parser')
    currentLinks = currentTable.find_all('a')
    for l in currentLinks:
        if len(l.attrs) == 1 and l.attrs['href'].startswith('parenting'):
            
            postloc = 'https://www.mumsnet.com/Talk/' + l['href']
            
            trying = True
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
        
posts_df = pd.DataFrame({'titles':post_titles, 'date':post_dates, 'post':posts})
posts_df.to_feather('./mumsnetparenting.feather')