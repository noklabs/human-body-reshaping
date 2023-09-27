import json
import os
import praw
import requests
import shutil
import sys
import time

from fake_useragent import UserAgent
from tinydb import TinyDB, Query


def get_reddit(reddit_config):
    reddit = praw.Reddit(
        client_id=reddit_config['client_id'],
        client_secret=reddit_config['client_secret'],
        user_agent=reddit_config['user_agent']
    )
    return reddit


def get_image_url(submission_url):
    if submission_url.endswith('.jpg') or submission_url.endswith('.jpeg') or submission_url.endswith('.png'):
        return submission_url
    elif 'imgur' in submission_url:
        return 'https://i.imgur.com/%s.jpeg' % (submission_url.split('/')[-1])  # It does not matter if you use .png or .jpeg, Imgur will return the image
    else:
        return None


def crawl_posts(reddit_config, crawler_config):
    database = TinyDB(crawler_config['database_path'])
    reddit = get_reddit(reddit_config)
    for subreddit_name in crawler_config['subreddits']:
        subreddit = reddit.subreddit(subreddit_name)
        scrape_time = time.time()
        for submission_index, submission in enumerate(subreddit.top(time_filter='all', limit=crawler_config['limit'])):
            sys.stdout.write('\r[%d/~%d]' % (submission_index + 1, crawler_config['limit']))
            sys.stdout.flush()
            assert submission.created == submission.created_utc
            image_url = get_image_url(submission.url)
            if not submission.is_robot_indexable or submission.is_video or not image_url:
                continue
            database.insert({
                'scrape_time': scrape_time,
                'title': submission.title,
                'text': submission.selftext,
                'score': submission.score,
                'reddit_id': submission.id,
                'image_url': image_url,
                'upvote_count': submission.ups,
                'downvote_count': submission.downs,
                'upvote_ratio': submission.upvote_ratio,
                'subreddit_name': subreddit_name,
                'subreddit_id': submission.subreddit_id,
                'subreddit_subscribers': submission.subreddit_subscribers,
                'creation_unix_epoch': submission.created,
                'edit_unix_epoch': submission.edited,
                'total_awards_received': submission.total_awards_received,
                'comments_count': submission.num_comments,
                'post_permalink': submission.permalink,
                'gilded': submission.gilded,
                'not_safe_for_work': submission.over_18
            })
        print()  # newline


def crawl_images(crawler_config):
    image_dir = crawler_config['image_dir']
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    database = TinyDB(crawler_config['database_path'])
    query = Query()
    user_agent = UserAgent()
    for i, item in enumerate(database):
        sys.stdout.write('\r[%d/%d]' % (i + 1, len(database)))
        sys.stdout.flush()
        output_path = os.path.join(image_dir, item['image_url'].split('/')[-1])
        if not os.path.exists(output_path):
            with requests.get(item['image_url'], headers={'User-agent': user_agent.random, 'Connection': 'close'}, stream=True) as response:
                if response.status_code == 200:
                    with open(output_path, 'wb') as output_file:
                        shutil.copyfileobj(response.raw, output_file)
                else:
                    print(response.status_code, item['image_url'])  # TODO remove
            time.sleep(1)
    print()  # newline


def main(reddit_config, crawler_config):
    #crawl_posts(reddit_config, crawler_config)  # TODO uncomment
    crawl_images(crawler_config)


if __name__ == '__main__':
    with open('praw_config.json') as praw_config_file:
        reddit_config = json.loads(praw_config_file.read())
    with open('crawler_config.json') as crawler_config_file:
        crawler_config = json.loads(crawler_config_file.read())
    main(reddit_config, crawler_config)
