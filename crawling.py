import json
import time
import tweepy
import argparse

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
        name = user.name
        desc = user.description
        locaton = user.location
        screen_name = user.screen_name

        for tweets in tweepy.Cursor(api.user_timeline, screen_name=username, tweet_mode='extended').items(int(count)):
            tweet_id = tweets.id_str
            text = tweets.full_text
            created = tweets.retweet_count
            retweet_count = tweets.retweet_count
            likes_count = tweets.favorite_count

            result[tweet_id] = {
                'Text': text,
                'Retweet count': retweet_count,
                'Likes count': likes_count,
                'Date created': str(created)
            }
        profile = {
            'Name': name,
            'Screen name': screen_name,
            'Description': desc,
            'Location': locaton,
            'Followers': followers,
            'Following': following,
            'Status': result
        }

        json_result = json.dumps(profile, indent=4)

        print('Done')
        with open('result.json', 'w') as f:
            return f.write(json_result)


    except tweepy.TweepError as e:
        if e.api_code == 50:
            print('User not found')
            input('Press Enter to continue ')


if __name__ == '__main__':
    get_tweets(args.username, args.count)