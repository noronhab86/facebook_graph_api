"""
Data models for Facebook API entities.

This package contains data model classes that represent various
Facebook entities such as users, pages, posts, and insights.
These models provide structured access to API data and helper
methods for common operations.

Main components:
- User: Models for Facebook user data
- Page: Models for Facebook Page data
- Post: Models for content posts and media
- Insights: Models for analytics and metrics data
"""

from facebook_api.models.user import User, UserProfile
from facebook_api.models.page import Page, PageSettings
from facebook_api.models.post import Post, Media, Comment
from facebook_api.models.insights import Metric, Insight, InsightPeriod

__all__ = [
    'User', 'UserProfile',
    'Page', 'PageSettings',
    'Post', 'Media', 'Comment',
    'Metric', 'Insight', 'InsightPeriod'
]
