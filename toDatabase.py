import csv
import time
import pandas as pd
import mysql.connector
import tweepy
from TwitterAPI import TwitterAPI, TwitterOAuth, TwitterRequestError, TwitterConnectionError, TwitterPager

from TreeNode import TreeNode

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="twitter_post"
)

mycursor = mydb.cursor()

tweet_result = {}

# credentials to grant user access to twitter API
consumer_key = "OIpYHLyMhNyh2bMB0YGVwrix4"
consumer_key_secret = "NNbadTOk0a51liZXyBUkegFBXt0UnT5Mut6nWO2OsErkjfQ2TP"
access_token = "1438047431594176514-7ppLrU5d7yXbxWx078p8ph8di5bguZ"
access_token_secret = "17g1vECj8AEnf2XmI4y2rB2NUR8jxJ7VRehTGZVXHWYOW"

# authorization process
auth = tweepy.OAuthHandler(consumer_key, consumer_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

api_twitter_api = TwitterAPI(consumer_key, consumer_key_secret, access_token, access_token_secret, api_version='2')

names = ["raisa6690"]
conv_id = ["1455710059875368963"]


def get_new_tweets(names):
    print("Retrieving tweets")
    corpus = []
    for name in names:
        tweets = api.user_timeline(name, include_rts=False, count=10, tweet_mode="extended")
        time.sleep(4)
        corpus.extend(tweets)
    data = [[tweet.id_str, tweet.user.screen_name, tweet.full_text, tweet.created_at] for tweet in corpus]
    tweets = pd.DataFrame(data, columns=['tweet_id', 'screen_name', 'text', 'timestamp'])
    print(tweets.head)
    return tweets


def add_data(tweets):
    print("Retrieving additional data")
    ids = tweets.tweet_id
    conv_ids = []
    for id in ids:

        TWEET_ID = id
        TWEET_FIELDS = 'conversation_id'

        try:
            r = api_twitter_api.request(f'tweets/:{TWEET_ID}', {'tweet.fields': TWEET_FIELDS})

            for item in r:
                conv_ids.append(item['conversation_id'])


        except TwitterRequestError as e:
            print(e.status_code)
            for msg in iter(e):
                print(msg)

        except TwitterConnectionError as e:
            print(e)

        except Exception as e:
            print(e)

    tweets['conversation_id'] = conv_ids
    print(tweets)
    return tweets


def retrieve_replies(conversation_id):
    global root
    try:
        # GET ROOT OF THE CONVERSATION
        r = api_twitter_api.request(f'tweets/:{conversation_id}',
                                    {
                                        'tweet.fields': 'author_id,conversation_id,created_at,in_reply_to_user_id'
                                    })

        for item in r:
            root = TreeNode(item)
            # print(f'ROOT {root.id()}')

        # GET ALL REPLIES IN CONVERSATION

        pager = TwitterPager(api_twitter_api, 'tweets/search/recent',
                             {
                                 'query': f'conversation_id:{conversation_id}',
                                 'tweet.fields': 'author_id,conversation_id,created_at,in_reply_to_user_id'
                             })

        orphans = []

        for item in pager.get_iterator(wait=2):
            node = TreeNode(item)
            # print(f'{node.id()} => {node.reply_to()}')
            # COLLECT ANY ORPHANS THAT ARE NODE'S CHILD
            orphans = [orphan for orphan in orphans if not node.find_parent_of(orphan)]
            # IF NODE CANNOT BE PLACED IN TREE, ORPHAN IT UNTIL ITS PARENT IS FOUND
            if not root.find_parent_of(node):
                orphans.append(node)

        conv_id, child_id, text = root.list_l1()
        #         print('\nTREE...')
        # 	    root.print_tree(0)

        assert len(orphans) == 0, f'{len(orphans)} orphaned tweets'

    except TwitterRequestError as e:
        print(e.status_code)
        for msg in iter(e):
            print(msg)

    except TwitterConnectionError as e:
        print(e)

    except Exception as e:
        print(e)

    return conv_id, child_id, text


"""
Retrieves replies for a list of conversation ids (conv_ids
Returns a dataframe with columns [conv_id, child_id, text] tuple which shows every reply's tweet_id and text in the last two columns
"""


def reply_thread_maker(conv_ids):
    conv_id = []
    child_id = []
    text = []
    for id in conv_ids:
        conv_id1, child_id1, text1 = retrieve_replies(id)
        conv_id.extend(conv_id1)
        child_id.extend(child_id1)
        text.extend(text1)

    replies_data = {'conversation_id': conv_id,
                    'child_tweet_id': child_id,
                    'tweet_text': text}

    replies = pd.DataFrame(replies_data)
    print(replies)
    return replies


def generateToCSV():
    user = api.get_user("jokowi")
    follower = user.followers_count
    following = user.friends_count
    name = user.name
    desc = user.description
    location = user.location
    screen_name = user.screen_name

    data = desc.replace("\n", " ")

    strip_screen_name = screen_name.replace("\n", " ")
    strip_description = desc.replace("\n", " ")
    strip_location = location.replace("\n", " ")

    data = [strip_screen_name, strip_description, strip_location, follower, following]

    with open("twitter_profile.csv", "w", encoding="UTF8") as f:
        writer = csv.writer(f)

        writer.writerow(data)


def generatePostToCSV():
    user = api.get_user("jokowi")
    name = user.screen_name

    for tweets in tweepy.Cursor(api.user_timeline, screen_name="jokowi", tweet_mode="extended").items(3200):
        tweet_id = tweets.id_str
        text = tweets.full_text
        created = tweets.created_at
        retweet_count = tweets.retweet_count
        likes_count = tweets.favorite_count

        strip_post = text.replace("\n", " ")

        sql = "INSERT INTO post (screen_name, status_id, status_text, status_retweet_count, status_likes_count, status_created) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (name, tweet_id, strip_post, retweet_count, likes_count, str(created))
        mycursor.execute(sql, val)
        mydb.commit()
        print(tweet_id)


def get_tweets_replies():
    name = 'raisa6690'
    tweet_id = '1401358780449783813'

    replies = []
    for tweet in tweepy.Cursor(api.search, q='to:' + name, wait_on_rate_limit=True,
                               wait_on_rate_limit_notify=True).items():
        if hasattr(tweet, 'in_reply_to_status_id_str'):
            if tweet.in_reply_to_status_id_str == tweet_id:
                replies.append(tweet)

    for result in replies:
        print('========================')
        print(result.text)
        print('========================')

    print("total: " + str(len(replies)))

    # with open('replies_clean.csv', 'w', encoding='UTF-8') as f:
    #     csv_writer = csv.DictWriter(f, fieldnames=('user', 'text'))
    #     csv_writer.writeheader()
    #     for tweet in replies:
    #         row = {'user': tweet.user.screen_name, 'text': tweet.text.replace('\n', ' ')}
    #         csv_writer.writerow(row)


def update_urls(tweet, api, urls):
    tweet_id = tweet.id
    user_name = tweet.user.screen_name
    max_id = None
    replies = tweepy.Cursor(api.search, q='to:{}'.format(user_name),
                            since_id=tweet_id, max_id=max_id, tweet_mode='extended').items()

    for reply in replies:
        if (reply.in_reply_to_status_id == tweet_id):
            urls.append(get_twitter_url(user_name, reply.id))
            try:
                for reply_to_reply in update_urls(reply, api, urls):
                    pass
            except Exception:
                pass
        max_id = reply.id
        print(urls)
    return urls


def get_api():
    auth = tweepy.OAuthHandler(consumer_key, consumer_key_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api


def get_tweet(url):
    tweet_id = url.split('/')[-1]
    api = get_api()
    tweet = api.get_status(tweet_id)
    return tweet


def get_twitter_url(user_name, status_id):
    return "https://twitter.com/" + str(user_name) + "/status/" + str(status_id)


def get_hashtags():
    i = 0
    for tweet in tweepy.Cursor(api.search, q="#NNN", count=100, lang="id").items(100):
        i = i + 1
        print("==============================================")
        print(i)
        print(tweet.created_at, tweet.text)
        print("==============================================")


if __name__ == "__main__":
    add_data(get_new_tweets(names))
    #replies = reply_thread_maker(conv_id)
    #replies.to_csv("replies.csv")
    # replies.head()
    # get_new_tweets(names)
    # get_hashtags()
    # generateToCSV()
    # generatePostToCSV()
    # get_tweets_replies()
    # url = 'https://twitter.com/raisa6690/status/1401358780449783813'
    # api = get_api()
    # tweet = get_tweet(url)
    # urls = [url]
    # urls = update_urls(tweet, api, urls)
