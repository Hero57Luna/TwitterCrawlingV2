import tweepy
import mysql.connector
import csv

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="w9AuxZSTY9Eh5dfg",
    database="kultura"
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

    for tweets in tweepy.Cursor(api.user_timeline, screen_name = "jokowi", tweet_mode="extended").items(3200):
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

if __name__ == "__main__":
    # generateToCSV()
    # generatePostToCSV()
    print(mydb)