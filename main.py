import pandas as pd
import os
import logging
from config import Config  # Adjusted to match assumed Config class
from data_collector import RedditDataCollector
from sentiment_analyzer import SentimentAnalyzer
from visualization_generator import VisualizationGenerator
from report_generator import ReportGenerator
from image_search_integration import ImageSearchIntegration

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    try:
        config = Config()
        config.validate_reddit_credentials()
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
        return

    topic = input("Enter the topic to analyze: ")

    # Initialize components
    data_collector = RedditDataCollector(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        user_agent=config.REDDIT_USER_AGENT,
        username=config.REDDIT_USERNAME,
        password=config.REDDIT_PASSWORD
    )
    sentiment_analyzer = SentimentAnalyzer()
    viz_generator = VisualizationGenerator()
    report_generator = ReportGenerator(output_dir=config.OUTPUT_DIR)
    image_search_integrator = ImageSearchIntegration(output_dir=config.OUTPUT_DIR)

    # 1. Collect Data
    logging.info(f"Collecting Reddit data for topic: {topic}")
    try:
        data = data_collector.collect_data(
            topic,
            subreddit_name=config.DEFAULT_SUBREDDIT,
            post_limit=config.DEFAULT_POST_LIMIT,
            comment_limit=config.DEFAULT_COMMENT_LIMIT
        )
    except Exception as e:
        logging.error(f"Data collection error: {e}")
        return

    if not data:
        logging.warning(f"No data found for topic {topic}. Try a different topic or check your API credentials.")
        return

    df = pd.DataFrame(data)

    # 2. Perform Sentiment Analysis
    logging.info("Performing sentiment analysis...")
    try:
        sentiment_results = sentiment_analyzer.analyze(data)
        sentiment_df = pd.DataFrame(sentiment_results)
    except Exception as e:
        logging.error(f"Sentiment analysis error: {e}")
        return

    # Save raw sentiment results to CSV
    topic_clean = topic.replace(" ", "_")
    output_csv_path = os.path.join(config.OUTPUT_DIR, f"{topic_clean}_sentiment_results.csv")
    try:
        sentiment_df.to_csv(output_csv_path, index=False)
        logging.info(f"Sentiment results saved to {output_csv_path}")
    except Exception as e:
        logging.error(f"Error saving CSV: {e}")
        return

    # Display basic statistics
    logging.info("\nSentiment Analysis Statistics:")
    logging.info(sentiment_df[["vader_neg", "vader_neu", "vader_pos", "vader_compound", "textblob_polarity", "combined_compound"]].describe())

    # Show top 5 most positive and negative texts
    logging.info("\nTop 5 Most Positive Texts:")
    logging.info(sentiment_df.nlargest(5, "combined_compound")[["text", "combined_compound", "type", "subreddit"]])
    logging.info("\nTop 5 Most Negative Texts:")
    logging.info(sentiment_df.nsmallest(5, "combined_compound")[["text", "combined_compound", "type", "subreddit"]])

    # 3. Generate Visualizations
    logging.info("Generating visualizations...")
    try:
        plot_file = viz_generator.plot_sentiment_analysis(sentiment_df, topic, output_path=config.OUTPUT_DIR)
        wordcloud_file = viz_generator.generate_wordcloud(sentiment_df["text"], topic, output_path=config.OUTPUT_DIR)
        sentiment_counts_file = viz_generator.plot_sentiment_counts(sentiment_df, topic, output_path=config.OUTPUT_DIR)
        
        # New plots
        heatmap_file = viz_generator.plot_sentiment_heatmap(sentiment_df, topic, output_path=config.OUTPUT_DIR)
        pie_chart_file = viz_generator.plot_sentiment_distribution_pie(sentiment_df, topic, output_path=config.OUTPUT_DIR)

    except Exception as e:
        logging.error(f"Visualization error: {e}")
        return

    # 4. Search and download image for the topic
    logging.info(f"Searching for an image related to {topic}...")
    topic_image_path = None
    try:
        image_results = image_search_integrator.search_and_download_image(topic)
        if image_results:
            topic_image_path = image_search_integrator.copy_image_to_output(image_results, topic)
            logging.info(f"Found and saved topic image: {topic_image_path}")
        else:
            logging.warning(f"No image found for topic {topic}.")
    except Exception as e:
        logging.error(f"Image search/download error: {e}")

    # 5. Generate Report
    logging.info("Generating summary report...")
    try:
        report_file = report_generator.generate_summary_report(
            sentiment_df, 
            topic, 
            plot_file, 
            wordcloud_file, 
            sentiment_counts_file,
            heatmap_path=heatmap_file,
            pie_path=pie_chart_file,
            topic_image_path=topic_image_path
        )
        logging.info(f"Analysis complete. Report available at {report_file}")
    except Exception as e:
        logging.error(f"Report generation error: {e}")
        return

if __name__ == "__main__":
    main()


