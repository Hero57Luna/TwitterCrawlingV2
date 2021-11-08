import json
import tweepy
import mysql.connector
import sys
import argparse
from TwitterAPI import TwitterAPI, TwitterOAuth, TwitterRequestError, TwitterConnectionError, TwitterPager

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="w9AuxZSTY9Eh5dfg",
    database="kultura"
)

mycursor = mydb.cursor()

consumer_key = "63WpEbrK3zrblLMKFORcjygvJ"
consumer_key_secret = "5mhAij5jbkcnmwa6Q0tNz0Jf2Xp6fhiQ4FTrE5j55nNmfcjIm9"
access_token = "1456092689418514433-mviRAFruatdVhtGfeDK84SH6VORJTC"
access_token_secret = "v36I2cY9NCvrDsdfvarBSl1OC7eV0QcflLTtCOjgzOpgR"

auth = tweepy.OAuthHandler(consumer_key, consumer_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

api_twitter_api = TwitterAPI(consumer_key, consumer_key_secret, access_token, access_token_secret, api_version='2')

result = {}
profile = {}
final = {}

parser = argparse.ArgumentParser(description='Get tweets from selected user')
parser.add_argument('-u', '--username', help='Target username', required='-p' in sys.argv, type=str)
parser.add_argument('-c', '--count', help='Amount of tweets to be crawled', required='-p' in sys.argv, type=str)
parser.add_argument('-r', '--replies', help='Get replies based on tweet id', action='store_true')
parser.add_argument('-i', '--id', help='Tweet id', type=str, required='-r' in sys.argv)
parser.add_argument('-p', '--post', help='Get post', action='store_true')
parser.add_argument('-k', '--keyword', help='Hashtag keyword', type=str, required='-ht' in sys.argv)
parser.add_argument('-lang', '--language', help='Base language for hashtag', type=str, nargs="?", default="id")
parser.add_argument('-ht', '--hashtag', help='Get hashtag', action='store_true')
args = parser.parse_args()


def get_tweets(username, count):
    try:
        print('Processing...')
        user = api.get_user(screen_name=username)
        followers = user.followers_count
        following = user.friends_count
        name = user.screen_name
        desc = user.description
        location = user.location
        screen_name = user.screen_name

        for tweets in tweepy.Cursor(api.user_timeline, screen_name=username, tweet_mode='extended').items(int(count)):
            tweet_id = tweets.id_str
            text = tweets.full_text
            created = tweets.created_at
            retweet_count = tweets.retweet_count
            likes_count = tweets.favorite_count

            result[tweet_id] = {
                'Text': text,
                'Retweet count': retweet_count,
                'Likes count': likes_count,
                'Date created': str(created)
            }

            insert_into_posts = "INSERT INTO twitter_post (screen_name, status_id, status_text, status_retweet_count, status_likes_count, status_created) VALUES (%s, %s, %s, %s, %s, %s)"
            value_posts = (name, tweet_id, text, retweet_count, likes_count, str(created))
            mycursor.execute(insert_into_posts, value_posts)
            mydb.commit()

        profile_output = {
            'Name': name,
            'Screen name': screen_name,
            'Description': desc,
            'Location': location,
            'Followers': followers,
            'Following': following,
            'Status': result
        }

        json_result = json.dumps(profile_output, indent=4)

        print('Done')
        with open('result.json', 'w') as f:
            return f.write(json_result)

    except ValueError as e:
        if e == 50:
            print('User not found')
            input('Press Enter to continue ')


def get_profile(username):
    user = api.get_user(screen_name=username)
    followers = user.followers_count
    following = user.friends_count
    name = user.name
    desc = user.description
    location = user.location
    screen_name = user.screen_name

    insert_into_profile = "INSERT IGNORE INTO twitter_profile (screen_name, name, description, location, followers, following) VALUES (%s, %s, %s, %s, %s, %s)"
    value_profile = (screen_name, name, desc, location, followers, following)
    mycursor.execute(insert_into_profile, value_profile)
    mydb.commit()


#  the function below are still work in progress
def get_tweets_replies(conversation_id):
    convo_id = []
    try:
        pager = TwitterPager(api_twitter_api, 'tweets/search/recent',
                             {'query': f'conversation_id:{conversation_id}', 'tweet.fields': 'conversation_id'})
        print("Retrieving replies...")
        for page in pager.get_iterator(wait=5):
            convo_id.append(page['id'])
        print("Done")

        print("Inserting to database...")
        for reply_result in convo_id:
            str_conv_id = str(conversation_id)
            str_reply_result = str(reply_result)
            screen_name = api.get_status(conversation_id)
            screen_name_user = screen_name.user.screen_name
            user = api.get_status(reply_result)
            name = user.user.screen_name
            text = user.text
            date = user.created_at

            sql = "INSERT INTO twitter_replies (screen_name, tweet_id, replies_id, replies_text, reply_by, date_created) VALUES (%s, %s, %s, %s, %s, %s)"
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


def get_hashtags(keyword, language):
    print("Retrieving hashtag...")
    for tweet in tweepy.Cursor(api.search_tweets, q="#{} -filter:retweets".format(keyword), lang=language,
                               tweet_mode="extended").items():
        tweet_id = tweet.id
        hashtag_text = tweet.full_text
        likes_count = tweet.favorite_count
        retweet_count = tweet.retweet_count
        tweet_by = tweet.user.screen_name
        date_created = tweet.created_at

        insert_into_hashtag = "INSERT INTO twitter_hashtag " \
                              "(tweet_id, text, likes_count, retweet_count, tweet_by, date_created) " \
                              "VALUES (%s, %s, %s, %s, %s, %s)"

        hashtag_values = (tweet_id, hashtag_text, likes_count, retweet_count, tweet_by, date_created)

        mycursor.execute(insert_into_hashtag, hashtag_values)
        mydb.commit()
    print("Done")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if args.replies and args.id:
            get_tweets_replies(args.id)
        elif args.post and args.username:
            get_profile(args.username)
            get_tweets(args.username, args.count)
        elif args.hashtag and args.keyword:
            get_hashtags(args.keyword, args.language)
    else:
        print("Cannot empty")