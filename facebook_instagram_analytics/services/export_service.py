"""
Export service for analytics data.
Handles exporting data to Google Sheets.
"""

import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple

from facebook_instagram_analytics.api.google_sheets_api import GoogleSheetsAPI
from facebook_instagram_analytics.models.account import AccountCollection
from facebook_instagram_analytics.models.insights import (
    AccountInsights, Post, Demographics, AdData, ConsolidatedMetrics
)
from facebook_instagram_analytics.utils.logging_utils import get_logger, LogPerformance
from facebook_instagram_analytics.utils.date_utils import create_filename_timestamp

# Initialize logger
logger = get_logger(__name__)


class ExportService:
    """Service for exporting analytics data to various formats."""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize the export service.
        
        Args:
            credentials_path (str, optional): Path to the Google API credentials JSON file.
        """
        self.google_sheets = GoogleSheetsAPI(credentials_path)
        logger.info("Initialized Export Service")
    
    def export_accounts_data(self, accounts: AccountCollection) -> Optional[str]:
        """
        Export accounts data to Google Sheets.
        
        Args:
            accounts (AccountCollection): Collection of social media accounts.
            
        Returns:
            str or None: URL of the created spreadsheet, or None if export failed.
        """
        if not accounts:
            logger.warning("No accounts data to export")
            return None
        
        logger.info("Exporting accounts data to Google Sheets")
        
        # Create DataFrame from accounts data
        df = pd.DataFrame(accounts.to_list_of_dicts())
        
        # Add a timestamp to make the sheet name unique
        timestamp = create_filename_timestamp()
        sheet_name = f"Facebook_Instagram_Accounts_{timestamp}"
        
        sheet_url = self.google_sheets.create_or_update_sheet(sheet_name, df)
        
        if sheet_url:
            logger.info(f"Accounts data exported to: {sheet_url}")
        else:
            logger.error("Failed to export accounts data")
        
        return sheet_url
    
    def export_metrics_data(
        self, 
        metrics_data: ConsolidatedMetrics, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Optional[str]:
        """
        Export consolidated metrics data to Google Sheets.
        
        Args:
            metrics_data (ConsolidatedMetrics): Consolidated metrics data.
            start_date (str, optional): Start date in YYYY-MM-DD format.
            end_date (str, optional): End date in YYYY-MM-DD format.
            
        Returns:
            str or None: URL of the created spreadsheet, or None if export failed.
        """
        if not metrics_data or not metrics_data.accounts:
            logger.warning("No metrics data to export")
            return None
        
        logger.info("Exporting metrics data to Google Sheets")
        
        # Create DataFrame from accounts metrics
        df = pd.DataFrame(metrics_data.accounts)
        
        # Add a timestamp and date range to make the sheet name unique
        timestamp = create_filename_timestamp()
        sheet_name = f"Metrics_{timestamp}"
        
        if start_date and end_date:
            sheet_name = f"Metrics_{start_date}_to_{end_date}_{timestamp}"
        
        sheet_url = self.google_sheets.create_or_update_sheet(sheet_name, df)
        
        if sheet_url:
            logger.info(f"Metrics data exported to: {sheet_url}")
        else:
            logger.error("Failed to export metrics data")
        
        return sheet_url
    
    def export_top_posts(
        self, 
        top_posts: List[Post], 
        account_name: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Optional[str]:
        """
        Export top posts data to Google Sheets.
        
        Args:
            top_posts (list): List of top posts.
            account_name (str): Name of the account.
            start_date (str, optional): Start date in YYYY-MM-DD format.
            end_date (str, optional): End date in YYYY-MM-DD format.
            
        Returns:
            str or None: URL of the created spreadsheet, or None if export failed.
        """
        if not top_posts:
            logger.warning("No top posts data to export")
            return None
        
        logger.info(f"Exporting top posts data for {account_name} to Google Sheets")
        
        # Create DataFrame from top posts data
        df = pd.DataFrame([post.to_dict() for post in top_posts])
        
        # Add a timestamp and date range to make the sheet name unique
        timestamp = create_filename_timestamp()
        sheet_name = f"Top_Posts_{account_name}_{timestamp}"
        
        if start_date and end_date:
            sheet_name = f"Top_Posts_{account_name}_{start_date}_to_{end_date}_{timestamp}"
        
        sheet_url = self.google_sheets.create_or_update_sheet(sheet_name, df)
        
        if sheet_url:
            logger.info(f"Top posts data exported to: {sheet_url}")
        else:
            logger.error("Failed to export top posts data")
        
        return sheet_url
    
    def export_demographics(
        self, 
        demographics: Demographics, 
        account_name: str
    ) -> Dict[str, Optional[str]]:
        """
        Export demographics data to Google Sheets.
        
        Args:
            demographics (Demographics): Demographics data.
            account_name (str): Name of the account.
            
        Returns:
            dict: Dictionary with URLs of created spreadsheets.
        """
        if not demographics:
            logger.warning("No demographics data to export")
            return {"age_gender_url": None, "location_url": None}
        
        logger.info(f"Exporting demographics data for {account_name} to Google Sheets")
        
        # Get DataFrames for age/gender and location
        dataframes = demographics.to_dataframes()
        
        # Add a timestamp to make the sheet names unique
        timestamp = create_filename_timestamp()
        
        # Export both DataFrames
        sheet_name_age_gender = f"Demographics_AgeGender_{account_name}_{timestamp}"
        sheet_name_location = f"Demographics_Location_{account_name}_{timestamp}"
        
        age_gender_url = self.google_sheets.create_or_update_sheet(
            sheet_name_age_gender, 
            dataframes['age_gender']
        )
        
        location_url = self.google_sheets.create_or_update_sheet(
            sheet_name_location, 
            dataframes['location']
        )
        
        if age_gender_url:
            logger.info(f"Age/gender demographics exported to: {age_gender_url}")
        
        if location_url:
            logger.info(f"Location demographics exported to: {location_url}")
        
        return {
            "age_gender_url": age_gender_url,
            "location_url": location_url
        }
    
    def export_ads_data(
        self, 
        ads_data: List[AdData], 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Optional[str]:
        """
        Export Facebook Ads data to Google Sheets.
        
        Args:
            ads_data (list): List of ad data objects.
            start_date (str, optional): Start date in YYYY-MM-DD format.
            end_date (str, optional): End date in YYYY-MM-DD format.
            
        Returns:
            str or None: URL of the created spreadsheet, or None if export failed.
        """
        if not ads_data:
            logger.warning("No ads data to export")
            return None
        
        logger.info("Exporting ads data to Google Sheets")
        
        # Create DataFrame from ads data
        df = pd.DataFrame([ad.to_dict() for ad in ads_data])
        
        # Add a timestamp and date range to make the sheet name unique
        timestamp = create_filename_timestamp()
        sheet_name = f"Ads_Data_{timestamp}"
        
        if start_date and end_date:
            sheet_name = f"Ads_Data_{start_date}_to_{end_date}_{timestamp}"
        
        sheet_url = self.google_sheets.create_or_update_sheet(sheet_name, df)
        
        if sheet_url:
            logger.info(f"Ads data exported to: {sheet_url}")
        else:
            logger.error("Failed to export ads data")
        
        return sheet_url
