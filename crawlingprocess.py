import pandas as pd
import tweepy
from consolemenu import *
from consolemenu.items import *

# credentials to grant user access to twitter API
consumer_key = "OIpYHLyMhNyh2bMB0YGVwrix4"
consumer_key_secret = "NNbadTOk0a51liZXyBUkegFBXt0UnT5Mut6nWO2OsErkjfQ2TP"
access_token = "1438047431594176514-7ppLrU5d7yXbxWx078p8ph8di5bguZ"
access_token_secret = "17g1vECj8AEnf2XmI4y2rB2NUR8jxJ7VRehTGZVXHWYOW"

# authorization process
auth = tweepy.OAuthHandler(consumer_key, consumer_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def UserData():
    username = input('Enter username: ')
    return username

def GetProfile():
    try:
        username = input('Enter username: ')
        profile = []
        user = api.get_user(username)
        follower = user.followers_count
        following = user.friends_count
        name = user.name
        desc = user.description
        locaton = user.location
        screen_name = user.screen_name
        print('===================================================')
        print('The user you are looking for has the following:')
        print('===================================================')
        print('Name \t\t\t : {}'.format(name))
        print('Screen name \t : {}'.format(screen_name))
        print('Description \t : {}'.format(desc))
        print('Location \t\t : {}'.format(locaton))
        print('Followers \t\t : {}'.format(follower))
        print('Following \t\t : {}'.format(following))
        print('===================================================')
    except tweepy.TweepError as e:
        if e.api_code == 50:
            print('User not found')
        else:
            print('Error with code {}'.format(e.api_code))

def GetTweets():
    reply = []
    try:
        username = input('Enter username: ')
        user = api.get_user(username)
        if (user):
            count = input('How many data do you want to extract? ')
            try:
                print('Please wait...')
                for tweets in tweepy.Cursor(api.user_timeline, screen_name = '{}'.format(username), tweet_mode = 'extended').items(int(count)):
                    tweet_id = tweets.id_str
                    text = tweets.full_text
                    created = tweets.created_at
                    retweet_count = tweets.retweet_count
                    replies_count = tweets.in_reply_to_status_id
                    likes_count = tweets.favorite_count
                    for replies in tweepy.Cursor(api.search, q='to:{}'.format(username), result_type='recent').items(100):
                        if(replies.in_reply_to_status_id_str == tweet_id):
                            reply.append(replies.text)
                    print('==========================================')
                    print('ID: {}'.format(tweet_id))
                    print('Tweets: {}'.format(text))
                    print('Retweet count: {}'.format(retweet_count))
                    print('Likes count: {}'.format(likes_count))
                    print('Replies: {}'.format(reply))
                    print('Date created: {}'.format(created))
                    print('==========================================')
            except ValueError:
                print('Invalid input')
    except tweepy.TweepError as e:
        if e.api_code == 50:
            print('User not found')

def main():
    menu = ConsoleMenu("Twitter Data Crawling", "You are now in the main menu")

    get_profile = FunctionItem("About profile", GetProfile)
    get_tweets = FunctionItem("Get tweets", GetTweets)

    menu.append_item(get_profile)
    menu.append_item(get_tweets)

    menu.show()

if __name__ == '__main__':
    main()