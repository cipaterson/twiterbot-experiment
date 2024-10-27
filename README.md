# Project Title

Tweeter Bot experiments.

## Description

Detect mentions of a user, and reply with a helpful tweet (post?).

get_mentions_engage.py is the main script.  It will determine the latest mention and then enter a loop polling for new ones every 60 seconds.

get_tweet.py is a utility to retrieve information about one tweet ID.

## Getting Started

### Dependencies

Install the packages in requirements.txt

Several environment vars need to be defined to allow authentication against the twitter API.  These can optionally be read from a .env file:
```shell
BEARER_TOKEN=%3DFiIk7W0rM7zyxxxxxxxxxxxxxxxxxxxx00pXBBw9vnqVC
CONSUMER_KEY=O1iRxxxxxxxxxQ54YzK6q
CONSUMER_SECRET=ZfFSHqj1txxxxxxxxQPYQVXxXyCxIN
ACCESS_TOKEN=14621982-xxxxxxxxxnt9SLC8Eio9uqd
ACCESS_TOKEN_SECRET=DN9ZVACCRdxxxxxxxxxxxD2SPDDDPlJ6
```

### Installing

```python
git clone <this repo>
cd twitterbot-experiment
pip -r requirements.txt
```

### Executing program

Start the script, reading required env vars from .env, looking for mentions of the MM Support twitter ID, with a verbosity level of 2, and in "test" mode, i.e. don't actually reply with a tweet:
```
./get_mentions_engage.py -e -m 14621982 -vv -t
```
Start the script, expect Auth variables from the parent environment, listen for "@Metamask_support" ID, with  minimal output:
```
./get_mentions_engage.py --mention 14621982
```

## Help

```
% ./get_mentions_engage.py --help
usage: get_mentions_engage.py [-h] [-m MENTION] [-v] [-t] [-e]

Poll for mentions, reply with a tweet for each mention

options:
  -h, --help            show this help message and exit
  -m MENTION, --mention MENTION
                        Mentioned Twitter ID to look for.
  -v, --verbose         Be more verbose, can be used several times, e.g. -vvv
  -t, --test            Don't make any changes - i.e. Don't reply with a tweet
  -e, --env             Read our environment from .env, otherwise expect it from the parent process.
```

## Authors



## Version History


## License

TBD - choose license.

## Acknowledgments

