"""
Facebook & Instagram Analytics Tool.

A comprehensive Python package for analyzing and visualizing 
Facebook and Instagram analytics data. This tool integrates 
with the Facebook Graph API to provide detailed insights into 
account performance, audience demographics, and ads data.

This package provides tools for:
- Account Analysis: Fetch and analyze data from connected Facebook Pages and Instagram Business accounts
- Audience Demographics: Understand your audience with detailed demographic breakdowns
- Post Performance: Identify top-performing content across platforms
- Ads Analysis: Analyze Facebook Ads performance with detailed metrics
- Google Sheets Integration: Export data to Google Sheets for easy sharing and additional analysis
- Data Visualization: Generate insightful visualizations of key performance metrics
"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("facebook_instagram_analytics")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.1.0"  # Default version if package is not installed

from facebook_instagram_analytics.services.analytics_service import AnalyticsService
from facebook_instagram_analytics.services.export_service import ExportService
from facebook_instagram_analytics.services.visualization_service import VisualizationService

__all__ = [
    'AnalyticsService',
    'ExportService',
    'VisualizationService',
]
