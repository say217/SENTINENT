import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
import pandas as pd

class SentimentAnalyzer:
    def __init__(self):
        nltk.download("vader_lexicon", quiet=True)
        self.sia = SentimentIntensityAnalyzer()

    def analyze(self, data):
        sentiment_results = []
        for item in data:
            text = item.get("text", "")
            if not isinstance(text, str) or not text:
                # Skip empty or non-string text
                continue

            # VADER sentiment analysis
            vader_scores = self.sia.polarity_scores(text)
            # TextBlob sentiment analysis
            textblob_sentiment = TextBlob(text).sentiment

            # Combine scores (simple average for this example)
            combined_compound = (vader_scores["compound"] + textblob_sentiment.polarity) / 2

            sentiment_results.append({
                "id": item["id"],
                "type": item["type"],
                "text": text,
                "subreddit": item["subreddit"],
                "created": item["created"],
                "url": item["url"],
                "vader_neg": vader_scores["neg"],
                "vader_neu": vader_scores["neu"],
                "vader_pos": vader_scores["pos"],
                "vader_compound": vader_scores["compound"],
                "textblob_polarity": textblob_sentiment.polarity,
                "textblob_subjectivity": textblob_sentiment.subjectivity,
                "combined_compound": combined_compound,
                "confidence": abs(combined_compound)  # Use absolute of combined score as confidence
            })
        return sentiment_results

if __name__ == "__main__":
    # This block is for testing purposes
    test_data = [
        {"id": "1", "type": "post", "text": "I love Python, it's the best language!", "subreddit": "python", "created": "", "url": ""},
        {"id": "2", "type": "comment", "text": "I hate bugs, they are so annoying.", "subreddit": "programming", "created": "", "url": ""},
        {"id": "3", "type": "post", "text": None, "subreddit": "test", "created": "", "url": ""}  # Test invalid text
    ]
    analyzer = SentimentAnalyzer()
    results = analyzer.analyze(test_data)
    df = pd.DataFrame(results)
    print(df)
