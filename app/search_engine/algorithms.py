
import re
import json
import math
import collections
from collections import Counter
import numpy as np
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from numpy import linalg as la
from array import array
from numpyencoder import NumpyEncoder
#from app.search_engine.search_engine import SearchEngine

def lowering(d):
    for key in d:
        d[key] = d[key].lower()
    return d

def cleaning(d):
    for key in d:
        d[key] = ["".join(re.sub(r'[^A-Za-z0-9 #]', ' ', i) for i in d[key])]
    return d


def tokenize(d):
    for key in d:
        for sentence in d[key]:
            d[key] = sentence.split()
    return d


def stpwords(d):
    languages = ["english", "spanish", "french"]
    for language in languages:
        stop_words = set(stopwords.words(language))
        for key in d:
            d[key] = [word for word in d[key] if word not in stop_words]
    return d

def stemming(d):
    stemmer = PorterStemmer()
    for key in d.keys():
        d[key] = [stemmer.stem(word) for word in d[key]]
    return d


def build_terms(query):  # used to process query text
    """
    Preprocess the input query removing stop words, stemming,
    transforming in lowercase and return the tokens of the text.

    Argument:
    query -- string (text) to be preprocessed

    Returns:
    query - a list of tokens corresponding to the input text after the preprocessing
    """

    stemmer = PorterStemmer()
    stop_words = set(stopwords.words("english"))
    query=  query.lower() ## Transform in lowercase
    query=  query.split() ## Tokenize the text to get a list of terms
    query =[word for word in query if not word in stop_words]  ##eliminate the stopwords
    query =[stemmer.stem(word) for word in query] ## perform stemming

    return query


def rank_documents(terms, docs, index, idf, tf):
    """
    Perform the ranking of the results of a search based on the tf-idf weights

    Argument:
    terms -- list of query terms
    docs -- list of documents, to rank, matching the query
    index -- inverted index data structure
    idf -- inverted document frequencies
    tf -- term frequencies

    Returns:
    Print the list of ranked documents
    """
    # I'm interested only on the element of the docVector corresponding to the query terms
    doc_vectors = collections.defaultdict(lambda: [0] * len(terms))  # I call doc_vectors[k] for a nonexistent key k, the key-value pair (k,[0]*len(terms)) will be automatically added to the dictionary
    query_vector = [0] * len(terms)

    # compute the norm for the query tf
    query_terms_count = collections.Counter(terms)
    query_norm = la.norm(list(query_terms_count.values()))

    for termIndex, term in enumerate(terms):  # termIndex is the index of the term in the query
        if term not in index:
            continue

        ## Compute tf*idf(normalize TF as done with documents)
        query_vector[termIndex] = query_terms_count[term] / len(terms) * idf[term]

        # Generate doc_vectors for matching docs
        for doc_index, (doc, postings) in enumerate(index[term]):
            if doc in docs:
                doc_vectors[doc][termIndex] = tf[term][doc_index] * idf[term]  # TODO: check if multiply for idf

    # Calculate the score of each doc
    # compute the cosine similarity between queyVector and each docVector:
    # HINT: you can use the dot product because in case of normalized vectors it corresponds to the cosine similarity
    #print("docVec",curDocVec)
    doc_scores = [[np.dot(curDocVec, query_vector), doc] for doc, curDocVec in doc_vectors.items()]
    doc_scores.sort(reverse=True)
    result_docs = [x[1] for x in doc_scores]
    # print document titles instead if document id's
    # result_docs=[ title_index[x] for x in result_docs ]
    if len(result_docs) == 0:
        print("No results found, try again")
        query = input()
        docs = search_alg(query, index)
    return result_docs



def create_index_tfidf(my_dict, num_documents):
    """
    Implement the inverted index and compute tf, df and idf

    Argument:
    my_dict -- collection of Wikipedia articles
    num_documents -- total number of documents

    Returns:
    index - the inverted index (implemented through a Pyhon dictionary) containing terms as keys and the corresponding
    list of document these keys appears in (and the positions) as values.
    tf - normalized term frequency for each term in each document
    df - number of documents each term appear in
    idf - inverse document frequency of each term
    """
    try:
        with open("index.txt", 'r') as file:
            index = json.load(file)
        with open("tf.txt", 'r') as file:
            tf = json.load(file)
        with open("idf.txt", 'r') as file:
            idf = json.load(file)

    except:
        index = collections.defaultdict(list)
        tf = collections.defaultdict(list)  # term frequencies of terms in documents (documents in the same order as in the main index)
        df = collections.defaultdict(int)  # document frequencies of terms in the corpus
        idf = collections.defaultdict(float)
        for doc in my_dict:
            current_tweet_index = {}
            for position, term in enumerate(my_dict[doc]):  # terms contains page_title + page_text. Loop over all terms
                try:
                    # if the term is already in the index for the current page (current_tweet_index)
                    # append the position to the corresponding list
                    current_tweet_index[term][1].append(position)
                except:
                    # Add the new term as dict key and initialize the array of positions and add the position
                    current_tweet_index[term] = [doc, [position]]  # [doc, np.array('I', [position])] 'I' indicates unsigned int (int in Python)

            # normalize term frequencies
            # Compute the denominator to normalize term frequencies (formula 2 above)
            # norm is the same for all terms of a document.
            norm = 0
            for term, posting in current_tweet_index.items():
                # posting will contain the list of positions for current term in current document.
                # posting ==> [current_doc, [list of positions]]
                # you can use it to infer the frequency of current term.
                norm += len(posting) ** 2
            norm = math.sqrt(norm)

            # calculate the tf(dividing the term frequency by the above computed norm) and df weights
            for term, posting in current_tweet_index.items():
                # append the tf for current term (tf = term frequency in current doc/norm)
                tf[term].append(np.round(len(posting) / norm, 4))  ## SEE formula (1) above
                # increment the document frequency of current term (number of documents containing the current term)
                df[term] = tf[term]  # increment DF for current term

            # merge the current page index with the main index
            for term_page, posting_page in current_tweet_index.items():
                index[term_page].append(posting_page)

            # Compute IDF following the formula (3) above. HINT: use np.log
            for term in df:
                idf[term] = np.round(np.log(float(num_documents / len(df[term]))), 4)

        json_dict = json.dumps(index, cls=NumpyEncoder)
        with open("index.txt", 'w') as f:
            f.write(json_dict)
        json_dict = json.dumps(tf)
        with open("tf.txt", 'w') as f:
            f.write(json_dict)
        json_dict = json.dumps(idf)
        with open("idf.txt", 'w') as f:
            f.write(json_dict)

    return index, tf, idf

def search_alg(query, index):
    docs = set()
    for term in query:
        try:
            # store in term_docs the ids of the docs that contain "term"
            term_docs = [posting[0] for posting in index[term]]

            # docs = docs Union term_docs
            docs = docs.union(term_docs)
        except:
            # term is not in index
            pass
    docs = list(docs)

    return docs