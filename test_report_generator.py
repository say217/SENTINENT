import unittest
import pandas as pd
import os
from report_generator import ReportGenerator

class TestReportGenerator(unittest.TestCase):

    def setUp(self):
        self.output_dir = "./test_reports"
        os.makedirs(self.output_dir, exist_ok=True)
        self.reporter = ReportGenerator(output_dir=self.output_dir)
        self.test_df = pd.DataFrame([
            {"id": "1", "type": "post", "text": "Python is great for data analysis and machine learning.", "created": "2023-01-01", "subreddit": "python", "url": "", "vader_neg": 0.0, "vader_neu": 0.4, "vader_pos": 0.6, "vader_compound": 0.8, "textblob_polarity": 0.7, "combined_compound": 0.75},
            {"id": "2", "type": "comment", "text": "I love using pandas for data manipulation.", "created": "2023-01-01", "subreddit": "python", "url": "", "vader_neg": 0.0, "vader_neu": 0.3, "vader_pos": 0.7, "vader_compound": 0.7, "textblob_polarity": 0.8, "combined_compound": 0.75},
            {"id": "3", "type": "post", "text": "Learning new programming languages can be challenging.", "created": "2023-01-02", "subreddit": "programming", "url": "", "vader_neg": 0.0, "vader_neu": 1.0, "vader_pos": 0.0, "vader_compound": 0.0, "textblob_polarity": 0.1, "combined_compound": 0.05},
            {"id": "4", "type": "comment", "text": "This library has some serious bugs.", "created": "2023-01-02", "subreddit": "software", "url": "", "vader_neg": 0.6, "vader_neu": 0.4, "vader_pos": 0.0, "vader_compound": -0.6, "textblob_polarity": -0.5, "combined_compound": -0.55},
            {"id": "5", "type": "post", "text": "Excited about the new AI advancements!", "created": "2023-01-03", "subreddit": "AI", "url": "", "vader_neg": 0.0, "vader_neu": 0.3, "vader_pos": 0.7, "vader_compound": 0.9, "textblob_polarity": 0.8, "combined_compound": 0.85},
        ])
        # Create dummy image files for testing
        self.dummy_plot_path = os.path.join(self.output_dir, "dummy_plot.png")
        self.dummy_wordcloud_path = os.path.join(self.output_dir, "dummy_wordcloud.png")
        self.dummy_sentiment_counts_path = os.path.join(self.output_dir, "dummy_sentiment_counts.png")
        with open(self.dummy_plot_path, "w") as f:
            f.write("dummy content")
        with open(self.dummy_wordcloud_path, "w") as f:
            f.write("dummy content")
        with open(self.dummy_sentiment_counts_path, "w") as f:
            f.write("dummy content")

    def tearDown(self):
        # Clean up generated files and directory
        for f in os.listdir(self.output_dir):
            os.remove(os.path.join(self.output_dir, f))
        os.rmdir(self.output_dir)

    def test_generate_summary_report(self):
        topic = "Test Report"
        report_file = self.reporter.generate_summary_report(
            self.test_df, topic, self.dummy_plot_path, self.dummy_wordcloud_path, self.dummy_sentiment_counts_path
        )
        self.assertTrue(os.path.exists(report_file))
        self.assertTrue(report_file.endswith("_sentiment_report.md"))

if __name__ == "__main__":
    unittest.main()
