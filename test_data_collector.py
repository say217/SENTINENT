import unittest
from unittest.mock import MagicMock, patch
from data_collector import RedditDataCollector
from datetime import datetime

class TestRedditDataCollector(unittest.TestCase):

    def setUp(self):
        self.mock_reddit = MagicMock()
        self.collector = RedditDataCollector("id", "secret", "agent", "user", "pass")
        self.collector.reddit = self.mock_reddit

    @patch("uuid.uuid4", return_value="mock_uuid")
    def test_collect_data_success(self, mock_uuid):
        # Mock a submission object
        mock_submission = MagicMock()
        mock_submission.title = "Test Post Title"
        mock_submission.selftext = "Test Post Selftext"
        mock_submission.created_utc = datetime.now().timestamp()
        mock_submission.subreddit.display_name = "test_subreddit"
        mock_submission.url = "http://example.com/post"

        # Mock a comment object
        mock_comment = MagicMock()
        mock_comment.body = "Test Comment Body"
        mock_comment.created_utc = datetime.now().timestamp()
        mock_comment.subreddit.display_name = "test_subreddit"

        mock_submission.comments.replace_more.return_value = None
        mock_submission.comments.list.return_value = [mock_comment]

        self.mock_reddit.subreddit.return_value.search.return_value = [mock_submission]

        data = self.collector.collect_data("test_topic", post_limit=1, comment_limit=1)

        self.assertEqual(len(data), 2) # 1 post + 1 comment
        self.assertEqual(data[0]["type"], "post")
        self.assertEqual(data[0]["text"], "Test Post Title Test Post Selftext")
        self.assertEqual(data[1]["type"], "comment")
        self.assertEqual(data[1]["text"], "Test Comment Body")

    def test_collect_data_no_data(self):
        self.mock_reddit.subreddit.return_value.search.return_value = []
        data = self.collector.collect_data("non_existent_topic")
        self.assertEqual(len(data), 0)

    def test_collect_data_exception_handling(self):
        self.mock_reddit.subreddit.return_value.search.side_effect = Exception("API Error")
        data = self.collector.collect_data("test_topic")
        self.assertEqual(len(data), 0)

if __name__ == "__main__":
    unittest.main()


