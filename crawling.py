import json
import time
import tweepy
import mysql.connector
import argparse
import csv

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="w9AuxZSTY9Eh5dfg",
    database="kultura"
)

mycursor = mydb.cursor()

consumer_key = "OIpYHLyMhNyh2bMB0YGVwrix4"
consumer_key_secret = "NNbadTOk0a51liZXyBUkegFBXt0UnT5Mut6nWO2OsErkjfQ2TP"
access_token = "1438047431594176514-7ppLrU5d7yXbxWx078p8ph8di5bguZ"
access_token_secret = "17g1vECj8AEnf2XmI4y2rB2NUR8jxJ7VRehTGZVXHWYOW"

auth = tweepy.OAuthHandler(consumer_key, consumer_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

result = {}
profile = {}
final = {}

parser = argparse.ArgumentParser(description='Get tweets from selected user')
parser.add_argument('-u', '--username', type=str, help='Target username', required=True)
parser.add_argument('-c', '--count', type=int, help='Amount of tweets to be crawled', required=True)
args = parser.parse_args()


def get_tweets(username, count):
    try:
        print('Processing...')
        user = api.get_user(username)
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

    except tweepy.TweepError as e:
        if e.api_code == 50:
            print('User not found')
            input('Press Enter to continue ')


def get_profile(username):
    user = api.get_user(username)
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
def get_tweets_replies():
    name = 'jokowi'
    tweet_id = '1454981763982192641'

    replies = []
    for tweet in tweepy.Cursor(api.search, q='to:' + name, result_type='recent', timeout=999999).items():
        if hasattr(tweet, 'in_reply_to_status_id_str'):
            if (tweet.in_reply_to_status_id_str == tweet_id):
                replies.append(tweet)

    with open('replies_clean.csv', 'w') as f:
        csv_writer = csv.DictWriter(f, fieldnames=('user', 'text'))
        csv_writer.writeheader()
        for tweet in replies:
            row = {'user': tweet.user.screen_name, 'text': tweet.text.replace('\n', ' ')}
            csv_writer.writerow(row)


def get_hashtags():
    for tweet in tweepy.Cursor(api.search, q="#gajayanmemanggil", count=100,
                               lang="en",
                               since="2017-04-03").items():
        print(tweet.created_at, tweet.text)


def main(username, count):
    get_tweets(username=username, count=count)
    get_profile(username=username)


if __name__ == '__main__':
    #  main(args.username, args.count)
    get_hashtags()
