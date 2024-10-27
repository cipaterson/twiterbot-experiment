#!/usr/bin/env python3

from requests_oauthlib import OAuth1Session
import requests
import os
import sys
import json
import time
from datetime import datetime
import time
import random
import argparse

# Globals
args = None
tweet_index=0
# mentioned_us = {}   # Record users who mentioned us and how often

# Debug function: print a debug message if verbosity is set high enough
def dprint(level, *str):
    if args.verbose >= level:
        print(" ".join(str))

# The main act.  Handle arguments, initialize, and loop looking for mentions
def main():
    parser = argparse.ArgumentParser(
        description='Poll for mentions, reply with a tweet for each mention')
    parser.add_argument('-m', '--mention', default="14621982",  # Default @zzyplza

                        help='Mentioned Twitter ID to look for.')
    parser.add_argument('-v', '--verbose', help='Be more verbose, can be used several times, e.g. -vvv',
                        action="count", default=0)
    parser.add_argument('-t', '--test', help='Don\'t make any changes - i.e. Don\'t reply with a tweet',
                        action="store_true")
    parser.add_argument('-e', '--env',
                        help='Read our environment from .env, otherwise expect it from the parent process.',
                        action="store_true")

    global args
    args = parser.parse_args()

    # If --env, then read .env into our environment, otherwise parent environment will hold configuration
    if args.env:
        from dotenv import load_dotenv
        load_dotenv()

    if os.environ.get("CONSUMER_KEY") is None:
        print("ERROR: These environment vars need to exist: CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN", file=sys.stderr)
        parser.print_help()
        exit(1)

    # Create the oauth session
    oauth = OAuth1Session(
        # Twitter API dev account key and secret
        # for access to the API product with any restrictions that apply to your purchased plan
        os.environ.get("CONSUMER_KEY"),
        client_secret=os.environ.get("CONSUMER_SECRET"),
        # Tokens to allow actions on behalf of a real Twitter user
        resource_owner_key=os.environ.get("ACCESS_TOKEN"),
        resource_owner_secret=os.environ.get("ACCESS_TOKEN_SECRET")
    )

    twitter_id = args.mention
    dprint(1, f'Looking for mentions of this Twitter user: {twitter_id}')

    # Initial call to find the last tweet we are mentioned in
    (count, newest_id, tweets, users) = get_mentions(bearer_oauth, twitter_id, 0)

    # Loop, when we see some tweets mentioning us, then reply with a tweet
    while True:
        # Go ask twitter API for mentions of twitter_id since newest_id
        (count, newest_id, tweets, users) = get_mentions(bearer_oauth, twitter_id, newest_id)

        if count > 0:
            for tweet in tweets:
                # if tweet.get("referenced_tweets") is not None:
                #     # There may be a better way to do this -
                #     dprint(3, "Mention was found in a reply, ignoring in case we cause an infinite regression")
                #     continue
                dprint(3, f'{tweet["author_id"]=}')
                user = next(u for u in users if u["id"] == tweet["author_id"])
                dprint(2, f'{user["username"]=}')
                # dprint(2, f'{tweet["text"]}')
                dprint(2, f'{tweet=}')
                dprint(2, '---------------')
                if len(tweet["edit_history_tweet_ids"]) > 1:
                    dprint(0, f'{tweet["id"]}: More than one edit_history_tweet_ids!')
                if tweet.get("referenced_tweets") is None:
                  dprint(0, f'{tweet["id"]}: None referenced_tweets!')
                else:
                  if len(tweet["referenced_tweets"]) > 1:
                      dprint(0, f'{tweet["id"]}: More than one referenced tweet!')
                  for r in tweet["referenced_tweets"]:
                      if r["type"] != 'replied_to':
                          dprint(0, f'{tweet["id"]}: Type not replied to!: {r["type"]}')

                reply_to_tweet(oauth, tweet, users)

        time.sleep(60)


# Specialized authentication function - requests.get needs this to do bearer token auth
def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f'Bearer {os.environ.get("BEARER_TOKEN")}'
    # r.headers["User-Agent"] = "v2UserMentionsPython"
    return r

