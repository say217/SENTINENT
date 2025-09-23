from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session, flash
from markupsafe import Markup
import markdown
import pandas as pd
import logging
import os
import sqlite3
import smtplib
from email.mime.text import MIMEText
from passlib.hash import pbkdf2_sha256
from functools import wraps
from data_collector import RedditDataCollector
from sentiment_analyzer import SentimentAnalyzer
from visualization_generator import VisualizationGenerator
from report_generator import ReportGenerator
from image_search_integration import ImageSearchIntegration
from config import Config
import random
import string
from datetime import datetime, timedelta
import traceback

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(days=1)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
config = Config()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Log session state before each request
@app.before_request
def log_session_state():
    logging.info(f"Request to {request.path} with session: {session.get('email')}")

# Database initialization
def init_db():
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS pending_users (
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                verification_code TEXT NOT NULL,
                created_at DATETIME NOT NULL
            )
        ''')
        conn.commit()

# Initialize database on app start
init_db()

# Email validation
def is_valid_email(email):
    return '@' in email and '.' in email and len(email) > 5

# Generate verification code
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

# Send verification email
def send_verification_email(email, code):
    try:
        msg = MIMEText(f"Your verification code is: {code}\n\nPlease enter this code to verify your email. It expires in 10 minutes.")
        msg['Subject'] = 'Verify Your Email - Sentiment Analysis App'
        msg['From'] = config.SMTP_USERNAME
        msg['To'] = email
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.set_debuglevel(1)  # Enable SMTP debug output
            server.starttls()
            server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
            server.send_message(msg)
        logging.info(f"Verification email sent to {email} with code {code}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"SMTP authentication failed: {e}\nTraceback: {traceback.format_exc()}")
        flash("Failed to send verification email. Check SMTP credentials.", "error")
        return False
    except smtplib.SMTPConnectError as e:
        logging.error(f"SMTP connection failed: {e}\nTraceback: {traceback.format_exc()}")
        flash("Failed to send verification email. Unable to connect to SMTP server.", "error")
        return False
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error: {e}\nTraceback: {traceback.format_exc()}")
        flash("Failed to send verification email. SMTP server issue.", "error")
        return False
    except Exception as e:
        logging.error(f"Unexpected error sending email to {email}: {e}\nTraceback: {traceback.format_exc()}")
        flash("An unexpected error occurred while sending the verification email.", "error")
        return False

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            logging.warning(f"Session missing 'email' for {request.path}. Redirecting to login.")
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        logging.info(f"Session valid for user: {session['email']} at {request.path}")
        return f(*args, **kwargs)
    return decorated_function

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        if not is_valid_email(email):
            flash('Invalid email format.', 'error')
            return render_template('signup.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('signup.html')
        try:
            with sqlite3.connect('users.db') as conn:
                c = conn.cursor()
                c.execute('SELECT email FROM users WHERE email = ?', (email,))
                if c.fetchone():
                    flash('Email already registered.', 'error')
                    return render_template('signup.html')
                c.execute('SELECT email FROM pending_users WHERE email = ?', (email,))
                if c.fetchone():
                    c.execute('DELETE FROM pending_users WHERE email = ?', (email,))
                verification_code = generate_verification_code()
                password_hash = pbkdf2_sha256.hash(password)
                created_at = datetime.utcnow()
                c.execute('INSERT INTO pending_users (email, password_hash, verification_code, created_at) VALUES (?, ?, ?, ?)',
                          (email, password_hash, verification_code, created_at))
                conn.commit()
            if send_verification_email(email, verification_code):
                flash('A verification code has been sent to your email.', 'success')
                return redirect(url_for('verify', email=email))
            else:
                flash('Failed to send verification email. Please try again.', 'error')
                return render_template('signup.html')
        except Exception as e:
            logging.error(f"Signup error: {e}\nTraceback: {traceback.format_exc()}")
            flash('An error occurred during signup. Please try again.', 'error')
            return render_template('signup.html')
    return render_template('signup.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    email = request.args.get('email')
    if not email:
        flash('Invalid verification request.', 'error')
        return redirect(url_for('signup'))
    if request.method == 'POST':
        code = request.form['code']
        try:
            with sqlite3.connect('users.db') as conn:
                c = conn.cursor()
                c.execute('SELECT password_hash, verification_code, created_at FROM pending_users WHERE email = ?', (email,))
                result = c.fetchone()
                if not result:
                    flash('Invalid or expired verification request.', 'error')
                    return render_template('verify.html', email=email)
                password_hash, stored_code, created_at = result
                created_at = datetime.fromisoformat(created_at)
                if datetime.utcnow() > created_at + timedelta(minutes=10):
                    c.execute('DELETE FROM pending_users WHERE email = ?', (email,))
                    conn.commit()
                    flash('Verification code expired. Please sign up again.', 'error')
                    return redirect(url_for('signup'))
                if code != stored_code:
                    flash('Invalid verification code.', 'error')
                    return render_template('verify.html', email=email)
                c.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (email, password_hash))
                c.execute('DELETE FROM pending_users WHERE email = ?', (email,))
                conn.commit()
                session.permanent = True  # Make session persistent
                session['email'] = email  # Log in the user
                flash('Email verified successfully! Welcome!', 'success')
                return redirect(url_for('welcome'))  # Redirect to welcome page
        except Exception as e:
            logging.error(f"Verification error: {e}\nTraceback: {traceback.format_exc()}")
            flash('An error occurred during verification.', 'error')
            return render_template('verify.html', email=email)
    return render_template('verify.html', email=email)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        if not is_valid_email(email):
            flash('Invalid email format.', 'error')
            return render_template('login.html')
        try:
            with sqlite3.connect('users.db') as conn:
                c = conn.cursor()
                c.execute('SELECT password_hash FROM users WHERE email = ?', (email,))
                result = c.fetchone()
                if result and pbkdf2_sha256.verify(password, result[0]):
                    session.permanent = True  # Make session persistent
                    session['email'] = email
                    flash('Login successful!', 'success')
                    return redirect(url_for('welcome'))  # Redirect to welcome page
                else:
                    flash('Invalid email or password.', 'error')
                    return render_template('login.html')
        except Exception as e:
            logging.error(f"Login error: {e}\nTraceback: {traceback.format_exc()}")
            flash('An error occurred during login.', 'error')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/welcome')
@login_required
def welcome():
    logging.info(f"Rendering welcome.html for user: {session.get('email')}")
    return render_template('welcome.html', email=session.get('email'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/', methods=['GET'])
@login_required
def index():
    logging.info(f"Rendering index.html for user: {session.get('email')}")
    return render_template('index.html', email=session.get('email'))

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    logging.info(f"Analyze route accessed. Session: {session.get('email')}, Form data: {request.form}")
    topic = request.form.get('topic')
    if not topic:
        logging.error("No topic provided in form submission")
        flash('Please provide a topic.', 'error')
        return redirect(url_for('index'))

    # Initialize components
    try:
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
        image_search = ImageSearchIntegration(output_dir=config.OUTPUT_DIR, api_key=config.PIXABAY_API_KEY)
    except Exception as e:
        logging.error(f"Initialization error: {e}\nTraceback: {traceback.format_exc()}")
        return render_template('results.html', error=f"Initialization error: {e}")

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
        logging.error(f"Data collection error: {e}\nTraceback: {traceback.format_exc()}")
        return render_template('results.html', error=f"Data collection error: {e}")

    if not data:
        logging.warning(f"No data found for topic '{topic}'. Try a different topic or check your API credentials.")
        return render_template('results.html', error=f"No data found for topic '{topic}'.")

    df = pd.DataFrame(data)

    # 2. Perform Sentiment Analysis
    logging.info("Performing sentiment analysis...")
    try:
        sentiment_results = sentiment_analyzer.analyze(data)
        sentiment_df = pd.DataFrame(sentiment_results)
    except Exception as e:
        logging.error(f"Sentiment analysis error: {e}\nTraceback: {traceback.format_exc()}")
        return render_template('results.html', error=f"Sentiment analysis error: {e}")

    # Save raw sentiment results to CSV
    output_csv_filename = f"{topic.replace(' ', '_')}_sentiment_results.csv"
    output_csv_path = os.path.join(config.OUTPUT_DIR, output_csv_filename)
    try:
        sentiment_df.to_csv(output_csv_path, index=False)
        logging.info(f"Sentiment results saved to {output_csv_path}")
    except Exception as e:
        logging.error(f"Error saving CSV: {e}\nTraceback: {traceback.format_exc()}")
        return render_template('results.html', error=f"Error saving CSV: {e}")

    # Read CSV data for display (up to 20 rows for scrollable table)
    try:
        csv_data = pd.read_csv(output_csv_path).iloc[:20].to_dict(orient='records')
        csv_columns = pd.read_csv(output_csv_path).columns.tolist()
    except Exception as e:
        logging.error(f"Error reading CSV data: {e}\nTraceback: {traceback.format_exc()}")
        csv_data = []
        csv_columns = []

    # 3. Generate Visualizations
    logging.info("Generating visualizations...")
    try:
        plot_filenames = viz_generator.plot_sentiment_analysis(sentiment_df, topic, output_path=config.OUTPUT_DIR)
        wordcloud_file = viz_generator.generate_wordcloud(sentiment_df["text"], topic, output_path=config.OUTPUT_DIR)
        sentiment_counts_file = viz_generator.plot_sentiment_counts(sentiment_df, topic, output_path=config.OUTPUT_DIR)
        heatmap_file = viz_generator.plot_sentiment_heatmap(sentiment_df, topic, output_path=config.OUTPUT_DIR)
        pie_file = viz_generator.plot_sentiment_distribution_pie(sentiment_df, topic, output_path=config.OUTPUT_DIR)
    except Exception as e:
        logging.error(f"Visualization error: {e}\nTraceback: {traceback.format_exc()}")
        return render_template('results.html', error=f"Visualization error: {e}")

    # 4. Fetch Topic Image
    logging.info(f"Fetching image for topic: {topic}")
    try:
        image_path = image_search.search_and_download_image(topic)
        topic_image_filename = os.path.basename(image_path) if image_path else None
    except Exception as e:
        logging.error(f"Image search error: {e}\nTraceback: {traceback.format_exc()}")
        topic_image_filename = None

    # 5. Generate Report
    logging.info("Generating summary report...")
    try:
        # Pass the first plot filename for the report (e.g., distribution plot)
        report_file = report_generator.generate_summary_report(sentiment_df, topic, plot_filenames['distribution'], wordcloud_file, sentiment_counts_file)
    except Exception as e:
        logging.error(f"Report generation error: {e}\nTraceback: {traceback.format_exc()}")
        return render_template('results.html', error=f"Report generation error: {e}")

    # Prepare data for rendering in template
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            report_markdown = f.read()
        report_html = markdown.markdown(report_markdown, extensions=['tables', 'fenced_code'])
        report_content = Markup(report_html)
    except Exception as e:
        logging.error(f"Error reading report: {e}\nTraceback: {traceback.format_exc()}")
        return render_template('results.html', error=f"Error generating report: {e}")

    # Get paths for images
    distribution_filename = os.path.basename(plot_filenames['distribution']) if plot_filenames.get('distribution') else None
    subreddit_filename = os.path.basename(plot_filenames['subreddit']) if plot_filenames.get('subreddit') else None
    trend_filename = os.path.basename(plot_filenames['trend']) if plot_filenames.get('trend') else None
    type_filename = os.path.basename(plot_filenames['type']) if plot_filenames.get('type') else None
    wordcloud_filename = os.path.basename(wordcloud_file) if wordcloud_file else None
    sentiment_counts_filename = os.path.basename(sentiment_counts_file) if sentiment_counts_file else None
    heatmap_filename = os.path.basename(heatmap_file) if heatmap_file else None
    pie_filename = os.path.basename(pie_file) if pie_file else None

    return render_template(
        'results.html',
        topic=topic,
        report_content=report_content,
        distribution_image=distribution_filename,
        subreddit_image=subreddit_filename,
        trend_image=trend_filename,
        type_image=type_filename,
        wordcloud_image=wordcloud_filename,
        sentiment_counts_image=sentiment_counts_filename,
        heatmap_image=heatmap_filename,
        pie_image=pie_filename,
        topic_image=topic_image_filename,
        csv_file=output_csv_filename,
        csv_data=csv_data,
        csv_columns=csv_columns,
        email=session.get('email')
    )

@app.route('/output/<filename>')
@login_required
def output_file(filename):
    return send_from_directory(config.OUTPUT_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)