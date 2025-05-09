"""
Analytics service for Facebook and Instagram data.
Fetches and processes social media analytics data.
"""

import json
from typing import Dict, List, Optional, Any, Union, Tuple

from facebook_instagram_analytics.api.facebook_api import FacebookGraphAPI
from facebook_instagram_analytics.models.account import (
    SocialMediaAccount, FacebookPage, InstagramAccount, AdAccount, AccountCollection
)
from facebook_instagram_analytics.models.insights import (
    AccountInsights, Post, Demographics, AdData, ConsolidatedMetrics
)
from facebook_instagram_analytics.utils.date_utils import get_date_range
from facebook_instagram_analytics.utils.logging_utils import get_logger, LogPerformance

# Initialize logger
logger = get_logger(__name__)


class AnalyticsService:
    """Service for fetching and processing Facebook and Instagram analytics data."""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the analytics service.
        
        Args:
            access_token (str, optional): Facebook API access token.
        """
        self.api = FacebookGraphAPI(access_token)
        logger.info("Initialized Analytics Service")
    
    def get_connected_accounts(self) -> AccountCollection:
        """
        Get all Facebook and Instagram accounts connected to the user.
        
        Returns:
            AccountCollection: Collection of connected accounts.
        """
        logger.info("Fetching connected accounts")
        
        accounts = AccountCollection()
        
        with LogPerformance(logger, "Fetching connected accounts"):
            # Get user accounts
            user_response = self.api.make_request('me/accounts')
            
            if not user_response or 'data' not in user_response:
                logger.warning("No Facebook Pages found")
                return accounts
            
            # Process Facebook Pages
            for account_data in user_response.get('data', []):
                fb_page = FacebookPage(
                    id=account_data.get('id'),
                    name=account_data.get('name'),
                    category=account_data.get('category'),
                    access_token=account_data.get('access_token')
                )
                accounts.add_account(fb_page)
                logger.debug(f"Added Facebook Page: {fb_page.name} (ID: {fb_page.id})")
                
                # Get Instagram accounts linked to this Facebook page
                insta_response = self.api.make_request(f"{fb_page.id}/instagram_accounts")
                
                if insta_response and 'data' in insta_response:
                    for insta_data in insta_response.get('data', []):
                        ig_account = InstagramAccount(
                            id=insta_data.get('id'),
                            username=insta_data.get('username', 'Unknown')
                        )
                        accounts.add_account(ig_account)
                        logger.debug(f"Added Instagram account: {ig_account.username} (ID: {ig_account.id})")
            
            # Get Ad Accounts
            ad_accounts_response = self.api.make_request('me/adaccounts')
            
            if ad_accounts_response and 'data' in ad_accounts_response:
                for ad_account_data in ad_accounts_response.get('data', []):
                    ad_account = AdAccount(
                        id=ad_account_data.get('id'),
                        name=ad_account_data.get('name', f"Ad Account {ad_account_data.get('id')}")
                    )
                    accounts.add_account(ad_account)
                    logger.debug(f"Added Ad Account: {ad_account.name} (ID: {ad_account.id})")
        
        logger.info(f"Found {len(accounts.facebook_pages)} Facebook Pages, {len(accounts.instagram_accounts)} Instagram accounts, and {len(accounts.ad_accounts)} Ad Accounts")
        return accounts
    
    def get_facebook_insights(
        self, 
        account_id: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None, 
        metrics: Optional[str] = None
    ) -> Optional[AccountInsights]:
        """
        Get insights for a Facebook page.
        
        Args:
            account_id (str): Facebook Page ID.
            start_date (str, optional): Start date in YYYY-MM-DD format.
            end_date (str, optional): End date in YYYY-MM-DD format.
            metrics (str, optional): Comma-separated list of metrics to fetch.
                
        Returns:
            AccountInsights or None: Insights data for the Facebook page.
        """
        start_date, end_date = get_date_range(start_date, end_date)
        
        if metrics is None:
            metrics = "page_impressions,page_impressions_unique,page_engaged_users,page_post_engagements,page_fans"
        
        logger.info(f"Fetching Facebook insights for account {account_id} from {start_date} to {end_date}")
        
        params = {
            'metric': metrics,
            'period': 'day',
            'since': start_date,
            'until': end_date
        }
        
        with LogPerformance(logger, f"Fetching Facebook insights for {account_id}"):
            insights_response = self.api.make_request(f"{account_id}/insights", params)
        
        if not insights_response or 'data' not in insights_response:
            logger.warning(f"No insights data found for Facebook Page {account_id}")
            return None
        
        insights = AccountInsights(account_id=account_id)
        
        for metric_data in insights_response['data']:
            metric_name = metric_data['name']
            metric_values = metric_data['values']
            insights.add_metric(metric_name, metric_values)
            logger.debug(f"Added metric {metric_name} with {len(metric_values)} data points")
        
        logger.info(f"Fetched {len(insights.metrics)} metrics for Facebook Page {account_id}")
        return insights
    
    def get_instagram_insights(
        self, 
        account_id: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Optional[AccountInsights]:
        """
        Get insights for an Instagram business account.
        
        Args:
            account_id (str): Instagram account ID.
            start_date (str, optional): Start date in YYYY-MM-DD format.
            end_date (str, optional): End date in YYYY-MM-DD format.
                
        Returns:
            AccountInsights or None: Insights data for the Instagram account.
        """
        start_date, end_date = get_date_range(start_date, end_date)
        
        logger.info(f"Fetching Instagram insights for account {account_id} from {start_date} to {end_date}")
        
        # First, get the Instagram business account ID if we have the user ID
        with LogPerformance(logger, f"Retrieving Instagram business account for {account_id}"):
            ig_response = self.api.make_request(f"{account_id}")
        
        if not ig_response:
            logger.warning(f"Could not find Instagram business account for {account_id}")
            return None
        
        ig_business_id = ig_response.get('id')
        
        # Get insights
        metrics = "impressions,reach,profile_views,follower_count"
        params = {
            'metric': metrics,
            'period': 'day',
            'since': start_date,
            'until': end_date
        }
        
        with LogPerformance(logger, f"Fetching Instagram insights for {ig_business_id}"):
            insights_response = self.api.make_request(f"{ig_business_id}/insights", params)
        
        if not insights_response or 'data' not in insights_response:
            logger.warning(f"No insights data found for Instagram account {ig_business_id}")
            return None
        
        insights = AccountInsights(account_id=ig_business_id)
        
        for metric_data in insights_response['data']:
            metric_name = metric_data['name']
            metric_values = metric_data['values']
            insights.add_metric(metric_name, metric_values)
            logger.debug(f"Added metric {metric_name} with {len(metric_values)} data points")
        
        logger.info(f"Fetched {len(insights.metrics)} metrics for Instagram account {ig_business_id}")
        return insights
    
    def get_consolidated_metrics(
        self, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> ConsolidatedMetrics:
        """
        Get consolidated metrics for all accounts.
        
        Args:
            start_date (str, optional): Start date in YYYY-MM-DD format.
            end_date (str, optional): End date in YYYY-MM-DD format.
                
        Returns:
            ConsolidatedMetrics: Consolidated metrics for all accounts.
        """
        start_date, end_date = get_date_range(start_date, end_date)
        
        logger.info(f"Fetching consolidated metrics from {start_date} to {end_date}")
        
        accounts = self.get_connected_accounts()
        consolidated = ConsolidatedMetrics()
        
        for fb_page in accounts.facebook_pages:
            insights = self.get_facebook_insights(fb_page.id, start_date, end_date)
            
            if insights and insights.metrics:
                metrics = insights.metrics
                views = metrics.get('page_impressions', metrics.get('page_views', None))
                reach = metrics.get('page_impressions_unique', None)
                likes = metrics.get('page_actions_post_reactions_like_total', None)
                follows = metrics.get('page_fans', None)
                
                consolidated.add_account_data(
                    account_id=fb_page.id,
                    name=fb_page.name,
                    account_type='Facebook Page',
                    views=views.total if views else 0,
                    reach=reach.total if reach else 0,
                    likes=likes.total if likes else 0,
                    follows=follows.total if follows else 0
                )
                logger.debug(f"Added Facebook Page metrics for {fb_page.name}")
        
        for ig_account in accounts.instagram_accounts:
            insights = self.get_instagram_insights(ig_account.id, start_date, end_date)
            
            if insights and insights.metrics:
                metrics = insights.metrics
                views = metrics.get('impressions', None)
                reach = metrics.get('reach', None)
                follows = metrics.get('follower_count', None)
                
                consolidated.add_account_data(
                    account_id=ig_account.id,
                    name=ig_account.username,
                    account_type='Instagram',
                    views=views.total if views else 0,
                    reach=reach.total if reach else 0,
                    follows=follows.total if follows else 0
                )
                logger.debug(f"Added Instagram metrics for {ig_account.username}")
        
        logger.info(f"Consolidated metrics for {len(consolidated.accounts)} accounts")
        return consolidated
    
    def get_top_posts(
        self, 
        account_id: str, 
        account_type: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None, 
        limit: int = 10
    ) -> List[Post]:
        """
        Get top posts for a specific account.
        
        Args:
            account_id (str): Account ID.
            account_type (str): Account type ('Facebook Page' or 'Instagram').
            start_date (str, optional): Start date in YYYY-MM-DD format.
            end_date (str, optional): End date in YYYY-MM-DD format.
            limit (int, optional): Maximum number of posts to return.
                
        Returns:
            list: List of top posts.
        """
        start_date, end_date = get_date_range(start_date, end_date)
        
        logger.info(f"Fetching top posts for {account_type} {account_id} from {start_date} to {end_date}")
        
        posts = []
        
        if account_type == 'Facebook Page':
            # Get posts with insights
            params = {
                'fields': 'id,message,created_time,insights.metric(post_impressions,post_impressions_unique,post_reactions_by_type_total)',
                'limit': 100,  # Get more posts to find the top ones
                'since': start_date,
                'until': end_date
            }
            
            with LogPerformance(logger, f"Fetching Facebook posts for {account_id}"):
                posts_response = self.api.make_request(f"{account_id}/posts", params)
            
            if not posts_response or 'data' not in posts_response:
                logger.warning(f"No posts found for Facebook Page {account_id}")
                return []
            
            # Process posts
            for post_data in posts_response['data']:
                post = Post(
                    id=post_data.get('id'),
                    account_id=account_id,
                    platform='Facebook',
                    message=post_data.get('message', ''),
                    created_time=post_data.get('created_time')
                )
                
                # Process insights
                if 'insights' in post_data and 'data' in post_data['insights']:
                    for metric in post_data['insights']['data']:
                        if metric['name'] == 'post_impressions':
                            post.insights['views'] = metric['values'][0]['value']
                        elif metric['name'] == 'post_impressions_unique':
                            post.insights['reach'] = metric['values'][0]['value']
                        elif metric['name'] == 'post_reactions_by_type_total':
                            post.insights['likes'] = metric['values'][0]['value'].get('like', 0)
                
                posts.append(post)
            
            logger.debug(f"Processed {len(posts)} Facebook posts")
            
        elif account_type == 'Instagram':
            # Get Instagram media with insights
            params = {
                'fields': 'id,caption,media_type,permalink,timestamp,insights.metric(impressions,reach,engagement)',
                'limit': 100,
                'since': start_date,
                'until': end_date
            }
            
            with LogPerformance(logger, f"Fetching Instagram media for {account_id}"):
                media_response = self.api.make_request(f"{account_id}/media", params)
            
            if not media_response or 'data' not in media_response:
                logger.warning(f"No media found for Instagram account {account_id}")
                return []
            
            # Process media
            for media_data in media_response['data']:
                post = Post(
                    id=media_data.get('id'),
                    account_id=account_id,
                    platform='Instagram',
                    message=media_data.get('caption', ''),
                    created_time=media_data.get('timestamp'),
                    permalink=media_data.get('permalink'),
                    media_type=media_data.get('media_type')
                )
                
                # Process insights
                if 'insights' in media_data and 'data' in media_data['insights']:
                    for metric in media_data['insights']['data']:
                        if metric['name'] == 'impressions':
                            post.insights['impressions'] = metric['values'][0]['value']
                        elif metric['name'] == 'reach':
                            post.insights['reach'] = metric['values'][0]['value']
                        elif metric['name'] == 'engagement':
                            post.insights['engagement'] = metric['values'][0]['value']
                
                posts.append(post)
            
            logger.debug(f"Processed {len(posts)} Instagram posts")
        
        # Sort by views/impressions (can change the sorting criteria)
        posts.sort(
            key=lambda x: (
                x.insights.get('views', 0) + 
                x.insights.get('impressions', 0)
            ), 
            reverse=True
        )
        
        logger.info(f"Retrieved {min(limit, len(posts))} top posts out of {len(posts)} total posts")
        return posts[:limit]
    
    def get_demographic_breakdown(
        self, 
        account_id: str, 
        account_type: str
    ) -> Optional[Demographics]:
        """
        Get demographic breakdown of the audience.
        
        Args:
            account_id (str): Account ID.
            account_type (str): Account type ('Facebook Page' or 'Instagram').
                
        Returns:
            Demographics or None: Demographic data for the account.
        """
        logger.info(f"Fetching demographic breakdown for {account_type} {account_id}")
        
        demographics = Demographics(account_id=account_id)
        
        if account_type == 'Facebook Page':
            # Get age and gender breakdown
            with LogPerformance(logger, f"Fetching Facebook age/gender demographics for {account_id}"):
                age_gender_response = self.api.make_request(f"{account_id}/insights", {
                    'metric': 'page_fans_gender_age',
                    'period': 'lifetime'
                })
            
            # Get location breakdown
            with LogPerformance(logger, f"Fetching Facebook location demographics for {account_id}"):
                location_response = self.api.make_request(f"{account_id}/insights", {
                    'metric': 'page_fans_country',
                    'period': 'lifetime'
                })
            
            # Process age/gender data
            if age_gender_response and 'data' in age_gender_response:
                for item in age_gender_response['data']:
                    if item['name'] == 'page_fans_gender_age':
                        demographics.age_gender = item['values'][0]['value']
                        logger.debug(f"Added {len(demographics.age_gender)} age/gender segments")
            
            # Process location data
            if location_response and 'data' in location_response:
                for item in location_response['data']:
                    if item['name'] == 'page_fans_country':
                        demographics.location = item['values'][0]['value']
                        logger.debug(f"Added {len(demographics.location)} countries")
            
        elif account_type == 'Instagram':
            # Get Instagram audience demographics
            with LogPerformance(logger, f"Fetching Instagram demographics for {account_id}"):
                audience_response = self.api.make_request(f"{account_id}/insights", {
                    'metric': 'audience_gender_age,audience_country',
                    'period': 'lifetime'
                })
            
            if audience_response and 'data' in audience_response:
                for item in audience_response['data']:
                    if item['name'] == 'audience_gender_age':
                        demographics.age_gender = item['values'][0]['value']
                        logger.debug(f"Added {len(demographics.age_gender)} age/gender segments")
                    elif item['name'] == 'audience_country':
                        demographics.location = item['values'][0]['value']
                        logger.debug(f"Added {len(demographics.location)} countries")
        
        if not demographics.age_gender and not demographics.location:
            logger.warning(f"No demographic data found for {account_type} {account_id}")
            return None
        
        logger.info(f"Retrieved demographic data with {len(demographics.age_gender)} age/gender segments and {len(demographics.location)} countries")
        return demographics
    
    def get_facebook_ads_data(
        self, 
        ad_account_id: Optional[str] = None, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> List[AdData]:
        """
        Get Facebook Ads data including account, campaign, reach, impressions, cost per result, amount spent, etc.
        
        Args:
            ad_account_id (str, optional): Ad Account ID. If not provided, will fetch data for all ad accounts.
            start_date (str, optional): Start date in YYYY-MM-DD format.
            end_date (str, optional): End date in YYYY-MM-DD format.
                
        Returns:
            list: List of ad data objects.
        """
        start_date, end_date = get_date_range(start_date, end_date)
        
        logger.info(f"Fetching Facebook Ads data from {start_date} to {end_date}")
        
        # If no ad account ID provided, get all ad accounts
        if not ad_account_id:
            with LogPerformance(logger, "Fetching all ad accounts"):
                ad_accounts_response = self.api.make_request('me/adaccounts')
            
            if not ad_accounts_response or 'data' not in ad_accounts_response:
                logger.warning("No ad accounts found")
                return []
            
            ad_accounts = [account['id'] for account in ad_accounts_response['data']]
        else:
            ad_accounts = [ad_account_id]
        
        all_ads_data = []
        
        for account_id in ad_accounts:
            logger.info(f"Processing ad account {account_id}")
            
            # Get campaigns data
            params = {
                'fields': 'name,objective,status',
                'time_range': json.dumps({
                    'since': start_date,
                    'until': end_date
                }),
                'limit': 100
            }
            
            with LogPerformance(logger, f"Fetching campaigns for ad account {account_id}"):
                campaigns_response = self.api.make_request(f"{account_id}/campaigns", params)
            
            if not campaigns_response or 'data' not in campaigns_response:
                logger.warning(f"No campaigns found for ad account {account_id}")
                continue
            
            logger.info(f"Found {len(campaigns_response['data'])} campaigns for ad account {account_id}")
            
            for campaign in campaigns_response['data']:
                campaign_id = campaign['id']
                campaign_name = campaign['name']
                
                # Get insights for this campaign
                insights_params = {
                    'fields': 'campaign_name,reach,impressions,cost_per_result_type,spend,device_platform,region,age,gender',
                    'time_range': json.dumps({
                        'since': start_date,
                        'until': end_date
                    }),
                    'breakdowns': 'region,device_platform,age,gender',
                    'level': 'campaign'
                }
                
                with LogPerformance(logger, f"Fetching insights for campaign {campaign_id}"):
                    insights_response = self.api.make_request(f"{campaign_id}/insights", insights_params)
                
                if not insights_response or 'data' not in insights_response:
                    logger.warning(f"No insights found for campaign {campaign_id}")
                    continue
                
                logger.info(f"Found {len(insights_response['data'])} insight entries for campaign {campaign_id}")
                
                for insight in insights_response['data']:
                    ad_data = AdData(
                        account_id=account_id,
                        campaign_id=campaign_id,
                        campaign_name=campaign_name,
                        reach=int(insight.get('reach', 0)),
                        impressions=int(insight.get('impressions', 0)),
                        cost_per_result=float(insight.get('cost_per_result_type', 0)),
                        amount_spent=float(insight.get('spend', 0)),
                        region=insight.get('region', 'Unknown'),
                        platform_device=insight.get('device_platform', 'Unknown'),
                        age=insight.get('age', 'Unknown'),
                        gender=insight.get('gender', 'Unknown')
                    )
                    
                    all_ads_data.append(ad_data)
        
        logger.info(f"Retrieved a total of {len(all_ads_data)} ad data records")
        return all_ads_data
