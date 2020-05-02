# Program to control listening to requests from users to the bot.
import tweepy
#from secrets import *
import os
from astrobotph import tweet_reply

# ============= For use on Heroku ==============================
C_KEY = os.environ['C_KEY']
C_SECRET = os.environ['C_SECRET']
A_TOKEN = os.environ['A_TOKEN']
A_TOKEN_SECRET = os.environ['A_TOKEN_SECRET']
# ==============================================================

class StreamListener(tweepy.StreamListener):

    def __init__(self, api):
        self.api = api
        self.me = api.me()

    def on_status(self, status):
        if hasattr(status, "retweeted_status"): # ignore retweets
            return
        #elif status.in_reply_to_status_id is not None or status.user.id == self.me.id:
        elif status.user.id == self.me.id or status.user.screen_name == 'AstRobotPh':
            #  I'm its author so, ignore it
            return
        else:
            try:
                tweet_text = status.extended_tweet["full_text"]
            except AttributeError:
                tweet_text = status.text
            except Exception as e:
                print("Status issue in bot_stream")
                print(e)

            try:
                print("replying!")
                # pipe calculation away to this routine to avoid backlog and IncompleteRead
                print(tweet_text)
                tweet_reply(tweet_text, status.user.screen_name, status.id_str)
            except Exception as e:
                print("Tweet reply failed in bot_stream.")
                print(e)

    def on_error(self, status_code):
        #if status_code == 420:
        print("astrobotph_stream.py error code: ", status_code)
        return True

    def on_disconnect(self, notice):
        return True


if __name__ == "__main__":

    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
    auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
    api = tweepy.API(auth)


    while True: # used because connection was randomly resetting quite a lot.

        stream_listener = StreamListener(api)
        stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

        try:
            # use ID rather than username
            stream.filter(track=['@AstRobotPh'])

        except Exception as e:
            print("Stream error. Restarting via while loop")
            print(e)
