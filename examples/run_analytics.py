#!/usr/bin/env python
"""
Example script for running Facebook & Instagram Analytics.
Demonstrates how to use the refactored analytics library.
"""

import os
import sys
import argparse
import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional, Tuple

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from facebook_instagram_analytics.utils.logging_utils import get_logger
from facebook_instagram_analytics.utils.date_utils import get_date_range
from facebook_instagram_analytics.services.analytics_service import AnalyticsService
from facebook_instagram_analytics.services.export_service import ExportService
from facebook_instagram_analytics.services.visualization_service import VisualizationService

# Initialize logger
logger = get_logger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Facebook & Instagram Analytics Tool'
    )
    
    parser.add_argument(
        '--access-token',
        help='Facebook API access token (overrides .env setting)'
    )
    
    parser.add_argument(
        '--google-credentials',
        help='Path to Google API credentials file (overrides .env setting)'
    )
    
    parser.add_argument(
        '--start-date',
        help='Start date for analytics (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--end-date',
        help='End date for analytics (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--months',
        type=int,
        default=6,
        help='Number of months to analyze (default: 6, used if start-date not provided)'
    )
    
    parser.add_argument(
        '--ad-account',
        help='Specific Ad Account ID to analyze'
    )
    
    parser.add_argument(
        '--account',
        help='Specific Account ID to analyze (Facebook Page or Instagram)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Directory to save visualizations (default: output)'
    )
    
    return parser.parse_args()


def get_date_range_from_args(args) -> Tuple[str, str]:
    """Get date range from command line arguments."""
    if args.start_date and args.end_date:
        return args.start_date, args.end_date
    
    end_date = datetime.datetime.now()
    
    if args.end_date:
        end_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d")
    
    if args.start_date:
        start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d")
    else:
        start_date = end_date - relativedelta(months=args.months)
    
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


def main():
    """Main function for the analytics tool."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Get date range
    start_date, end_date = get_date_range_from_args(args)
    logger.info(f"Analyzing data from {start_date} to {end_date}")
    
    # Initialize services
    analytics = AnalyticsService(access_token=args.access_token)
    export = ExportService(credentials_path=args.google_credentials)
    visualization = VisualizationService(output_dir=args.output_dir)
    
    # Get all connected accounts
    logger.info("Getting connected accounts...")
    accounts = analytics.get_connected_accounts()
    
    logger.info(f"Found {len(accounts.get_all_accounts())} connected accounts:")
    for account in accounts.get_all_accounts():
        logger.info(f"- {account.name} ({account.account_type})")
    
    # Export accounts to Google Sheets
    accounts_sheet_url = export.export_accounts_data(accounts)
    if accounts_sheet_url:
        logger.info(f"Accounts data exported to: {accounts_sheet_url}")
    
    # Get consolidated metrics
    logger.info("Getting consolidated metrics...")
    metrics = analytics.get_consolidated_metrics(start_date, end_date)
    
    logger.info("Facebook Metrics:")
    for metric, value in metrics.facebook.items():
        logger.info(f"- {metric.capitalize()}: {value}")
    
    logger.info("Instagram Metrics:")
    for metric, value in metrics.instagram.items():
        logger.info(f"- {metric.capitalize()}: {value}")
    
    # Export metrics to Google Sheets
    metrics_sheet_url = export.export_metrics_data(metrics, start_date, end_date)
    if metrics_sheet_url:
        logger.info(f"Metrics data exported to: {metrics_sheet_url}")
    
    # Generate metrics visualizations
    metrics_viz_path = visualization.generate_metrics_comparison(
        metrics, start_date, end_date
    )
    logger.info(f"Metrics comparison visualization saved to: {metrics_viz_path}")
    
    account_viz_path = visualization.generate_platform_metrics_breakdown(metrics)
    logger.info(f"Account metrics breakdown visualization saved to: {account_viz_path}")
    
    # Process specific accounts
    specific_account = args.account
    
    if specific_account:
        logger.info(f"Processing specific account: {specific_account}")
        
        account = accounts.find_by_id(specific_account)
        
        if account:
            logger.info(f"Found account: {account.name} ({account.account_type})")
            
            # Get top posts
            logger.info(f"Getting top posts for {account.name}...")
            top_posts = analytics.get_top_posts(
                account.id, account.account_type, start_date, end_date
            )
            
            if top_posts:
                logger.info(f"Found {len(top_posts)} top posts")
                
                # Export top posts to Google Sheets
                top_posts_url = export.export_top_posts(
                    top_posts, account.name, start_date, end_date
                )
                
                if top_posts_url:
                    logger.info(f"Top posts data exported to: {top_posts_url}")
            
            # Get demographic breakdown
            logger.info(f"Getting demographic breakdown for {account.name}...")
            demographics = analytics.get_demographic_breakdown(
                account.id, account.account_type
            )
            
            if demographics:
                # Export demographics to Google Sheets
                demographics_urls = export.export_demographics(demographics, account.name)
                
                if demographics_urls.get('age_gender_url'):
                    logger.info(f"Age/Gender demographics exported to: {demographics_urls['age_gender_url']}")
                
                if demographics_urls.get('location_url'):
                    logger.info(f"Location demographics exported to: {demographics_urls['location_url']}")
                
                # Generate demographics visualizations
                demo_viz_paths = visualization.generate_demographics_visualization(
                    demographics, account.name
                )
                
                if demo_viz_paths.get('age_gender'):
                    logger.info(f"Age/Gender visualization saved to: {demo_viz_paths['age_gender']}")
                
                if demo_viz_paths.get('location'):
                    logger.info(f"Location visualization saved to: {demo_viz_paths['location']}")
        else:
            logger.error(f"Account with ID {specific_account} not found")
    
    # Process Facebook Ads data
    logger.info("Getting Facebook Ads data...")
    ads_data = analytics.get_facebook_ads_data(
        ad_account_id=args.ad_account,
        start_date=start_date,
        end_date=end_date
    )
    
    if ads_data:
        logger.info(f"Found {len(ads_data)} ads data records")
        
        # Export ads data to Google Sheets
        ads_data_url = export.export_ads_data(ads_data, start_date, end_date)
        if ads_data_url:
            logger.info(f"Ads data exported to: {ads_data_url}")
        
        # Generate ads visualizations
        ads_viz_paths = visualization.generate_ads_performance_visualization(
            ads_data, start_date, end_date
        )
        
        for viz_type, path in ads_viz_paths.items():
            logger.info(f"Ads {viz_type} visualization saved to: {path}")
    else:
        logger.warning("No ads data found")
    
    logger.info("Analytics process completed successfully")


if __name__ == "__main__":
    main()
