"""
Configuration module for Facebook Instagram Analytics.
Loads environment variables and provides application settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Facebook API configuration
FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
FACEBOOK_API_VERSION = os.getenv('FACEBOOK_API_VERSION', 'v18.0')
FACEBOOK_BASE_URL = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"

# Google Sheets configuration
GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'facebook_instagram_analytics.log')

# Default date ranges
DEFAULT_LOOKBACK_YEARS = int(os.getenv('DEFAULT_LOOKBACK_YEARS', 2))
DEFAULT_LOOKBACK_MONTHS = int(os.getenv('DEFAULT_LOOKBACK_MONTHS', 6))

# API request settings
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))  # seconds
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 5))  # seconds
