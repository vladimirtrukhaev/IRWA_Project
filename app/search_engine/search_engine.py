import random
import json
import collections
from app.core.utils import get_random_date
from app.search_engine.algorithms import lowering
from app.search_engine.algorithms import cleaning
from app.search_engine.algorithms import tokenize
from app.search_engine.algorithms import stemming
from app.search_engine.algorithms import stpwords
from app.search_engine.algorithms import build_terms
from app.search_engine.algorithms import create_index_tfidf
from app.search_engine.algorithms import rank_documents
from app.search_engine.algorithms import search_alg

def build_data():
    try:
        doc = "my_dict.txt"
        with open(doc, 'r') as file:
            my_dict = json.load(file)

    except:
        doc = "my_dict_raw.txt"
        with open(doc, 'r') as file:
            my_dict = json.load(file)

        my_dict = lowering(my_dict)
        my_dict = cleaning(my_dict)
        my_dict = tokenize(my_dict)
        my_dict = stpwords(my_dict)
        my_dict = stemming(my_dict)

    return my_dict

class SearchEngine:
    """educational search engine"""
    #i = 12345
    def __init__(self, corpus):
        my_dict = build_data()
        num_documents = len(my_dict)
        self.info_dict = corpus
        self.index, self.tf, self.idf = create_index_tfidf(my_dict, num_documents)

    def search(self, search_query):
        print("Search query:", search_query)
        query = build_terms(search_query)
        docs = search_alg(query, self.index) #finding possible matching docs
        results = rank_documents(query, docs, self.index, self.idf, self.tf)

        #building the output
        output = []
        for result in results:
            d = self.info_dict[result]
            doc_page = "doc_details?id={}".format(result)
            #modificar variables para hacerlo más simple

            tweet_title = d.tweet[0:100]

            d0 = d.date.split()
            date = d0[2] + " " + d0[1] + " " + d0[5] + " " + d0[3]

            output.append(TweetInfo(tweet_title, date, d.likes, d.retweets, doc_page))

        return output


class TweetInfo:
    def __init__(self, title_tweet, date,likes, retweets, doc_page):
        self.title_tweet = title_tweet
        self.date = date
        self.likes = likes
        self.retweets = retweets
        self.doc_page = doc_page
