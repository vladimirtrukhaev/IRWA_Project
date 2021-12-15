import datetime
from random import random
import json
from faker import Faker

fake = Faker()


# fake.date_between(start_date='today', end_date='+30d')
# fake.date_time_between(start_date='-30d', end_date='now')
#
# # Or if you need a more specific date boundaries, provide the start
# # and end dates explicitly.
# start_date = datetime.date(year=2015, month=1, day=1)
# fake.date_between(start_date=start_date, end_date='+30y')

def get_random_date():
    """Generate a random datetime between `start` and `end`"""
    return fake.date_time_between(start_date='-30d', end_date='now')


def get_random_date_in(start, end):
    """Generate a random datetime between `start` and `end`"""
    return start + datetime.timedelta(
        # Get a random amount of seconds between `start` and `end`
        seconds=random.randint(0, int((end - start).total_seconds())), )


class Document:
    def __init__(self, tweet, username, date, hashtags, likes, retweets, url):
        self.tweet = tweet
        self.username = username
        self.date = date
        self.hashtags = hashtags
        self.likes = likes
        self.retweets = retweets
        self.url = url


def load_documents_corpus():
    """
    Load documents corpus from dataset_tweets_WHO.txt file
    :return:
    """

    global docs_info
    try:
        docs_info = {}
        with open("docs_info.txt", 'r') as file:
            info = json.load(file)
            for index, doc in info.enumerate():
                print(index, doc)
                tweet = doc[0]
                username = doc[1]
                date = doc[2]
                hashtags = doc[3]
                likes = doc[4]
                retweets = doc[5]
                url = doc[6]

                docs_info[index] = Document(tweet, username, date, hashtags, likes, retweets, url)


    except:

        doc = "dataset_tweets_WHO.txt"
        with open(doc, 'r') as file:
            data = json.load(file)

        # initializing dictionary "my_dict" where value is the tweet text and key its id
        keylist = []
        for key in data:
            keylist.append(key)

        my_dict = {}
        docs_info = {}
        info = {}

        for i in keylist:
            my_dict[i] = None
            docs_info[i] = None
            info[i] = None

        for key in data:
            # initializing my_dict
            tweet = []
            for i in data[key]["full_text"]:
                tweet.append(i)
            tweet1 = "".join(tweet)
            my_dict[key] = tweet1

            # creting docs_info
            tweet = data[key]["full_text"]
            username = data[key]["user"]["name"]
            date = data[key]["created_at"]
            hashtags = data[key]["entities"]["hashtags"]
            likes = data[key]["favorite_count"]
            retweets = data[key]["retweet_count"]
            try:
                url = data[key]["entities"]["media"][0]["expanded_url"]
            except:  # sometimes we weren't able to find the url in the data, then:
                url = "https://twitter.com/WHO/status/%s" % (data[key]["id_str"])

            #info = [tweet, username, date, hashtags,likes, retweets, url]

            docs_info[key] = Document(tweet, username, date, hashtags,likes, retweets, url)
            info[key] = [tweet, username, date, hashtags,likes, retweets, url]

        json_docs = json.dumps(info)
        with open("docs_info.txt", 'w') as f:
            f.write(json_docs)

        json_dict = json.dumps(my_dict)
        with open("my_dict_raw.txt", 'w') as f:
            f.write(json_dict)

    return docs_info



    ##### demo replace ith your code here #####
    #docs = []
    #for i in range(200):
        #docs.append(Document(fake.uuid4(), fake.text(), fake.text(), fake.date_this_year(), fake.email(), fake.ipv4()))
    #return docs
