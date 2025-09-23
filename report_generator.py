import pandas as pd
import os
import requests
from urllib.parse import quote

class ReportGenerator:
    def __init__(self, output_dir="."):
        self.output_dir = output_dir

    def search_and_download_image(self, topic):
        """Search for an image related to the topic using Google Custom Search API"""
        try:
            # This is a placeholder for image search functionality
            # In a real implementation, you would use Google Custom Search API
            # For now, we'll return None and handle it gracefully
            return None
        except Exception as e:
            print(f"Error searching for image: {e}")
            return None

    def calculate_sentiment_statistics(self, df):
        """Calculate detailed positive and negative sentiment statistics"""
        def categorize_sentiment(score):
            if score >= 0.05:
                return "Positive"
            elif score <= -0.05:
                return "Negative"
            else:
                return "Neutral"

        df["sentiment_category"] = df["combined_compound"].apply(categorize_sentiment)
        
        total_count = len(df)
        positive_count = len(df[df["sentiment_category"] == "Positive"])
        negative_count = len(df[df["sentiment_category"] == "Negative"])
        neutral_count = len(df[df["sentiment_category"] == "Neutral"])
        
        positive_percentage = (positive_count / total_count) * 100
        negative_percentage = (negative_count / total_count) * 100
        neutral_percentage = (neutral_count / total_count) * 100
        
        avg_positive_score = df[df["sentiment_category"] == "Positive"]["combined_compound"].mean() if positive_count > 0 else 0
        avg_negative_score = df[df["sentiment_category"] == "Negative"]["combined_compound"].mean() if negative_count > 0 else 0
        avg_neutral_score = df[df["sentiment_category"] == "Neutral"]["combined_compound"].mean() if neutral_count > 0 else 0
        
        return {
            "total_count": total_count,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "positive_percentage": positive_percentage,
            "negative_percentage": negative_percentage,
            "neutral_percentage": neutral_percentage,
            "avg_positive_score": avg_positive_score,
            "avg_negative_score": avg_negative_score,
            "avg_neutral_score": avg_neutral_score
        }

    def generate_summary_report(self, df, topic, plot_path, wordcloud_path, sentiment_counts_path, heatmap_path=None, pie_path=None, topic_image_path=None):
        # Clean text column to ensure UTF-8 compatibility
        df['text'] = df['text'].apply(lambda x: x.encode('utf-8', errors='ignore').decode('utf-8') if isinstance(x, str) else x)
        
        # Calculate detailed sentiment statistics
        sentiment_stats = self.calculate_sentiment_statistics(df)
        
        report_content = f"# Comprehensive Sentiment Analysis Report for {topic}\n\n"
        
        # Add topic-related image if available
        if topic_image_path and os.path.exists(topic_image_path):
            report_content += f"![Topic Image]({os.path.basename(topic_image_path)})\n\n"
        
        report_content += "## Executive Summary\n\n"
        report_content += f"This comprehensive sentiment analysis report examines {sentiment_stats['total_count']} pieces of content related to '{topic}'. "
        report_content += f"The analysis reveals that {sentiment_stats['positive_percentage']:.1f}% of the content expresses positive sentiment, "
        report_content += f"{sentiment_stats['negative_percentage']:.1f}% expresses negative sentiment, and {sentiment_stats['neutral_percentage']:.1f}% is neutral.\n\n"
        
        report_content += "## 1. Detailed Sentiment Statistics\n\n"
        
        report_content += "### 1.1 Overall Distribution\n\n"
        report_content += f"- **Total Content Analyzed**: {sentiment_stats['total_count']} items\n"
        report_content += f"- **Positive Content**: {sentiment_stats['positive_count']} items ({sentiment_stats['positive_percentage']:.1f}%)\n"
        report_content += f"- **Negative Content**: {sentiment_stats['negative_count']} items ({sentiment_stats['negative_percentage']:.1f}%)\n"
        report_content += f"- **Neutral Content**: {sentiment_stats['neutral_count']} items ({sentiment_stats['neutral_percentage']:.1f}%)\n\n"
        
        report_content += "### 1.2 Average Sentiment Scores\n\n"
        report_content += f"- **Average Positive Score**: {sentiment_stats['avg_positive_score']:.3f}\n"
        report_content += f"- **Average Negative Score**: {sentiment_stats['avg_negative_score']:.3f}\n"
        report_content += f"- **Average Neutral Score**: {sentiment_stats['avg_neutral_score']:.3f}\n\n"
        
        report_content += "### 1.3 Statistical Summary of All Sentiment Metrics\n\n"
        stats = df[["vader_neg", "vader_neu", "vader_pos", "vader_compound", "textblob_polarity", "combined_compound"]].describe().to_markdown()
        report_content += f"{stats}\n\n"

        # Interpretation of statistics
        report_content += "### 1.4 Statistical Interpretation\n\n"
        overall_sentiment = df["combined_compound"].mean()
        if overall_sentiment > 0.1:
            sentiment_interpretation = "predominantly positive"
        elif overall_sentiment < -0.1:
            sentiment_interpretation = "predominantly negative"
        else:
            sentiment_interpretation = "generally neutral"
        
        report_content += f"The overall sentiment towards '{topic}' is **{sentiment_interpretation}** with an average combined compound score of {overall_sentiment:.3f}. "
        
        sentiment_variance = df["combined_compound"].var()
        if sentiment_variance > 0.3:
            report_content += f"The high variance ({sentiment_variance:.3f}) indicates diverse opinions and polarized views on this topic.\n\n"
        elif sentiment_variance < 0.1:
            report_content += f"The low variance ({sentiment_variance:.3f}) suggests relatively consistent sentiment across the analyzed content.\n\n"
        else:
            report_content += f"The moderate variance ({sentiment_variance:.3f}) indicates a reasonable spread of opinions on this topic.\n\n"

        report_content += "## 2. Content Analysis by Sentiment Category\n\n"

        report_content += "### 2.1 Top 5 Most Positive Content\n\n"
        positive_texts = df.nlargest(5, "combined_compound")[["text", "combined_compound", "type", "subreddit"]].to_markdown(index=False)
        report_content += f"{positive_texts}\n\n"
        
        report_content += "**Analysis**: The most positive content typically features enthusiastic language, success stories, or expressions of satisfaction. "
        report_content += "These posts and comments often use words like 'great', 'love', 'excited', and 'amazing', contributing to their high sentiment scores.\n\n"

        report_content += "### 2.2 Top 5 Most Negative Content\n\n"
        negative_texts = df.nsmallest(5, "combined_compound")[["text", "combined_compound", "type", "subreddit"]].to_markdown(index=False)
        report_content += f"{negative_texts}\n\n"
        
        report_content += "**Analysis**: The most negative content often contains criticism, complaints, or expressions of frustration. "
        report_content += "Common negative indicators include words like 'bugs', 'problems', 'hate', 'terrible', and 'disappointing'.\n\n"

        # Content type analysis
        report_content += "### 2.3 Sentiment by Content Type\n\n"
        type_analysis = df.groupby('type')['combined_compound'].agg(['mean', 'count', 'std']).round(3)
        report_content += type_analysis.to_markdown()
        report_content += "\n\n"
        
        if 'post' in type_analysis.index and 'comment' in type_analysis.index:
            post_sentiment = type_analysis.loc['post', 'mean']
            comment_sentiment = type_analysis.loc['comment', 'mean']
            if post_sentiment > comment_sentiment:
                report_content += "**Observation**: Posts tend to be more positive than comments, which may indicate that original content creators are more optimistic, while commenters provide more critical feedback.\n\n"
            elif comment_sentiment > post_sentiment:
                report_content += "**Observation**: Comments tend to be more positive than posts, suggesting that community engagement often involves supportive responses.\n\n"
            else:
                report_content += "**Observation**: Posts and comments show similar sentiment patterns, indicating consistent community attitudes.\n\n"

        # Subreddit analysis
        report_content += "### 2.4 Sentiment by Community (Subreddit)\n\n"
        subreddit_analysis = df.groupby('subreddit')['combined_compound'].agg(['mean', 'count', 'std']).round(3)
        report_content += subreddit_analysis.to_markdown()
        report_content += "\n\n"
        
        most_positive_subreddit = subreddit_analysis['mean'].idxmax()
        most_negative_subreddit = subreddit_analysis['mean'].idxmin()
        report_content += f"**Key Findings**: The most positive community is r/{most_positive_subreddit} with an average sentiment of {subreddit_analysis.loc[most_positive_subreddit, 'mean']:.3f}, "
        report_content += f"while r/{most_negative_subreddit} shows the most negative sentiment with an average of {subreddit_analysis.loc[most_negative_subreddit, 'mean']:.3f}.\n\n"

        report_content += "## 3. Sentiment Visualizations\n\n"
        
        report_content += "### 3.1 Comprehensive Sentiment Analysis Plots\n\n"
        if plot_path and os.path.exists(plot_path):
            report_content += f"![Sentiment Analysis Plots]({os.path.basename(plot_path)})\n\n"
            report_content += "This comprehensive visualization includes:\n"
            report_content += "- **Distribution of Sentiment Scores**: Shows how sentiment scores are distributed across all content\n"
            report_content += "- **Sentiment by Subreddit**: Compares sentiment patterns across different communities\n"
            report_content += "- **Sentiment Trend Over Time**: Reveals how sentiment changes over time\n"
            report_content += "- **Average Sentiment by Content Type**: Compares posts vs. comments\n\n"
        
        report_content += "### 3.2 Sentiment Distribution Overview\n\n"
        if sentiment_counts_path and os.path.exists(sentiment_counts_path):
            report_content += f"![Sentiment Distribution]({os.path.basename(sentiment_counts_path)})\n\n"
            report_content += "This bar chart provides a clear overview of the proportion of positive, negative, and neutral content.\n\n"
        
        if pie_path and os.path.exists(pie_path):
            report_content += f"![Sentiment Distribution Pie Chart]({os.path.basename(pie_path)})\n\n"
            report_content += "This pie chart offers an alternative view of sentiment distribution with percentage breakdowns.\n\n"
        
        report_content += "### 3.3 Sentiment Metrics Correlation\n\n"
        if heatmap_path and os.path.exists(heatmap_path):
            report_content += f"![Sentiment Correlation Heatmap]({os.path.basename(heatmap_path)})\n\n"
            report_content += "This heatmap shows how different sentiment analysis methods correlate with each other, "
            report_content += "helping to validate the consistency of our sentiment measurements.\n\n"
        
        report_content += "### 3.4 Word Cloud Analysis\n\n"
        if wordcloud_path and os.path.exists(wordcloud_path):
            report_content += f"![Word Cloud]({os.path.basename(wordcloud_path)})\n\n"
            report_content += "The word cloud highlights the most frequently mentioned terms in the analyzed content, "
            report_content += "providing insight into the main topics and themes of discussion.\n\n"

        report_content += "## 4. Key Insights and Recommendations\n\n"
        
        report_content += "### 4.1 Main Findings\n\n"
        if sentiment_stats['positive_percentage'] > 50:
            report_content += f"- **Predominantly Positive Reception**: With {sentiment_stats['positive_percentage']:.1f}% positive content, '{topic}' enjoys favorable community sentiment.\n"
        elif sentiment_stats['negative_percentage'] > 50:
            report_content += f"- **Concerning Negative Sentiment**: {sentiment_stats['negative_percentage']:.1f}% of content expresses negative sentiment, indicating potential issues that need attention.\n"
        else:
            report_content += f"- **Mixed Reception**: The sentiment is fairly balanced with {sentiment_stats['positive_percentage']:.1f}% positive and {sentiment_stats['negative_percentage']:.1f}% negative content.\n"
        
        report_content += f"- **Community Engagement**: Analysis of {sentiment_stats['total_count']} pieces of content across multiple communities provides a comprehensive view.\n"
        report_content += f"- **Sentiment Intensity**: The average sentiment scores indicate {'strong' if abs(overall_sentiment) > 0.3 else 'moderate'} emotional responses to the topic.\n\n"
        
        report_content += "### 4.2 Recommendations\n\n"
        if sentiment_stats['negative_percentage'] > 30:
            report_content += "- **Address Negative Feedback**: Consider investigating and addressing the concerns raised in negative content.\n"
        if sentiment_stats['positive_percentage'] > 60:
            report_content += "- **Leverage Positive Sentiment**: Build on the positive reception by amplifying successful aspects.\n"
        report_content += "- **Monitor Trends**: Continue tracking sentiment over time to identify emerging patterns.\n"
        report_content += "- **Community-Specific Strategies**: Tailor approaches based on the sentiment patterns observed in different communities.\n\n"

        report_content += "---\n\n"
        report_content += f"*Report generated using advanced sentiment analysis techniques combining VADER and TextBlob methodologies. Analysis based on {sentiment_stats['total_count']} content items.*\n"

        report_filename_md = os.path.join(self.output_dir, f"{topic.replace(' ', '_')}_sentiment_report.md")
        with open(report_filename_md, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"Enhanced report saved as '{report_filename_md}'")
        return report_filename_md

