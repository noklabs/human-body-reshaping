# Introduction

This code was tested on Ubuntu 22.04.3 with Python 3.11.4.

# Getting Started

1- Log into a Reddit account.

2- Follow [first steps](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps) to get client id and secret.

3- `cp praw_config_template.json praw_config.json`

4- Fill in the client id and secret as well as a user agent such as `testscript by u/username` in `praw_config.json`.

5- `pip install -r requirements.txt`

6- `python3 crawler.py`

# TODO

1- crawl videos (e.g. submission.url is https://v.redd.it/av6196a5tht21). Note that submission.video is not always correct.
