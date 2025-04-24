# Facebook & Instagram Analytics Tool

A comprehensive Python package for analyzing and visualizing Facebook and Instagram analytics data. This tool integrates with the Facebook Graph API to provide detailed insights into account performance, audience demographics, and ads data.

## Features

- **Account Analysis**: Fetch and analyze data from connected Facebook Pages and Instagram Business accounts
- **Audience Demographics**: Understand your audience with detailed demographic breakdowns
- **Post Performance**: Identify top-performing content across platforms
- **Ads Analysis**: Analyze Facebook Ads performance with detailed metrics
- **Google Sheets Integration**: Export data to Google Sheets for easy sharing and additional analysis
- **Data Visualization**: Generate insightful visualizations of key performance metrics

## Project Structure

```
facebook_instagram_analytics/
│
├── facebook_instagram_analytics/
│   ├── __init__.py
│   ├── config.py                 # Configuration settings
│   ├── api/                      # API clients
│   │   ├── __init__.py
│   │   ├── facebook_api.py       # Facebook Graph API client
│   │   └── google_sheets_api.py  # Google Sheets API client
│   │
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── account.py            # Social media account models
│   │   ├── analytics.py          # Analytics data models
│   │   ├── insights.py           # Insights and metrics models
│   │   └── ads.py                # Ads data models
│   │
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── analytics_service.py  # Analytics processing service
│   │   ├── export_service.py     # Data export service
│   │   └── visualization_service.py  # Data visualization service
│   │
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       ├── date_utils.py         # Date handling utilities
│       └── logging_utils.py      # Logging configuration
│
└── examples/                     # Example scripts
    └── run_analytics.py          # Main runner script
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Facebook Developer Account with API access
- Google Cloud project with Sheets API enabled (for export functionality)

### Install from PyPI

```bash
pip install facebook-instagram-analytics
```

### Install from Source

```bash
git clone https://github.com/yourusername/facebook-instagram-analytics.git
cd facebook-instagram-analytics
pip install -e .
```

## Configuration

Create a `.env` file based on the provided `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file with your API credentials:

```
# Facebook API Configuration
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token_here
FACEBOOK_API_VERSION=v18.0

# Google Sheets Configuration
GOOGLE_CREDENTIALS_PATH=credentials.json

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=facebook_instagram_analytics.log
```

## Usage

### Basic Usage

```python
from facebook_instagram_analytics.services.analytics_service import AnalyticsService
from facebook_instagram_analytics.services.export_service import ExportService
from facebook_instagram_analytics.services.visualization_service import VisualizationService

# Initialize services
analytics = AnalyticsService()
export = ExportService()
visualization = VisualizationService()

# Get connected accounts
accounts = analytics.get_connected_accounts()

# Get consolidated metrics for the last 6 months
metrics = analytics.get_consolidated_metrics()

# Export metrics to Google Sheets
sheet_url = export.export_metrics_data(metrics)

# Generate visualizations
viz_path = visualization.generate_metrics_comparison(metrics)
```

### Command Line Interface

The package includes a command-line interface for easy usage:

```bash
# Basic usage
fb-ig-analytics

# Specify date range
fb-ig-analytics --start-date 2023-01-01 --end-date 2023-06-30

# Analyze a specific account
fb-ig-analytics --account 123456789012345

# Analyze a specific ad account
fb-ig-analytics --ad-account act_123456789

# Customize output directory
fb-ig-analytics --output-dir my_reports
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
