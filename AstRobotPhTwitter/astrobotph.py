# Program to generate the title and tweet to twitter's API.
import tweepy
import numpy as np
import itertools
import time, re, os
from random import randint
from keras.models import Model, load_model
from keras.preprocessing.text import Tokenizer
#from secrets import *

bot_username = 'AstRobotPh'
logfile_name = bot_username + ".log"

# ============= For use on Heroku ==============================
A_TOKEN = os.environ['A_TOKEN']
A_TOKEN_SECRET = os.environ['A_TOKEN_SECRET']
C_KEY = os.environ['C_KEY']
C_SECRET = os.environ['C_SECRET']
# ==============================================================

# ==== global constants (yeah, I know...) =======
seq_length = 10
model = load_model('./astroph_no_dropout_100.h5')

# load in training titles to check originality
training = open("./training_titles.txt", "r")
training_titles = []
for line in training:
    training_titles.append(line.strip())
# ===============================================


def load_credentials():
    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
    auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
    api = tweepy.API(auth)
    return api

def log(message):
    """Log message to logfile."""
    path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(path, logfile_name), 'a+') as f:
        t = strftime("%d %b %Y %H:%M:%S", gmtime())
        f.write("\n" + t + " " + message)


def sample_with_temp(preds, temperature=1.0):
    # whether to select the most likely word, or randomise a bit
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

def tokenize():
    # tokenize all the possible words
    filename = "./papertitles_startrek_text.txt"
    with open(filename, encoding='utf-8-sig') as f:
        text = f.read()

    # tokenize by words, not chars
    tokenizer = Tokenizer(char_level = False, filters = '')
    tokenizer.fit_on_texts([text])

    return tokenizer

def capitalizer(title):
    # switch back from smallcaps to proper title punctuation

    unimportant=["a", "an", "the", "am" ,"is", "are", "and", "of", "in" , "on", "with", "from", "to", "as", "by", "for"]
    capitalize = ["ska", "ngc", "hd", "3d", "ii", 'sdss', 'grb']

    resp=""
    v = title.split()
    for idx, x in enumerate(v):
        if x not in unimportant:
            if x in capitalize:
                resp += (" " + x.upper())
            else:
                #resp += (" " + x.title())
                resp += (" " + ''.join(x.capitalize()))
        else:
            if idx == 0: # first word
                resp += (" " + ''.join(x.capitalize()))
            else:
                resp += (" " + x)

    return resp


def generate_text(seed_text, next_words, model, max_sequence_len, temp):

    output_text = seed_text
    start_title = '| ' * seq_length
    tokenizer = tokenize()

    seed_text = start_title + seed_text

    for _ in range(next_words):
        token_list = tokenizer.texts_to_sequences([seed_text])[0]
        token_list = token_list[-max_sequence_len:]
        token_list = np.reshape(token_list, (1, max_sequence_len))

        probs = model.predict(token_list, verbose=0)[0]
        y_class = sample_with_temp(probs, temperature = temp)

        if y_class == 0:
            output_word = ''
        else:
            output_word = tokenizer.index_word[y_class]

        if output_word == "|": # end of title
            break

        output_text += output_word + ' '
        seed_text += output_word + ' '

    return output_text

def generate_title(training_titles, seed_text = " "):

    gen_words = 35 # max words (will generate less if thinks title is shorter)
    temperature = 0.8  # measure of randomness in word choice

    paper_title = generate_text(seed_text, gen_words, model, seq_length, temperature)

    # remove duplicate words
    paper_title = ' '.join(c[0] for c in itertools.groupby(paper_title.split()))

    # check if generated title is in training set
    if paper_title in training_titles:
        print("match: ", paper_title)
        # what a cheat! Try again.
        paper_title = generate_title(training_titles, seed_text)
    else:
        paper_title = capitalizer(paper_title)

    return paper_title

def tweet(text):
    """Send out the text as a tweet."""
    # Twitter authentication
    api = load_credentials()

    # Send the tweet and log success or failure
    try:
        api.update_status(status=text)
    except tweepy.error.TweepError as e:
        print(e.reason)

def tweet_reply(intext, screen_name, id):
    """Grab parameters and send reply to a tweet."""
    # Twitter authentication
    api = load_credentials()

    try:
        # use only double quotes or confused by aphostrophes
        #seed = re.split('\" |\"|\” |\”|\“ |\“|\” |\”|\“ |\“|\*|\n', intext)
        #print("seed: ", seed)
        seed = re.split('\" |\"|\” |\”|\“ |\“|\” |\”|\“ |\“|\*|\n', intext)[1:2][0].strip().lower()+" "
    except:
        seed = " "

    paper_title = generate_title(training_titles, seed_text=seed)
    tweet_text = "Congratulations! Your paper " + "\""+paper_title.strip()+ "\"" + " has been accepted to the Journal of AstRobotomy."
    tweet_short = "Congrats! Your paper " + "\""+paper_title.strip()+ "\"" + " has been accepted."

    message="@"+screen_name+" "+tweet_text
    if len(message) > 280: # character count too long for twitter! use abbrev. form
        message="@"+screen_name+" "+tweet_short

    print("aaaand tweet")
    try:
        api.update_status(status=message, in_reply_to_status_id=id)
    except tweepy.error.TweepError as e:
        print("Problem: ")
        print(e.reason)
        print("fail")

if __name__ == "__main__":

    # Routine to randomly tweeet a paper title, unprompted. 
    # load in training titles to check originality
    training = open("./training_titles.txt", "r")
    training_titles = []
    for line in training:
        training_titles.append(line.strip())

    while True:
        INTERVAL = 60.0*6.0*randint(10, 60) # between 1 and 6 hours

        paper_title = generate_title(training_titles)
        tweet_text = "Published on AstRobot-Ph today: " + "\""+paper_title.strip()+ "\"" + "."

        print("Tweet: ", tweet_text)
        tweet(tweet_text)

        time.sleep(INTERVAL)
