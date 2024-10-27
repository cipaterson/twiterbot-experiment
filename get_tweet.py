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

# Debug function: print a debug message if verbosity is set high enough
def dprint(level, *str):
    if args.verbose >= level:
        print(" ".join(str))

# The main act.  Handle arguments, initialize, and loop looking for mentions
def main():
    parser = argparse.ArgumentParser(
        description='Get all info for a tweet id')
    parser.add_argument("tweetID", help="Tweet ID to get")
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

    tweet_id = args.tweetID

    # Go ask twitter API for a tweet
    (tweet, users) = get_tweet(bearer_oauth, tweet_id)

    dprint(3, f'{tweet["author_id"]=}')
    user = next(u for u in users if u["id"] == tweet["author_id"])
    dprint(2, f'{user["username"]=}')
    # dprint(2, f'{tweet["text"]}')
    dprint(0, f'{tweet=}')  #xxx
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
def get_tweet(bearer_oauth, tweet_id):
    # Tweet fields returned from mention timeline are adjustable.
    tweet_fields = "created_at,id,author_id,text,referenced_tweets"
    params = {
        "tweet.fields": tweet_fields,
        "expansions": "author_id",  # Adds an "includes" object to the response
    }

    url = f"https://api.twitter.com/2/tweets/{tweet_id}"
    dprint(0, url)
    response = requests.get(url, auth=bearer_oauth, params=params)

    # dprint(3, f'{response.headers["x-rate-limit-limit"]=}')
    # rate_limit_remaining = int(response.headers["x-rate-limit-remaining"])
    # seconds_to_go = int(response.headers["x-rate-limit-reset"])-int(time.time())
    # dprint(2, f'{rate_limit_remaining} requests left with {seconds_to_go} seconds to go')
    if response.status_code == 429:
        dprint(2, "error: {} {}".format(response.status_code, response.text))
        return None, None
    elif response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    json_response = response.json()
    dprint(3, json.dumps(json_response, indent=4, sort_keys=True))
    return json_response["data"], json_response["includes"]["users"]

if __name__ == '__main__':
    main()
