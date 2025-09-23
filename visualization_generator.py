import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import pandas as pd
import os

class VisualizationGenerator:
    def __init__(self):
        pass

    def plot_sentiment_analysis(self, df, topic, output_path="."):
        """
        Generate individual sentiment analysis plots and save them as separate files.
        Returns a dictionary of filenames for each plot.
        """
        topic_clean = topic.replace(" ", "_")
        plot_filenames = {}

        # Plot 1: Distribution of Compound Sentiment Scores
        plt.figure(figsize=(12, 6))
        sns.histplot(data=df, x='combined_compound', hue='type', multiple='stack', palette='viridis')
        plt.title('Distribution of Combined Sentiment Scores', fontsize=16)
        plt.xlabel('Combined Compound Score', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.legend(title='Content Type')
        filename_dist = f'{output_path}/{topic_clean}_sentiment_distribution.png'
        plt.savefig(filename_dist, dpi=300, bbox_inches='tight')
        plt.close()
        plot_filenames['distribution'] = filename_dist
        print(f"Distribution plot saved as '{filename_dist}'")

        # Plot 2: Sentiment by Subreddit
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=df, x='subreddit', y='combined_compound', hue='type', palette='plasma')
        plt.title('Sentiment Scores by Subreddit', fontsize=16)
        plt.xlabel('Subreddit', fontsize=12)
        plt.ylabel('Combined Compound Score', fontsize=12)
        plt.tick_params(axis='x', rotation=45)
        plt.legend(title='Content Type')
        filename_subreddit = f'{output_path}/{topic_clean}_sentiment_subreddit.png'
        plt.savefig(filename_subreddit, dpi=300, bbox_inches='tight')
        plt.close()
        plot_filenames['subreddit'] = filename_subreddit
        print(f"Subreddit plot saved as '{filename_subreddit}'")

        # Plot 3: Sentiment Trend Over Time
        try:
            df['date'] = pd.to_datetime(df['created'], errors='coerce').dt.date
            plt.figure(figsize=(12, 6))
            sns.lineplot(data=df, x='date', y='combined_compound', hue='type', marker='o', palette='magma')
            plt.title('Sentiment Trend Over Time', fontsize=16)
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Combined Compound Score', fontsize=12)
            plt.tick_params(axis='x', rotation=45)
            plt.legend(title='Content Type')
            plt.grid(True, linestyle='--', alpha=0.6)
            filename_trend = f'{output_path}/{topic_clean}_sentiment_trend.png'
            plt.savefig(filename_trend, dpi=300, bbox_inches='tight')
            plt.close()
            plot_filenames['trend'] = filename_trend
            print(f"Trend plot saved as '{filename_trend}'")
        except Exception as e:
            print(f"Error in plotting sentiment trend: {e}")
            plot_filenames['trend'] = None

        # Plot 4: Sentiment Distribution by Type (Post vs. Comment)
        sentiment_by_type = df.groupby('type')['combined_compound'].mean().reset_index()
        plt.figure(figsize=(8, 6))
        sns.barplot(data=sentiment_by_type, x='type', y='combined_compound', palette='coolwarm')
        plt.title('Average Sentiment by Content Type', fontsize=16)
        plt.xlabel('Content Type', fontsize=12)
        plt.ylabel('Average Combined Compound Score', fontsize=12)
        filename_type = f'{output_path}/{topic_clean}_sentiment_type.png'
        plt.savefig(filename_type, dpi=300, bbox_inches='tight')
        plt.close()
        plot_filenames['type'] = filename_type
        print(f"Type plot saved as '{filename_type}'")

        return plot_filenames

    def plot_sentiment_heatmap(self, df, topic, output_path="."):
        """Generate a heatmap showing sentiment correlation between different metrics"""
        sentiment_cols = ['vader_neg', 'vader_neu', 'vader_pos', 'vader_compound', 'textblob_polarity', 'combined_compound']
        correlation_matrix = df[sentiment_cols].corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='RdBu_r', center=0, 
                   square=True, linewidths=0.5, cbar_kws={"shrink": .8})
        plt.title(f'Sentiment Metrics Correlation Heatmap for {topic}', fontsize=16)
        plt.tight_layout()
        
        filename = f'{output_path}/{topic.replace(" ", "_")}_sentiment_heatmap.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Sentiment heatmap saved as '{filename}'")
        plt.close()
        return filename

    def plot_sentiment_distribution_pie(self, df, topic, output_path="."):
        """Generate a pie chart showing the distribution of positive, negative, and neutral sentiments"""
        def categorize_sentiment(score):
            if score >= 0.05:
                return "Positive"
            elif score <= -0.05:
                return "Negative"
            else:
                return "Neutral"

        df["sentiment_category"] = df["combined_compound"].apply(categorize_sentiment)
        sentiment_counts = df["sentiment_category"].value_counts()
        
        # Ensure all three categories are present for consistent coloring and explode
        sentiment_counts = sentiment_counts.reindex(["Positive", "Negative", "Neutral"], fill_value=0)

        plt.figure(figsize=(10, 8))
        colors = ['#2ecc71', '#e74c3c', '#3498db']  # Green, Red, Blue
        explode = [0.05] * len(sentiment_counts)
        
        plt.pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%', 
                colors=colors, startangle=90, explode=explode)
        plt.title(f'Sentiment Distribution for {topic}', fontsize=16)
        plt.axis('equal')
        
        filename = f'{output_path}/{topic.replace(" ", "_")}_sentiment_pie.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Sentiment pie chart saved as '{filename}'")
        plt.close()
        return filename

    def generate_wordcloud(self, text_data, topic, output_path="."):
        all_words = ' '.join(text_data)
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_words)
        filename = f'{output_path}/{topic.replace(" ", "_")}_wordcloud.png'
        wordcloud.to_file(filename)
        print(f"Word cloud saved as '{filename}'")
        return filename

    def plot_sentiment_counts(self, df, topic, output_path="."):
        def categorize_sentiment(score):
            if score >= 0.05:
                return "Positive"
            elif score <= -0.05:
                return "Negative"
            else:
                return "Neutral"

        df["sentiment_category"] = df["combined_compound"].apply(categorize_sentiment)
        sentiment_counts = df["sentiment_category"].value_counts().reindex(["Positive", "Negative", "Neutral"])

        plt.figure(figsize=(8, 6))
        sns.barplot(x=sentiment_counts.index, y=sentiment_counts.values, palette=["green", "red", "blue"])
        plt.title(f"Sentiment Distribution for {topic}", fontsize=16)
        plt.xlabel("Sentiment", fontsize=12)
        plt.ylabel("Count", fontsize=12)
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        filename = f"{output_path}/{topic.replace(' ', '_')}_sentiment_counts.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Sentiment counts plot saved as '{filename}'")
        plt.close()
        return filename