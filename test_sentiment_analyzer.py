import unittest
import pandas as pd
from sentiment_analyzer import SentimentAnalyzer

class TestSentimentAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = SentimentAnalyzer()

    def test_analyze_positive_sentiment(self):
        test_data = [
            {"id": "1", "type": "post", "text": "I love Python, it's the best language!", "subreddit": "python", "created": "", "url": ""}
        ]
        results = self.analyzer.analyze(test_data)
        self.assertEqual(len(results), 1)
        self.assertGreater(results[0]["vader_pos"], 0)
        self.assertGreater(results[0]["textblob_polarity"], 0)
        self.assertGreater(results[0]["combined_compound"], 0)
        self.assertGreater(results[0]["confidence"], 0)

    def test_analyze_negative_sentiment(self):
        test_data = [
            {"id": "1", "type": "comment", "text": "I hate bugs, they are so annoying.", "subreddit": "programming", "created": "", "url": ""}
        ]
        results = self.analyzer.analyze(test_data)
        self.assertEqual(len(results), 1)
        self.assertGreater(results[0]["vader_neg"], 0)
        self.assertLess(results[0]["textblob_polarity"], 0)
        self.assertLess(results[0]["combined_compound"], 0)
        self.assertGreater(results[0]["confidence"], 0) # Confidence should be positive regardless of sentiment

    def test_analyze_neutral_sentiment(self):
        test_data = [
            {"id": "1", "type": "post", "text": "The sky is blue.", "subreddit": "nature", "created": "", "url": ""}
        ]
        results = self.analyzer.analyze(test_data)
        self.assertEqual(len(results), 1)
        self.assertAlmostEqual(results[0]["vader_neu"], 1.0, delta=0.1)
        self.assertAlmostEqual(results[0]["textblob_polarity"], 0.0, delta=0.1)
        self.assertAlmostEqual(results[0]["combined_compound"], 0.0, delta=0.1)

    def test_analyze_empty_text(self):
        test_data = [
            {"id": "1", "type": "post", "text": "", "subreddit": "misc", "created": "", "url": ""}
        ]
        results = self.analyzer.analyze(test_data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["vader_neg"], 0)
        self.assertEqual(results[0]["vader_neu"], 0)
        self.assertEqual(results[0]["vader_pos"], 0)
        self.assertEqual(results[0]["vader_compound"], 0)
        self.assertEqual(results[0]["textblob_polarity"], 0)
        self.assertEqual(results[0]["textblob_subjectivity"], 0)
        self.assertEqual(results[0]["combined_compound"], 0)
        self.assertEqual(results[0]["confidence"], 0)

if __name__ == "__main__":
    unittest.main()


