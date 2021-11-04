import csv
import mysql.connector
import tweepy
from TwitterAPI import TwitterAPI, TwitterOAuth, TwitterRequestError, TwitterConnectionError, TwitterPager

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="twitter_post"
)

mycursor = mydb.cursor()

tweet_result = {}
replies_result = []

# credentials to grant user access to twitter API
consumer_key = "63WpEbrK3zrblLMKFORcjygvJ"
consumer_key_secret = "5mhAij5jbkcnmwa6Q0tNz0Jf2Xp6fhiQ4FTrE5j55nNmfcjIm9"
access_token = "1456092689418514433-mviRAFruatdVhtGfeDK84SH6VORJTC"
access_token_secret = "v36I2cY9NCvrDsdfvarBSl1OC7eV0QcflLTtCOjgzOpgR"

# authorization process
auth = tweepy.OAuthHandler(consumer_key, consumer_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

api_twitter_api = TwitterAPI(consumer_key, consumer_key_secret, access_token, access_token_secret, api_version='2')

names = ["raisa6690"]
conv_id = ["1455498487987015682"]


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


def get_tweets_replies(conversation_id):
    convo_id = []
    try:
        pager = TwitterPager(api_twitter_api, 'tweets/search/recent',
                             {'query': f'conversation_id:{conversation_id}', 'tweet.fields': 'conversation_id'})
        print("Retrieving replies...")
        for page in pager.get_iterator(wait=5):
            convo_id.append(page['id'])
        print("Done")

        print("Inserting to db")
        for reply_result in convo_id:
            str_conv_id = str(conversation_id)
            str_reply_result = str(reply_result)
            screen_name = api.get_status(conversation_id)
            screen_name_user = screen_name.user.screen_name
            user = api.get_status(reply_result)
            name = user.user.screen_name
            text = user.text
            date = user.created_at

            sql = "INSERT INTO replies (screen_name, tweet_id, replies_id, replies_text, reply_by, date_created) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (screen_name_user, str_conv_id, str_reply_result, text, name, str(date))
            mycursor.execute(sql, val)
            mydb.commit()
        print("Done")


    except TwitterRequestError as e:
        print(e.status_code)
        for msg in iter(e):
            print(msg)

    except TwitterConnectionError as e:
        print(e)

    except Exception as e:
        print(e)


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
    get_tweets_replies("1455498487987015682")
    # replies = reply_thread_maker(conv_id)
    # replies.to_csv("replies.csv")
    # replies = retrieve_replies("1455498487987015682")
    # print(replies)
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
