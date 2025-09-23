import unittest
import pandas as pd
import os
from visualization_generator import VisualizationGenerator

class TestVisualizationGenerator(unittest.TestCase):

    def setUp(self):
        self.viz_gen = VisualizationGenerator()
        self.test_df = pd.DataFrame([
            {"id": "1", "type": "post", "text": "Python is great for data analysis and machine learning.", "created": "2023-01-01", "subreddit": "python", "url": "", "vader_neg": 0.0, "vader_neu": 0.4, "vader_pos": 0.6, "vader_compound": 0.8, "textblob_polarity": 0.7, "combined_compound": 0.75},
            {"id": "2", "type": "comment", "text": "I love using pandas for data manipulation.", "created": "2023-01-01", "subreddit": "python", "url": "", "vader_neg": 0.0, "vader_neu": 0.3, "vader_pos": 0.7, "vader_compound": 0.7, "textblob_polarity": 0.8, "combined_compound": 0.75},
            {"id": "3", "type": "post", "text": "Learning new programming languages can be challenging.", "created": "2023-01-02", "subreddit": "programming", "url": "", "vader_neg": 0.0, "vader_neu": 1.0, "vader_pos": 0.0, "vader_compound": 0.0, "textblob_polarity": 0.1, "combined_compound": 0.05},
            {"id": "4", "type": "comment", "text": "This library has some serious bugs.", "created": "2023-01-02", "subreddit": "software", "url": "", "vader_neg": 0.6, "vader_neu": 0.4, "vader_pos": 0.0, "vader_compound": -0.6, "textblob_polarity": -0.5, "combined_compound": -0.55},
            {"id": "5", "type": "post", "text": "Excited about the new AI advancements!", "created": "2023-01-03", "subreddit": "AI", "url": "", "vader_neg": 0.0, "vader_neu": 0.3, "vader_pos": 0.7, "vader_compound": 0.9, "textblob_polarity": 0.8, "combined_compound": 0.85},
        ])
        self.output_dir = "./test_output"
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        # Clean up generated files
        for f in os.listdir(self.output_dir):
            os.remove(os.path.join(self.output_dir, f))
        os.rmdir(self.output_dir)

    def test_plot_sentiment_analysis(self):
        topic = "TestTopic"
        filename = self.viz_gen.plot_sentiment_analysis(self.test_df, topic)
        self.assertTrue(os.path.exists(filename))
        self.assertTrue(filename.endswith("_sentiment_plots.png"))

    def test_generate_wordcloud(self):
        topic = "TestTopic"
        text_data = self.test_df["text"].tolist()
        filename = self.viz_gen.generate_wordcloud(text_data, topic, output_path=self.output_dir)
        self.assertTrue(os.path.exists(filename))
        self.assertTrue(filename.endswith("_wordcloud.png"))

if __name__ == "__main__":
    unittest.main()




    def test_plot_sentiment_counts(self):
        topic = "TestTopic"
        filename = self.viz_gen.plot_sentiment_counts(self.test_df, topic, output_path=self.output_dir)
        self.assertTrue(os.path.exists(filename))
        self.assertTrue(filename.endswith("_sentiment_counts.png"))

