import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        # Reddit API credentials
        self.REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
        self.REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
        self.REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
        self.REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
        self.REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
        # SMTP configuration
        self.SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
        self.SMTP_USERNAME = os.getenv("SMTP_USERNAME")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        # Pixabay API key
        self.PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
        # Other settings
        self.DEFAULT_SUBREDDIT = "all"
        self.DEFAULT_POST_LIMIT = 10
        self.DEFAULT_COMMENT_LIMIT = 10
        self.OUTPUT_DIR = os.path.abspath(os.path.join(os.getcwd(), "..", "output"))
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        # Validate configurations
        self.validate_reddit_credentials()
        self.validate_smtp_credentials()
        self.validate_pixabay_credentials()

    def validate_reddit_credentials(self):
        if not all([
            self.REDDIT_CLIENT_ID,
            self.REDDIT_CLIENT_SECRET,
            self.REDDIT_USER_AGENT,
            self.REDDIT_USERNAME,
            self.REDDIT_PASSWORD
        ]):
            raise ValueError("Missing one or more required Reddit API credentials in .env file.")

    def validate_smtp_credentials(self):
        if not all([self.SMTP_USERNAME, self.SMTP_PASSWORD]):
            raise ValueError("Missing SMTP_USERNAME or SMTP_PASSWORD in .env file.")

    def validate_pixabay_credentials(self):
        if not self.PIXABAY_API_KEY:
            raise ValueError("Missing PIXABAY_API_KEY in .env file.")