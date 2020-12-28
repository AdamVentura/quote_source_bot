import json
import tweepy
import time
from keys import keys

CONSUMER_KEY = keys['consumer_key']
CONSUMER_SECRET = keys['consumer_secret']
ACCESS_TOKEN = keys['access_token']
ACCESS_TOKEN_SECRET = keys['access_token_secret']

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

print("Logged in.")

def check_mentions(api, keywords, since_id):
    print("Retrieving mentions")
    new_since_id = since_id
    for mention in tweepy.Cursor(api.mentions_timeline,
        since_id=since_id).items():
        new_since_id = max(mention.id, new_since_id)
        
        screen_name = mention.user.screen_name
            
        print(f"Mention: {mention.text}")

        tweet_id = mention.in_reply_to_status_id
        tweet = api.get_status(id = tweet_id)
        tweet = tweet.text
        print(f"Tweet: {tweet}")

        tweet = tweet.lower()
        tweet = tweet.replace('"', '')
        tweet = tweet.replace(' ', '')
        tweet = tweet.replace('”', '')
        tweet = tweet.replace('“', '')
        tweet = tweet.replace('’', '')
        tweet = tweet.replace(',', '')

        with open('quotes.json') as q:
            dataset = json.load(q)

        author_references = 0

        for data in dataset:
            quote = data["Quote"].lower()
            quote = quote.replace('"', '')
            quote = quote.replace(' ', '')
            quote = quote.replace('’', '')
            quote = quote.replace(',', '')
            if tweet in quote:
                author_references += 1
                if author_references == 1:
                    author = data["Author"]
                    reply = f"- {author}"
                    print("Just sourced a quote.")
                    api.update_status(
                        status=f"@{screen_name} {reply}",
                        in_reply_to_status_id=mention.id,
                    )
                elif author_references == 0:
                    print("Couldn't find the source of quote.")
                    api.update_status(
                        status=f"@{screen_name} Sorry @{screen_name}, I couldn't find the source of that quote.",
                        in_reply_to_status_id=mention.id,
                    )

            if not mention.user.following:
                tweet.user.follow()

            

        return new_since_id



def main():
    since_id = 1
    while True:
        since_id = check_mentions(api, [''], since_id)
        print("Waiting...")
        time.sleep(60)

if __name__ == "__main__":
    main()