"""
Google Sheets API client for exporting analytics data.
Handles authentication and sheet operations.
"""

import pandas as pd
from typing import List, Dict, Any, Optional, Union, Tuple

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

from facebook_instagram_analytics.config import GOOGLE_CREDENTIALS_PATH
from facebook_instagram_analytics.utils.logging_utils import get_logger, LogPerformance

# Initialize logger
logger = get_logger(__name__)


class GoogleSheetsAPI:
    """Client for the Google Sheets API."""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize the Google Sheets API client.
        
        Args:
            credentials_path (str, optional): Path to the Google API credentials JSON file.
                If not provided, will use the path from environment variables.
        """
        self.credentials_path = credentials_path or GOOGLE_CREDENTIALS_PATH
        self.client = None
        self.connect()
    
    def connect(self) -> bool:
        """
        Connect to the Google Sheets API.
        
        Returns:
            bool: True if connection successful, False otherwise.
        """
        logger.info("Connecting to Google Sheets API...")
        
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        try:
            with LogPerformance(logger, "Google Sheets API connection"):
                credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    self.credentials_path, scope
                )
                self.client = gspread.authorize(credentials)
            
            logger.info("Connected to Google Sheets API successfully")
            return True
            
        except FileNotFoundError:
            logger.error(f"Google API credentials file not found: {self.credentials_path}")
            self.client = None
            return False
            
        except Exception as e:
            logger.error(f"Error connecting to Google Sheets API: {str(e)}")
            self.client = None
            return False
    
    def create_spreadsheet(self, title: str) -> Optional[gspread.Spreadsheet]:
        """
        Create a new Google Spreadsheet.
        
        Args:
            title (str): Title of the spreadsheet.
            
        Returns:
            gspread.Spreadsheet or None: The created spreadsheet, or None if creation failed.
        """
        if not self.client:
            logger.error("Not connected to Google Sheets API")
            return None
        
        try:
            with LogPerformance(logger, f"Creating spreadsheet '{title}'"):
                spreadsheet = self.client.create(title)
            
            logger.info(f"Created spreadsheet: {title} (ID: {spreadsheet.id})")
            return spreadsheet
            
        except Exception as e:
            logger.error(f"Error creating spreadsheet '{title}': {str(e)}")
            return None
    
    def get_spreadsheet(self, title: str) -> Optional[gspread.Spreadsheet]:
        """
        Get an existing Google Spreadsheet by title.
        
        Args:
            title (str): Title of the spreadsheet.
            
        Returns:
            gspread.Spreadsheet or None: The spreadsheet, or None if not found.
        """
        if not self.client:
            logger.error("Not connected to Google Sheets API")
            return None
        
        try:
            with LogPerformance(logger, f"Getting spreadsheet '{title}'"):
                spreadsheet = self.client.open(title)
            
            logger.info(f"Found spreadsheet: {title} (ID: {spreadsheet.id})")
            return spreadsheet
            
        except gspread.exceptions.SpreadsheetNotFound:
            logger.info(f"Spreadsheet not found: {title}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting spreadsheet '{title}': {str(e)}")
            return None
    
    def create_or_update_worksheet(
        self, 
        spreadsheet: gspread.Spreadsheet,
        worksheet_title: str,
        data_frame: pd.DataFrame
    ) -> Optional[gspread.Worksheet]:
        """
        Create a new worksheet or update an existing one with DataFrame data.
        
        Args:
            spreadsheet (gspread.Spreadsheet): The spreadsheet to add/update the worksheet in.
            worksheet_title (str): Title of the worksheet.
            data_frame (pandas.DataFrame): Data to write to the worksheet.
            
        Returns:
            gspread.Worksheet or None: The created/updated worksheet, or None if operation failed.
        """
        if not self.client:
            logger.error("Not connected to Google Sheets API")
            return None
        
        try:
            # Check if worksheet exists
            try:
                worksheet = spreadsheet.worksheet(worksheet_title)
                logger.info(f"Updating existing worksheet: {worksheet_title}")
                worksheet.clear()
            except gspread.exceptions.WorksheetNotFound:
                # Create new worksheet
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_title,
                    rows=max(data_frame.shape[0] + 1, 100),  # +1 for header row, min 100 rows
                    cols=max(data_frame.shape[1], 26)        # min 26 columns
                )
                logger.info(f"Created new worksheet: {worksheet_title}")
            
            # Convert DataFrame to list of lists
            data_list = [data_frame.columns.tolist()] + data_frame.values.tolist()
            
            # Update worksheet with data
            with LogPerformance(logger, f"Updating worksheet '{worksheet_title}' with {len(data_list)} rows"):
                worksheet.update(data_list)
            
            logger.info(f"Successfully updated worksheet: {worksheet_title} with {len(data_list)-1} rows of data")
            return worksheet
            
        except Exception as e:
            logger.error(f"Error updating worksheet '{worksheet_title}': {str(e)}")
            return None
    
    def create_or_update_sheet(
        self, 
        sheet_name: str, 
        data_frame: pd.DataFrame,
        worksheet_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a new Google Sheet or update an existing one with DataFrame data.
        
        Args:
            sheet_name (str): Name of the spreadsheet.
            data_frame (pandas.DataFrame): Data to write to the sheet.
            worksheet_name (str, optional): Name of the worksheet. If not provided, uses the first worksheet.
            
        Returns:
            str or None: URL of the spreadsheet, or None if operation failed.
        """
        if not self.client:
            if not self.connect():
                return None
        
        try:
            # Try to open existing sheet
            sheet = self.get_spreadsheet(sheet_name)
            
            if not sheet:
                # Create new sheet
                sheet = self.create_spreadsheet(sheet_name)
                if not sheet:
                    return None
            
            # Determine worksheet name
            if not worksheet_name:
                worksheet_name = "Sheet1"
            
            # Update worksheet with data
            worksheet = self.create_or_update_worksheet(sheet, worksheet_name, data_frame)
            
            if worksheet:
                logger.info(f"Data exported to sheet: {sheet_name}, worksheet: {worksheet_name}")
                return sheet.url
            
            return None
            
        except Exception as e:
            logger.error(f"Error exporting data to Google Sheets: {str(e)}")
            return None