# Poll for any mentions of us and return them
# This uses "app auth" because our plan gives us 15 requests per 15 minutes - it uses a bearer token
def get_mentions(bearer_oauth, twitter_id, newest_id):
    # Tweet fields returned from mention timeline are adjustable.
    tweet_fields = "created_at,id,author_id,text,referenced_tweets"
    params = {
        "tweet.fields": tweet_fields,
        "max_results": 100,
        "expansions": "author_id",  # Adds an "includes" object to the response
        "since_id": newest_id,
    }
    # Special case: find the last mention by requesting a small number of tweets
    if newest_id ==0:
        params["max_results"] = 5

    dprint(1,f"Looking for mentions since {newest_id}, {time.asctime()}")
    url = f"https://api.twitter.com/2/users/{twitter_id}/mentions"
    response = requests.get(url, auth=bearer_oauth, params=params)
    # response = oauth.get(url, params=params)

    dprint(3, f'{response.headers["x-rate-limit-limit"]=}')
    rate_limit_remaining = int(response.headers["x-rate-limit-remaining"])
    seconds_to_go = int(response.headers["x-rate-limit-reset"])-int(time.time())
    dprint(2, f'{rate_limit_remaining} requests left with {seconds_to_go} seconds to go')
    if response.status_code == 429:
        dprint(2, "error: {} {}".format(response.status_code, response.text))
        return 0, newest_id, None, None
    elif response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    json_response = response.json()
    dprint(3, json.dumps(json_response, indent=4, sort_keys=True))

    meta = json_response["meta"]
    dprint(2, f'{meta=}')
    if meta["result_count"] == 0:
        return meta["result_count"], newest_id, None, None
    else:
        return meta["result_count"], meta["newest_id"], json_response["data"], json_response["includes"]["users"]

# Return the tweet text to reply with, cycle through several versions because X get's unhappy with identical tweets
# (Note we do add in a mention of the author we are replying to which may make each tweet unique)
def get_tweet_text():
    global tweet_index
    # Replace the text here with the text you wish to Tweet.
    theMessages = [
        'Need help? ',
        'We DO NOT use Gmail or web forms. ',
        'NEVER share your Secret Recovery Phrase ',
        'We never DM ',
        'We will never DM you,',
    ]
    tweet_text = theMessages[tweet_index]
    tweet_index += 1
    if tweet_index >= len(theMessages)-1:
        tweet_index = 0
    # tweet_text = "Hello world!"  # TEST tweet text
    return tweet_text

# Reply to a tweet with some canned text
# This must use "user auth" because we are acting on behalf of a user when we tweet
# We get 10 requests per 15 minutes on this channel
def reply_to_tweet(oauth, tweet, users):
    tweet_text = get_tweet_text()

    payload = {"text": tweet_text, "reply": {"in_reply_to_tweet_id": ""}}
    # dprint(3, f'{tweet["author_id"]=}')
    # user = next(u for u in users if u["id"] == tweet["author_id"])
    # dprint(2, f'{user["username"]=}')
    # # dprint(2, f'{tweet["text"]}')
    # dprint(2, f'{tweet=}')
    # dprint(2, '---------------')
    # payload["text"] = f'@{user["username"]} {tweet_text}'   ## pre-pend the id we're replying to
    payload["text"] = tweet_text
    payload["reply"]["in_reply_to_tweet_id"] = tweet["id"]
    dprint(3, f'{payload=}')
    dprint(3, f'{len(payload["text"])=}')

    # Don't reply if in test mode, --test on the command line
    if not args.test:
        # Reply to the mention
        response = oauth.post("https://api.twitter.com/2/tweets", json=payload)
        # dprint(3, f'{response.headers=}')
        for h in response.headers:
            if "limit" in h:
                dprint(3, f'{h}: {response.headers[h]}')
        json_response = response.json()
        dprint(3, json.dumps(json_response, indent=4, sort_keys=True))
        dprint(3, f'{response.headers["x-rate-limit-limit"]=}')
        rate_limit_remaining = int(response.headers["x-rate-limit-remaining"])
        seconds_to_go = int(response.headers["x-rate-limit-reset"])-int(time.time())
        dprint(2, f'{rate_limit_remaining} requests left with {seconds_to_go} seconds to go')
        if response.status_code == 200:
            dprint(1, f'Replied with: {response.data.id}')
        elif response.status_code == 429:
            dprint(2, "error: {} {}".format(response.status_code, response.text))
            return
        elif response.status_code != 201:
            raise Exception(
                "Request returned an error: {} {}".format(response.status_code, response.text)
            )
        # dprint(3, "Response code: {}".format(response.status_code))


if __name__ == '__main__':
    main()
