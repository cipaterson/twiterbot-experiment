#!/usr/bin/env python3

from requests_oauthlib import OAuth1Session
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

# Twitter API dev account key and secret
# for access to the API product with any restrictions that apply to your purchased plan
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")

bearer_token = os.environ.get("BEARER_TOKEN")
## NOTE OAuth1Session can't take a bearer_token, it's not an oauth technique

access_token = "14621982-5eVLsUx6noFggMHzOUP8IIM8pr6T2TDPmOnTERVsD"
access_token_secret = "J6XJJ93OIfi0cZH1qBzCfa10V33bmKaT7mSGxbmpvuoTx"

auth_needed = True
if auth_needed:
  # Get request token
  request_token_url = "https://api.twitter.com/oauth/request_token"
  oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

  try:
      fetch_response = oauth.fetch_request_token(request_token_url)
  except ValueError:
      print(
          "There may have been an issue with the consumer_key or consumer_secret you entered."
      )

  resource_owner_key = fetch_response.get("oauth_token")
  resource_owner_secret = fetch_response.get("oauth_token_secret")
  print("Got OAuth token: %s" % resource_owner_key)

  # # Get authorization
  base_authorization_url = "https://api.twitter.com/oauth/authorize"
  authorization_url = oauth.authorization_url(base_authorization_url)
  print("Please go here and authorize: %s" % authorization_url)
  verifier = input("Paste the PIN here: ")

  # Get the access token
  access_token_url = "https://api.twitter.com/oauth/access_token"
  oauth = OAuth1Session(
      consumer_key,
      client_secret=consumer_secret,
      resource_owner_key=resource_owner_key,
      resource_owner_secret=resource_owner_secret,
      verifier=verifier,
  )
  oauth_tokens = oauth.fetch_access_token(access_token_url)
  print(oauth_tokens)

  access_token = oauth_tokens["oauth_token"]
  access_token_secret = oauth_tokens["oauth_token_secret"]

  print(f'{access_token=}')
  print(f'{access_token_secret=}')
