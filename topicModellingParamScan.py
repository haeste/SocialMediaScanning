#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 13:08:26 2022

@author: chris
"""


import pandas as pd
from gensim.models import LdaModel, LdaMulticore
import gensim.downloader as api
import gensim
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from gensim.models import Phrases
import re
import logging
import pickle
import json
from docx import Document
from docx.shared import Cm, Pt
def saveTable(univariablemodels, multivariablemodel , sig=0.05):
    word_document = Document()
    table = word_document.add_table(0, 0)
    table.style = 'TableGrid'
    first_column_width = 20
    column_with = 8
    table.add_column(Cm(first_column_width))
    table.add_column(Cm(column_with))
    table.add_column(Cm(column_with))
    table.add_column(Cm(column_with))
    table.add_column(Cm(column_with))
    table.add_column(Cm(column_with))
    table.add_column(Cm(column_with))
    first_row = table.add_row()
    first_row.cells[1].text = 'Univariable Regression (n=228)'
    first_row.cells[2].text = 'Multiple Regression (n=228) '
    second_row = table.add_row()
    second_row.cells[0].text = 'Independent Variable'
    second_row.cells[1].text = 'Coefficient (standardised) [95% confidence interval]'
    second_row.cells[2].text = 'p-value'
    second_row.cells[3].text = '$R^2$'
    second_row.cells[4].text = 'p-value'
    second_row.cells[5].text = 'p-value (adj)'
    second_row.cells[6].text = 'f'


    for w in range(1,6):
        curr_wave = df[(df.wave==w) & (df.pvals_adj<=sig)]
        next_row = table.add_row()
        next_row.cells[0].text = 'Wave ' + str(w)
        print(curr_wave)
        for index, row in curr_wave.iterrows():
            next_row = table.add_row()
            next_row.cells[0].text = data_dict[row['value']]
            next_row.cells[1].text = str(row['medians_r1'])
            next_row.cells[2].text = str(row['medians_r2'])
            next_row.cells[3].text = str(row['medians_w'])
            next_row.cells[4].text = str(round(row['pvals'],3))
            next_row.cells[5].text = str(round(row['pvals_adj'],3))
            next_row.cells[6].text = str(round(row['uvals'],3))
    margin = 1
    sections = word_document.sections
    for section in sections:
        section.top_margin = Cm(margin)
        section.bottom_margin = Cm(margin)
        section.left_margin = Cm(margin)
        section.right_margin = Cm(margin)

    word_document.save(fname + '.docx')
def britishise(string,american_to_british):

    for american_spelling, british_spelling in american_to_british.items():
        string = string.replace(american_spelling, british_spelling)
  
    return string

with open("./american_spellings.json", 'r') as url:
    american_to_british = json.load(url)   
#%%
lemmatizer = WordNetLemmatizer()
logging.basicConfig(filename='./gensim.log',
                    format="%(asctime)s:%(levelname)s:%(message)s",
                    level=logging.INFO)
                           
                           
data = pd.read_feather('./reddit_posts.feather')
mnet = pd.read_feather('./mumsnetparenting.feather')
mnet['title'] = mnet.titles
mnet['selftext'] = mnet.post
mnet = mnet.drop(columns=['titles', 'post'])
mnet['source'] = 'mumsnet'
data = data.drop(columns=['num_comments', 'score'])
data['source'] = 'reddit_Parenting'

data = data.append(mnet)
posts = data.title + ' ' + data.selftext

#%%
posts_cleaned = []
for p in posts:
    if ('PENIS PENIS' not in p) and ('[removed]' not in p) and ('Message withdrawn at poster\'s request.' not in p):
        pi = britishise(p, american_to_british)
        pi = pi.replace('diaper', 'nappy')
        pi = pi.replace('diapers', 'nappies')
        posts_cleaned.append(pi.replace('’', '\''))
        
stop_words = stopwords.words('english') + ['think', 'thing', 'said', 'want', 'know', 'toddler','kid',
                                           'babi','old','year','utf','keyword','ref','encod', 'month', 
                                           'com', 'edu', 'subject', 'lines', 'organization', 'article', 
                                           'amp', 'www', 'com', 'amazon', 'http', 'message', 'withdrawn',
                                           'poster', 'request', 'removed','daughter','she\'s', 'he\'s',
                                           'child', 'children']
posts_preprocessed = gensim.parsing.preprocessing.preprocess_documents(posts_cleaned)
posts_processed = []
for post in posts_preprocessed:
    post = [p for p in post if p not in stop_words and (len(p)>3)]
    posts_processed.append(post)

bigram = Phrases(posts_processed, min_count=20)
#%%
for idx in range(len(posts_processed)):
    for token in bigram[posts_processed[idx]]:
        if '_' in token:
            # Token is a bigram, add to document.
            posts_processed[idx].append(token)

with open('./texts.pkl', 'wb') as f:
    pickle.dump(posts_processed, f)
#%%
cp = gensim.corpora.Dictionary(posts_processed)
cp.filter_extremes(no_below=20, no_above=0.5)
restricted_words = stopwords.words('english')
corpus = [cp.doc2bow(line) for line in posts_processed if line not in restricted_words]
#%%
ldamodels = []
coherence = []
for numtopics in range(3,35):
    ldamods = []
    for r_s in range(1,10):
        lda_model = LdaMulticore(corpus=corpus,
                                 id2word=cp,
                                 random_state=r_s,
                                 num_topics=numtopics,
                                 passes=20,
                                 chunksize=1000,
                                 batch=False,
                                 decay=0.5,
                                 offset=64,
                                 eval_every=10,
                                 iterations=1000,
                                 gamma_threshold=0.001,
                                 per_word_topics=True)    
        top_topics = lda_model.top_topics(corpus) #, num_words=20)
        ldamods.append(lda_model)
        avg_topic_coherence = sum([t[1] for t in top_topics]) / numtopics
        print('Average topic coherence: %.4f.' % avg_topic_coherence)
        coherence.append(avg_topic_coherence)
    ldamodels.append(ldamods)


with open('./ldamodels.pkl', 'wb') as f:
    pickle.dump(ldamodels, f)

