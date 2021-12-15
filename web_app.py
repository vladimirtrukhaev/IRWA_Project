import os
from json import JSONEncoder
from datetime import datetime
import nltk
from flask import Flask, render_template
from flask import request
from collections import Counter
from app.analytics.analytics_data import AnalyticsData, Click
from app.core import utils
from app.search_engine.objects import StatsDocument
from app.search_engine.search_engine import SearchEngine

# *** for using method to_json in objects ***
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default

# end lines ***for using method to_json in objects ***



app = Flask(__name__)

corpus = utils.load_documents_corpus()
searchEngine = SearchEngine(corpus)
analytics_data = AnalyticsData()



@app.route('/')
def search_form():
    return render_template('index.html', page_title="Welcome")


@app.route('/search', methods=['POST'])
def search_form_post():
    search_query = request.form['search-query']

    results = searchEngine.search(search_query)
    found_count = len(results)

    return render_template('results.html', results_list=results, page_title="Results", found_counter=found_count)


@app.route('/doc_details', methods=['GET'])
def doc_details():
    # getting request parameters:
    # user = request.args.get('user')
    clicked_doc_id = request.args["id"]

    if clicked_doc_id in analytics_data.fact_clicks.keys():
        analytics_data.fact_clicks[clicked_doc_id].counter += 1
    else:
        analytics_data.fact_clicks[clicked_doc_id] = Click(clicked_doc_id, corpus[str(clicked_doc_id)].tweet, 1)




    print("click in id={} - fact_clicks len: {}".format(clicked_doc_id, len(analytics_data.fact_clicks)))

    data = corpus[(clicked_doc_id)]
    t = data.tweet
    u = data.username
    l = data.likes
    r = data.retweets
    d0 = data.date.split()
    d = d0[2] +" "+ d0[1] +" "+ d0[5] +" " + d0[3]
    h = ""
    for i in range (0, len(data.hashtags)):
        h += data.hashtags[i]["text"]
    url = data.url

    return render_template('doc_details.html', tweet = t, likes = l, retweets = r, hashtags = h, url = url, user = u, date = d )


@app.route('/stats', methods=['GET'])
def stats():
    """
    Show simple statistics example. ### Replace with dashboard ###
    :return:
    """
    ### Start replace with your code ###
    docs = []

    for doc_id in analytics_data.fact_clicks:
        row: Document = corpus[doc_id]
        count = analytics_data.fact_clicks[doc_id].counter
        doc = StatsDocument(doc_id, row.tweet, row.username, row.date, row.likes, row.hashtags, row.retweets, row.url, count)
        docs.append(doc)

    # simulate sort by ranking
    docs.sort(key=lambda doc: doc.count, reverse=True)

    browser_list = list()
    browser = request.headers.get('User-Agent')
    browser_list.append(browser)

    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y %H:%M:%S")

    ip_list = list()
    ip_add = request.remote_addr
    ip_list.append(ip_add)

    return render_template('stats.html', clicks_data=docs, browser=browser_list,
                           date_time=date_time, ip_add=ip_list)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    visited_docs = list(analytics_data.fact_clicks.values())
    for doc in visited_docs: print(doc)
    # simulate sort by ranking
    #visited_docs.sort(key=lambda doc: doc.counter, reverse=True)


    return render_template('dashboard.html', visited_docs=visited_docs)


@app.route('/sentiment')
def sentiment_form():
    return render_template('sentiment.html')


@app.route('/sentiment', methods=['POST'])
def sentiment_form_post():
    text = request.form['text']
    nltk.download('vader_lexicon')
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    score = ((sid.polarity_scores(str(text)))['compound'])
    return render_template('sentiment.html', score=score)


if __name__ == "__main__":
    app.run(port=8088, host="0.0.0.0", threaded=False, debug=True)