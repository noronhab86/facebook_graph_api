"""
Facebook API client module.

This package provides interfaces for interacting with Facebook's Graph API
and related endpoints. It includes methods for authentication, data retrieval,
content publishing, and analytics.

Main components:
- GraphAPI: Core client for interacting with the Graph API
- BatchRequest: Handles batch request operations for improved performance
"""

from facebook_api.api.graph_api import GraphAPI
from facebook_api.api.batch_requests import BatchRequest

__all__ = ['GraphAPI', 'BatchRequest']
