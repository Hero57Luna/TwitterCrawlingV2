import pandas as pd
import json
import time
from tkinter import *
import tweepy
from consolemenu import *
from consolemenu.items import *
from tkinter import filedialog
import os

# credentials to grant user access to twitter API
consumer_key = "OIpYHLyMhNyh2bMB0YGVwrix4"
consumer_key_secret = "NNbadTOk0a51liZXyBUkegFBXt0UnT5Mut6nWO2OsErkjfQ2TP"
access_token = "1438047431594176514-7ppLrU5d7yXbxWx078p8ph8di5bguZ"
access_token_secret = "17g1vECj8AEnf2XmI4y2rB2NUR8jxJ7VRehTGZVXHWYOW"

# authorization process
auth = tweepy.OAuthHandler(consumer_key, consumer_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

saved_file_location = []  # dir for where the file will be saved
result = {}  # for json file
profile = {}
final = {}

# function for generating target profile info
def GetProfile():
    try:
        username = input('Enter username: ')
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
        print('Screen name \t\t : {}'.format(screen_name))
        print('Description \t\t : {}'.format(desc))
        print('Location \t\t : {}'.format(locaton))
        print('Followers \t\t : {}'.format(follower))
        print('Following \t\t : {}'.format(following))
        print('===================================================')
        input('Press Enter to continue ')
    except tweepy.TweepError as e:
        if e.api_code == 50:
            print('User not found')
            input('Press Enter to continue ')
        else:
            print('Error with code {}'.format(e.api_code))
            input('Press Enter to continue ')

# getting tweets from target
def GetTweets():
    # check if the username given in the user input is exist and returns error if doesn't
    try:
        username = input('Enter username: ')
        print('Searching...')
        user = api.get_user(username)
        if (user):
            print('Found!')
            save_directory = input('Save to local? y/n ')
            if save_directory == 'y':
                OpenDirectoryDialog()
                print('The file will be saved to {}/result.json'.format(saved_file_location[0]))
            elif save_directory == 'n':
                print('not saved to local')
            else:
                while save_directory not in ('y', 'n'):
                    print('please enter valid input')
                    save_directory = input('Save to local? y/n ')
                    if save_directory == 'y':
                        OpenDirectoryDialog()
                        print('The file will be saved to {}/result.json'.format(saved_file_location[0]))
                    elif save_directory == 'n':
                        print('not saved to local')
                    else:
                        continue

            count = input('How many data do you want to extract? ')
            try:
                start = time.time()
                if save_directory == 'n':
                    print('Please wait...')
                    for tweets in tweepy.Cursor(api.user_timeline, screen_name='{}'.format(username), tweet_mode='extended').items(int(count)):
                        tweet_id = tweets.id_str
                        text = tweets.full_text
                        created = tweets.created_at
                        retweet_count = tweets.retweet_count
                        # replies_count = tweets.in_reply_to_status_id
                        likes_count = tweets.favorite_count
                        print('==========================================')
                        print('ID: {}'.format(tweet_id))
                        print('Tweets: {}'.format(text))
                        print('Retweet count: {}'.format(retweet_count))
                        # print('Replies count: {}'.format(replies_count))
                        print('Likes count: {}'.format(likes_count))
                        print('Date created: {}'.format(created))
                        print('==========================================')
                    input('Press Enter to continue ')
                elif save_directory == 'y':
                    user = api.get_user(username)
                    followers = user.followers_count
                    following = user.friends_count
                    name = user.name
                    desc = user.description
                    locaton = user.location
                    screen_name = user.screen_name
                    for tweets in tweepy.Cursor(api.user_timeline, screen_name='{}'.format(username), tweet_mode='extended').items(int(count)):
                        tweet_id = tweets.id_str
                        text = tweets.full_text
                        created = tweets.created_at
                        retweet_count = tweets.retweet_count
                        # replies_count = tweets.in_reply_to_status_id
                        likes_count = tweets.favorite_count

                        result[tweet_id] = {
                            'Text' : text,
                            'Retweet count' : retweet_count,
                            'Likes count' : likes_count,
                            'Date created' : str(created)
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

                    with open('{}/result.json'.format(saved_file_location[0]), 'w') as f:
                        json.dump(profile, f, indent=4)
                end = time.time()
                execution_time = end - start
                print('Done in {} s'.format(round(execution_time, 2)))
                input('Press Enter to continue ')
            except ValueError:
                print('Invalid input')
                input('Press Enter to continue ')
    except tweepy.TweepError as e:
        if e.api_code == 50:
            print('User not found')
            input('Press Enter to continue ')

def GetTags():
    tags = input('Enter tags: ')
    #  date = input('Since yyyy-mm-dd: ')
    for tweet in tweepy.Cursor(api.search, q="{}".format(tags), since='2020-01-01', count=100).items(100):
        Tweet = tweet.text
        User = tweet.user.name
        Tanggal = tweet.created_at
        print('=============================')
        print('Tweet : {}'.format(Tweet))
        print('User : {}'.format(User))
        print('Created at : {}'.format(Tanggal))
        print('=============================')
    #     csvWriter.writerow([Tanggal, Tweet.encode('utf-8'), User])
    # csvWriter = csv.writer(csvFile)
    # csvFile.close()

def Tags():
    for i in range(0, 10):
        print(i)

def GetTweetsReplies():
    username = input('Enter username: ')
    tweet_id = input('Enter tweet ID ')
    user = api.get_user(username)

    reply = []
    for replies in tweepy.Cursor(api.search, q='to:{}'.format(username), result_type='recent', truncated=False,
                                 timeout=100).items(1000):
        if (replies.in_reply_to_status_id_str == tweet_id):
            reply.append(replies.text)

    # for i in reversed(reply):
    #     print('========================================')
    #     print(i)
    #     print('========================================')
    print('Total replies is {} replies'.format(len(reply)))


def OpenDirectoryDialog():
    root = Tk()  # pointing root to Tk() to use it as Tk() in program.
    root.withdraw()  # Hides small tkinter window
    root.attributes('-topmost', True)  # Opened windows will be active. above all windows despite of selection.
    open_file = filedialog.askdirectory()  # Returns opened path as str
    saved_file_location.append(open_file)


def main():
    menu = ConsoleMenu("Twitter Data Crawling", "You are now in the main menu")

    get_profile = FunctionItem("About profile", GetProfile)
    get_tweets = FunctionItem("Get tweets", GetTweets)
    get_tags = FunctionItem("Get tags", GetTags)

    menu.append_item(get_profile)
    menu.append_item(get_tweets)
    menu.append_item(get_tags)


    menu.show()



if __name__ == '__main__':
    main()
