# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 12:11:03 2022

@author: Christopher Thornton
"""

# import the required libraries
import pandas as pd
from gensim.models import LdaModel
import gensim
from nltk.corpus import stopwords
from gensim.models import Phrases


#%% Loading in the tweets
filename = 'C:/Users/nct76/twarc_testing/tweets.csv'
# Load in the csv file created by twarc

tweets = pd.read_csv(filename)

# Store only the text in a list

posts = tweets.text


#%% Preprocessing the tweets
# This creates a list of words that you don't want to include 
# stopwords.words('english') is a list of all commonly used words in English 
# we can add to this any additional words, in this case http is excluded because it 
# often appears in links. 
stop_words = stopwords.words('english') + ['http']

# Use gensim built in preprocessing - does all the things preprocessing you would typically do in topic modelling
posts_preprocessed = gensim.parsing.preprocessing.preprocess_documents(posts)

posts_processed = []
# remove the stopwords and any words with fewer than three characters
for post in posts_preprocessed:
    post = [p for p in post if p not in stop_words and len(p)>3]
    posts_processed.append(post)

# Find all bigrams - word pairs that occur together more than 20 times
# e.g. feel like, fall asleep ect. convert to single words feel_like
bigram = Phrases(posts_processed, min_count=20)

# for each post add bigrams as additional words
for idx in range(len(posts_processed)):
    for token in bigram[posts_processed[idx]]:
        if '_' in token:
            # Token is a bigram, add to post.
            posts_processed[idx].append(token)
#%% Creating corpus and dictionary
# create a dictionary of words from the posts
dictionary = gensim.corpora.Dictionary(posts_processed)
#dictionary.filter_extremes(no_below=20, no_above=0.5)

# convert each post into a bag of words
# here each post becomes an unordered set of integers - each corresponds to a word in the dictionary
corpus = [dictionary.doc2bow(line) for line in posts_processed]
# we can look them up:
words_as_numbers = list(map(lambda x: x[0], corpus[1]))
translation = [dictionary[i] for i in words_as_numbers]
print(words_as_numbers)
print(translation)

#%% Apply the topic model
# We can change the parameters here depending on the dataset. 
# The most obvious is the num_topics, here we have six but if we suspect 
# that our data naturally contains more we may wish to increase this
#lda_models = []
number_of_topics  = 8
lda_model = LdaModel(corpus=corpus,
                         id2word=dictionary,
                         random_state=100,
                         num_topics=number_of_topics,
                         passes=20,
                         chunksize=1000,
                         decay=0.5,
                         offset=64,
                         eval_every=10,
                         iterations=1000,
                         gamma_threshold=0.001,
                         per_word_topics=True)


top_topics = lda_model.top_topics(corpus)

# Average topic coherence is the sum of topic coherences of all topics, divided by the number of topics.
avg_topic_coherence = sum([t[1] for t in top_topics]) / 6
print('Average topic coherence: ' + str(round(avg_topic_coherence,4)))

#%%

import pyLDAvis.gensim_models as gensimvis
import pyLDAvis
lda_viz = gensimvis.prepare(lda_model, corpus, dictionary)
pyLDAvis.save_html(lda_viz, 'twitterLDA15topics.html')
display_data = pyLDAvis.display(lda_viz)

import numpy as np

topicsperdoc = [lda_model.get_document_topics(post) for post in corpus]

posts_df = pd.DataFrame(posts)
singletopicperdoc = [max(lis,key=lambda item:item[1])[0] for lis in topicsperdoc]
singleprobperdoc = [max(lis,key=lambda item:item[1])[1] for lis in topicsperdoc]
posts_df['singletopicperdoc'] = singletopicperdoc
posts_df['singleprobperdoc'] = singleprobperdoc

modelwords = lda_viz[1]
topicnamesstr = []
for t in range(1,number_of_topics+1):
    topic = 'Topic' + str(t)
    topicwords = modelwords[modelwords.Category==topic]
    order = list(np.argsort(topicwords.loglift + topicwords.logprob)[-4:])
    order.reverse()
    top5 = topicwords.iloc[order]
    topic_string = ''
    for tp in top5.Term:
        topic_string = topic_string + str(tp) + '+'
    
    topicnamesstr.append(topic_string[0:-1])
    
postslikely_df = posts_df[posts_df.singleprobperdoc>=0.75]
individualtopics = pd.DataFrame()
for i in postslikely_df.singletopicperdoc.unique():
    p_A = postslikely_df[postslikely_df.singletopicperdoc==i]
    p_A['topicwords'] = topicnamesstr[i]
    individualtopics = individualtopics.append(p_A)

from nltk.sentiment import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

individualtopics['neg_sentiment'] = [sia.polarity_scores(post)['neg'] for post in individualtopics.text]
individualtopics['pos_sentiment'] = [sia.polarity_scores(post)['pos'] for post in individualtopics.text]
individualtopics['neu_sentiment'] = [sia.polarity_scores(post)['neu'] for post in individualtopics.text]

    