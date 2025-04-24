"""
Date utility functions for Facebook Instagram Analytics.
Provides helper functions for date formatting and ranges.
"""

import datetime
from dateutil.relativedelta import relativedelta

from facebook_instagram_analytics.config import DEFAULT_LOOKBACK_YEARS, DEFAULT_LOOKBACK_MONTHS


def format_date(date):
    """
    Format date for API requests.
    
    Args:
        date (str or datetime): Date to format
        
    Returns:
        str: Formatted date string in YYYY-MM-DD format
    """
    if isinstance(date, str):
        try:
            date = datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {date}. Expected YYYY-MM-DD.")
    
    return date.strftime("%Y-%m-%d")


def get_date_range(start_date=None, end_date=None, years_back=DEFAULT_LOOKBACK_YEARS):
    """
    Get formatted date range, default to last specified years if not provided.
    
    Args:
        start_date (str or datetime, optional): Start date
        end_date (str or datetime, optional): End date
        years_back (int, optional): Number of years to look back if start_date not provided
        
    Returns:
        tuple: Formatted start and end dates (YYYY-MM-DD)
    """
    if end_date is None:
        end_date = datetime.datetime.now()
    elif isinstance(end_date, str):
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    
    if start_date is None:
        start_date = end_date - relativedelta(years=years_back)
    elif isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    
    return format_date(start_date), format_date(end_date)


def get_monthly_date_ranges(start_date, end_date):
    """
    Split a date range into monthly chunks for API pagination.
    
    Args:
        start_date (str or datetime): Start date
        end_date (str or datetime): End date
        
    Returns:
        list: List of (start_date, end_date) tuples for each month
    """
    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    
    if isinstance(end_date, str):
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    
    # Initialize the result list
    monthly_ranges = []
    
    # Set the first month's start date
    current_start = start_date
    
    while current_start < end_date:
        # Calculate the end of the current month
        if current_start.month == 12:
            current_end = datetime.datetime(current_start.year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            current_end = datetime.datetime(current_start.year, current_start.month + 1, 1) - datetime.timedelta(days=1)
        
        # If current_end is beyond the overall end_date, use end_date instead
        if current_end > end_date:
            current_end = end_date
        
        # Add the range to the result
        monthly_ranges.append((format_date(current_start), format_date(current_end)))
        
        # Move to the next month
        if current_end.month == 12:
            current_start = datetime.datetime(current_end.year + 1, 1, 1)
        else:
            current_start = datetime.datetime(current_end.year, current_end.month + 1, 1)
    
    return monthly_ranges


def create_filename_timestamp():
    """
    Create a timestamp string for filename usage.
    
    Returns:
        str: Timestamp string in YYYYMMDD_HHMMSS format
    """
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
