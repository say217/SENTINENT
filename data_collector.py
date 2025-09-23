import praw
import pandas as pd
import nltk
from datetime import datetime
import uuid
import os
import logging
import praw
from datetime import datetime
import uuid

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class RedditDataCollector:
    def __init__(self, client_id, client_secret, user_agent, username, password):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            username=username,
            password=password
        )

    def _clean_text(self, text):
        # Remove newlines, extra spaces, and handle encoding errors
        if not isinstance(text, str):
            return ""
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
        text = text.replace("\n", " ").strip()
        text = " ".join(text.split())
        return text

    def collect_data(self, topic, subreddit_name="all", post_limit=10, comment_limit=10):
        posts_data = []
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            for submission in subreddit.search(topic, limit=post_limit):
                post_id = str(uuid.uuid4())
                post_text = submission.title + " " + (submission.selftext if submission.selftext else "")
                posts_data.append({
                    'id': post_id,
                    'type': 'post',
                    'text': self._clean_text(post_text),
                    'created': datetime.fromtimestamp(submission.created_utc),
                    'subreddit': submission.subreddit.display_name,
                    'url': submission.url
                })

                submission.comments.replace_more(limit=0)
                for comment in submission.comments.list()[:comment_limit]:
                    posts_data.append({
                        'id': str(uuid.uuid4()),
                        'type': 'comment',
                        'text': self._clean_text(comment.body),
                        'created': datetime.fromtimestamp(comment.created_utc),
                        'subreddit': comment.subreddit.display_name,
                        'url': submission.url
                    })
        except Exception as e:
            logging.error(f"Error collecting data for topic '{topic}': {e}")
            return []
        return posts_data

if __name__ == "__main__":
    # This block is for testing purposes
    from dotenv import load_dotenv
    load_dotenv()

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")

    if not all([client_id, client_secret, user_agent, username, password]):
        logging.error("Missing Reddit API credentials in .env file.")
    else:
        collector = RedditDataCollector(client_id, client_secret, user_agent, username, password)
        test_topic = "Python Programming"
        data = collector.collect_data(test_topic, post_limit=2, comment_limit=2)
        if data:
            logging.info(f"Successfully collected {len(data)} items for '{test_topic}'.")
            for item in data[:5]:  # Print first 5 items for verification
                logging.info(item)
        else:
            logging.info(f"No data collected for '{test_topic}'.")