if __name__ == "__main__":
    # Example Usage
    data = [
        {"id": "1", "type": "post", "text": "Python is great for data analysis and machine learning.", "created": "2023-01-01", "subreddit": "python", "url": "", "vader_neg": 0.0, "vader_neu": 0.4, "vader_pos": 0.6, "vader_compound": 0.8, "textblob_polarity": 0.7, "combined_compound": 0.75},
        {"id": "2", "type": "comment", "text": "I love using pandas for data manipulation.", "created": "2023-01-01", "subreddit": "python", "url": "", "vader_neg": 0.0, "vader_neu": 0.3, "vader_pos": 0.7, "vader_compound": 0.7, "textblob_polarity": 0.8, "combined_compound": 0.75},
        {"id": "3", "type": "post", "text": "Learning new programming languages can be challenging.", "created": "2023-01-02", "subreddit": "programming", "url": "", "vader_neg": 0.0, "vader_neu": 1.0, "vader_pos": 0.0, "vader_compound": 0.0, "textblob_polarity": 0.1, "combined_compound": 0.05},
        {"id": "4", "type": "comment", "text": "This library has some serious bugs.", "created": "2023-01-02", "subreddit": "software", "url": "", "vader_neg": 0.6, "vader_neu": 0.4, "vader_pos": 0.0, "vader_compound": -0.6, "textblob_polarity": -0.5, "combined_compound": -0.55},
        {"id": "5", "type": "post", "text": "Excited about the new AI advancements!", "created": "2023-01-03", "subreddit": "AI", "url": "", "vader_neg": 0.0, "vader_neu": 0.3, "vader_pos": 0.7, "vader_compound": 0.9, "textblob_polarity": 0.8, "combined_compound": 0.85},
    ]
    df = pd.DataFrame(data)

    # Create dummy image files for testing
    os.makedirs("output", exist_ok=True)
    with open("output/test_plot.png", "w") as f:
        f.write("dummy content")
    with open("output/test_wordcloud.png", "w") as f:
        f.write("dummy content")
    with open("output/test_sentiment_counts.png", "w") as f:
        f.write("dummy content")

    reporter = ReportGenerator(output_dir="output")
    report_file = reporter.generate_summary_report(
        df, 
        "Test Topic", 
        "output/test_plot.png", 
        "output/test_wordcloud.png", 
        "output/test_sentiment_counts.png"
    )
    print(f"Generated report: {report_file}")

    # Clean up dummy files
    os.remove("output/test_plot.png")
    os.remove("output/test_wordcloud.png")
    os.remove("output/test_sentiment_counts.png")
    os.rmdir("output")

