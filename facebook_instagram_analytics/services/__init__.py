"""
Service layer for Facebook API operations.

This package contains service classes that implement business logic
for various Facebook API operations. These services abstract the
underlying API calls and provide a higher-level interface for
common tasks and workflows.

Main components:
- PageService: Operations for managing Facebook Pages
- PostService: Content publishing and management
- InsightsService: Analytics and metrics retrieval
- WebhookService: Handling real-time updates via webhooks
"""

from facebook_api.services.page_service import PageService
from facebook_api.services.post_service import PostService
from facebook_api.services.insights_service import InsightsService
from facebook_api.services.webhook_service import WebhookService

__all__ = [
    'PageService',
    'PostService',
    'InsightsService',
    'WebhookService'
]
