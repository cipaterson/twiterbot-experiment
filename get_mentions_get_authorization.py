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

auth_needed = False #does my app/project need authorization from the owner of the user account?
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

# Make the request
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret,
)

# Tweet fields are adjustable.
# Options include:
# attachments, author_id, context_annotations,
# conversation_id, created_at, entities, geo, id,
# in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
# possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
# source, text, and withheld
fields = "created_at,author_id,text"
params = {
  "tweet.fields": fields,
  "max_results": 10,
  # "since_id": 0,
}

twitter_id = "14621982"  # @zzyplza
##response = oauth.get("https://api.twitter.com/2/users/me") #, params=params)
# response = oauth.get("https://api.twitter.com/2/users/by/username/zzyplza", params=params)
##response = oauth.get("https://api.twitter.com/2/tweets/search/recent", params=params)

newest_id=0
while True:
  params["since_id"] = newest_id
  print("mentions since {}".format(newest_id))
  response = oauth.get(f"https://api.twitter.com/2/users/{twitter_id}/mentions", params=params)

  if response.status_code != 200:
      raise Exception(
          "Request returned an error: {} {}".format(response.status_code, response.text)
      )

  print("Response code: {}".format(response.status_code))

  json_response = response.json()
  print(json.dumps(json_response, indent=4, sort_keys=True))

  meta = json_response["meta"]
  print(meta["result_count"])
  if meta["result_count"] != 0:
    print(meta["newest_id"])
    newest_id=meta["newest_id"]
    for t in json_response["data"]:
        print(t["text"])
    print(meta["oldest_id"])

  time.sleep(60)
