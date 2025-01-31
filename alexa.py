from flask import Flask
from flask_ask import Ask, statement, question, session

import json
import requests
import time
import unidecode
import logging


app = Flask(__name__)
ask = Ask(app, "/reddit_reader")


def get_headlines(subreddit = 'worldnews'):
    logging.info("Searching for subreddit %s" % subreddit)
    user_pass_dict = {'user': 'username',
                      'passwd': 'password!',
                      'api_type': 'json'}
    sess = requests.session()
    sess.headers.update({'User-Agent': 'I am testing Alexa: MJG'})
    sess.post('https://www.reddit.com/api/login', data=user_pass_dict)
    time.sleep(1)
    url = 'https://www.reddit.com//r/%s/.json?limit=10' % subreddit
    html = sess.get(url)
    data = json.loads(html.content.decode('utf-8'))
    if data['data']['children']:
        titles = [unidecode.unidecode(listing['data']['title']) for listing in data['data']['children']]
        titles = '... '.join([i for i in titles])
        return "The current %s headlines are {}".format(titles) % subreddit
    else:
        return "I was unable to find the %s subreddit" % subreddit


@ask.launch
def start_skill():
    welcome_message = "Hello there, would you like the world news?"
    return question(welcome_message)


@ask.intent("CustomRedditIntent", mapping={'subreddit':'subreddit'})
def get_subreddit_headlines(subreddit):
    return statement(get_headlines(subreddit.replace(" ", "")))


@ask.intent("YesIntent")
def share_headlines():
    headlines = get_headlines()
    headline_msg = "The current world news headlines are {}".format(headlines)
    return statement(headline_msg)


@ask.intent("NoIntent")
def no_intent():
    bye_text = "I am not sure why you even asked me to speak..."
    return statement(bye_text)


if __name__ == '__main__':
    app.run(debug=True)
