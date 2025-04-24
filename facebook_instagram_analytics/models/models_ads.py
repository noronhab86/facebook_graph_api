"""
Ad models for Facebook API.

This module contains data models for Facebook Ads entities and insights.
These models provide structured access to ads data and performance metrics.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from enum import Enum


class CampaignObjective(Enum):
    """Facebook Ad Campaign Objectives."""
    
    BRAND_AWARENESS = "BRAND_AWARENESS"
    REACH = "REACH"
    TRAFFIC = "TRAFFIC"
    ENGAGEMENT = "ENGAGEMENT"
    APP_INSTALLS = "APP_INSTALLS"
    VIDEO_VIEWS = "VIDEO_VIEWS"
    LEAD_GENERATION = "LEAD_GENERATION"
    MESSAGES = "MESSAGES"
    CONVERSIONS = "CONVERSIONS"
    CATALOG_SALES = "CATALOG_SALES"
    STORE_TRAFFIC = "STORE_TRAFFIC"


class CampaignStatus(Enum):
    """Facebook Ad Campaign Statuses."""
    
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DELETED = "DELETED"
    ARCHIVED = "ARCHIVED"


class AdSetOptimizationGoal(Enum):
    """Facebook Ad Set Optimization Goals."""
    
    NONE = "NONE"
    APP_INSTALLS = "APP_INSTALLS"
    BRAND_AWARENESS = "BRAND_AWARENESS"
    AD_RECALL_LIFT = "AD_RECALL_LIFT"
    CLICKS = "CLICKS"
    ENGAGED_USERS = "ENGAGED_USERS"
    EVENT_RESPONSES = "EVENT_RESPONSES"
    IMPRESSIONS = "IMPRESSIONS"
    LEAD_GENERATION = "LEAD_GENERATION"
    QUALITY_LEAD = "QUALITY_LEAD"
    LINK_CLICKS = "LINK_CLICKS"
    OFFER_CLAIMS = "OFFER_CLAIMS"
    OFFSITE_CONVERSIONS = "OFFSITE_CONVERSIONS"
    PAGE_ENGAGEMENT = "PAGE_ENGAGEMENT"
    PAGE_LIKES = "PAGE_LIKES"
    POST_ENGAGEMENT = "POST_ENGAGEMENT"
    REACH = "REACH"
    SOCIAL_IMPRESSIONS = "SOCIAL_IMPRESSIONS"
    VIDEO_VIEWS = "VIDEO_VIEWS"
    APP_DOWNLOADS = "APP_DOWNLOADS"
    LANDING_PAGE_VIEWS = "LANDING_PAGE_VIEWS"
    VALUE = "VALUE"
    THRUPLAY = "THRUPLAY"
    REPLIES = "REPLIES"


@dataclass
class AdAccount:
    """Facebook Ad Account."""
    
    id: str
    name: Optional[str] = None
    currency: Optional[str] = None
    timezone_id: Optional[int] = None
    timezone_name: Optional[str] = None
    business_id: Optional[str] = None
    business_name: Optional[str] = None
    account_status: int = 1  # 1: active, 2: disabled, 3: unsettled, 7: pending_risk_review, 9: in_grace_period, 100: pending_closure, 101: closed, 102: pending_settlement, 201: any_active, 202: any_closed
    disable_reason: Optional[int] = None  # 0: NONE, 1: SUSPICIOUS_ACTIVITY, 2: POLICY_VIOLATION, 3: TOO_MANY_CHARGEBACKS, 4: TOO_MANY_MANUAL_REFUNDS, 5: TOO_MANY_MANUAL_REFUNDS_AND_CHARGEBACKS
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def account_id(self) -> str:
        """Get the account ID without the 'act_' prefix."""
        return self.id.replace('act_', '') if self.id.startswith('act_') else self.id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'account_id': self.account_id,
            'name': self.name,
            'currency': self.currency,
            'timezone_id': self.timezone_id,
            'timezone_name': self.timezone_name,
            'business_id': self.business_id,
            'business_name': self.business_name,
            'account_status': self.account_status,
            'disable_reason': self.disable_reason,
            **self.additional_data
        }


@dataclass
class Campaign:
    """Facebook Ad Campaign."""
    
    id: str
    name: str
    account_id: str
    objective: Optional[CampaignObjective] = None
    status: CampaignStatus = CampaignStatus.PAUSED
    buying_type: Optional[str] = None
    spend_cap: Optional[float] = None
    daily_budget: Optional[float] = None
    lifetime_budget: Optional[float] = None
    created_time: Optional[Union[str, datetime]] = None
    start_time: Optional[Union[str, datetime]] = None
    stop_time: Optional[Union[str, datetime]] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Process after initialization."""
        # Convert string dates to datetime objects
        for date_field in ['created_time', 'start_time', 'stop_time']:
            value = getattr(self, date_field)
            if isinstance(value, str):
                try:
                    if 'T' in value:  # ISO format
                        setattr(self, date_field, datetime.fromisoformat(value.replace('Z', '+00:00')))
                    else:
                        setattr(self, date_field, datetime.strptime(value, "%Y-%m-%d"))
                except ValueError:
                    pass  # Keep as string if parsing fails
        
        # Convert string objective to enum
        if isinstance(self.objective, str):
            try:
                self.objective = CampaignObjective(self.objective)
            except ValueError:
                pass  # Keep as string if not in enum
        
        # Convert string status to enum
        if isinstance(self.status, str):
            try:
                self.status = CampaignStatus(self.status)
            except ValueError:
                pass  # Keep as string if not in enum
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'account_id': self.account_id,
            'objective': self.objective.value if isinstance(self.objective, CampaignObjective) else self.objective,
            'status': self.status.value if isinstance(self.status, CampaignStatus) else self.status,
            'buying_type': self.buying_type,
            'spend_cap': self.spend_cap,
            'daily_budget': self.daily_budget,
            'lifetime_budget': self.lifetime_budget,
            'created_time': self.created_time.isoformat() if isinstance(self.created_time, datetime) else self.created_time,
            'start_time': self.start_time.isoformat() if isinstance(self.start_time, datetime) else self.start_time,
            'stop_time': self.stop_time.isoformat() if isinstance(self.stop_time, datetime) else self.stop_time,
            **self.additional_data
        }


@dataclass
class AdSet:
    """Facebook Ad Set."""
    
    id: str
    name: str
    campaign_id: str
    account_id: str
    status: CampaignStatus = CampaignStatus.PAUSED
    optimization_goal: Optional[AdSetOptimizationGoal] = None
    bid_amount: Optional[int] = None
    bid_strategy: Optional[str] = None
    daily_budget: Optional[float] = None
    lifetime_budget: Optional[float] = None
    targeting: Optional[Dict[str, Any]] = None
    created_time: Optional[Union[str, datetime]] = None
    start_time: Optional[Union[str, datetime]] = None
    end_time: Optional[Union[str, datetime]] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Process after initialization."""
        # Convert string dates to datetime objects
        for date_field in ['created_time', 'start_time', 'end_time']:
            value = getattr(self, date_field)
            if isinstance(value, str):
                try:
                    if 'T' in value:  # ISO format
                        setattr(self, date_field, datetime.fromisoformat(value.replace('Z', '+00:00')))
                    else:
                        setattr(self, date_field, datetime.strptime(value, "%Y-%m-%d"))
                except ValueError:
                    pass  # Keep as string if parsing fails
        
        # Convert string status to enum
        if isinstance(self.status, str):
            try:
                self.status = CampaignStatus(self.status)
            except ValueError:
                pass  # Keep as string if not in enum
        
        # Convert string optimization_goal to enum
        if isinstance(self.optimization_goal, str):
            try:
                self.optimization_goal = AdSetOptimizationGoal(self.optimization_goal)
            except ValueError:
                pass  # Keep as string if not in enum
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'campaign_id': self.campaign_id,
            'account_id': self.account_id,
            'status': self.status.value if isinstance(self.status, CampaignStatus) else self.status,
            'optimization_goal': self.optimization_goal.value if isinstance(self.optimization_goal, AdSetOptimizationGoal) else self.optimization_goal,
            'bid_amount': self.bid_amount,
            'bid_strategy': self.bid_strategy,
            'daily_budget': self.daily_budget,
            'lifetime_budget': self.lifetime_budget,
            'targeting': self.targeting,
            'created_time': self.created_time.isoformat() if isinstance(self.created_time, datetime) else self.created_time,
            'start_time': self.start_time.isoformat() if isinstance(self.start_time, datetime) else self.start_time,
            'end_time': self.end_time.isoformat() if isinstance(self.end_time, datetime) else self.end_time,
            **self.additional_data
        }


@dataclass
class Ad:
    """Facebook Ad."""
    
    id: str
    name: str
    adset_id: str
    campaign_id: str
    account_id: str
    status: CampaignStatus = CampaignStatus.PAUSED
    creative: Optional[Dict[str, Any]] = None
    created_time: Optional[Union[str, datetime]] = None
    updated_time: Optional[Union[str, datetime]] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Process after initialization."""
        # Convert string dates to datetime objects
        for date_field in ['created_time', 'updated_time']:
            value = getattr(self, date_field)
            if isinstance(value, str):
                try:
                    if 'T' in value:  # ISO format
                        setattr(self, date_field, datetime.fromisoformat(value.replace('Z', '+00:00')))
                    else:
                        setattr(self, date_field, datetime.strptime(value, "%Y-%m-%d"))
                except ValueError:
                    pass  # Keep as string if parsing fails
        
        # Convert string status to enum
        if isinstance(self.status, str):
            try:
                self.status = CampaignStatus(self.status)
            except ValueError:
                pass  # Keep as string if not in enum
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'adset_id': self.adset_id,
            'campaign_id': self.campaign_id,
            'account_id': self.account_id,
            'status': self.status.value if isinstance(self.status, CampaignStatus) else self.status,
            'creative': self.creative,
            'created_time': self.created_time.isoformat() if isinstance(self.created_time, datetime) else self.created_time,
            'updated_time': self.updated_time.isoformat() if isinstance(self.updated_time, datetime) else self.updated_time,
            **self.additional_data
        }


@dataclass
class AdCreative:
    """Facebook Ad Creative."""
    
    id: str
    name: Optional[str] = None
    object_story_spec: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    body: Optional[str] = None
    title: Optional[str] = None
    link_url: Optional[str] = None
    app_link: Optional[str] = None
    call_to_action_type: Optional[str] = None
    image_hash: Optional[str] = None
    video_id: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'object_story_spec': self.object_story_spec,
            'image_url': self.image_url,
            'body': self.body,
            'title': self.title,
            'link_url': self.link_url,
            'app_link': self.app_link,
            'call_to_action_type': self.call_to_action_type,
            'image_hash': self.image_hash,
            'video_id': self.video_id,
            **self.additional_data
        }


@dataclass
class AdInsight:
    """Facebook Ad Insight (performance metrics)."""
    
    ad_id: Optional[str] = None
    adset_id: Optional[str] = None
    campaign_id: Optional[str] = None
    account_id: Optional[str] = None
    date_start: Optional[Union[str, datetime, date]] = None
    date_stop: Optional[Union[str, datetime, date]] = None
    impressions: int = 0
    reach: int = 0
    frequency: float = 0.0
    clicks: int = 0
    unique_clicks: int = 0
    ctr: float = 0.0
    spend: float = 0.0
    cpm: float = 0.0
    cpp: float = 0.0
    cpc: float = 0.0
    actions: Dict[str, int] = field(default_factory=dict)
    conversions: Dict[str, int] = field(default_factory=dict)
    video_p25_watched_actions: int = 0
    video_p50_watched_actions: int = 0
    video_p75_watched_actions: int = 0
    video_p100_watched_actions: int = 0
    additional_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Process after initialization."""
        # Convert string dates to date objects
        for date_field in ['date_start', 'date_stop']:
            value = getattr(self, date_field)
            if isinstance(value, str):
                try:
                    if 'T' in value:  # ISO format with time
                        setattr(self, date_field, datetime.fromisoformat(value.replace('Z', '+00:00')).date())
                    else:
                        setattr(self, date_field, datetime.strptime(value, "%Y-%m-%d").date())
                except ValueError:
                    pass  # Keep as string if parsing fails
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            'ad_id': self.ad_id,
            'adset_id': self.adset_id,
            'campaign_id': self.campaign_id,
            'account_id': self.account_id,
            'date_start': self.date_start.isoformat() if isinstance(self.date_start, (datetime, date)) else self.date_start,
            'date_stop': self.date_stop.isoformat() if isinstance(self.date_stop, (datetime, date)) else self.date_stop,
            'impressions': self.impressions,
            'reach': self.reach,
            'frequency': self.frequency,
            'clicks': self.clicks,
            'unique_clicks': self.unique_clicks,
            'ctr': self.ctr,
            'spend': self.spend,
            'cpm': self.cpm,
            'cpp': self.cpp,
            'cpc': self.cpc,
            'actions': self.actions,
            'conversions': self.conversions,
            'video_p25_watched_actions': self.video_p25_watched_actions,
            'video_p50_watched_actions': self.video_p50_watched_actions,
            'video_p75_watched_actions': self.video_p75_watched_actions,
            'video_p100_watched_actions': self.video_p100_watched_actions,
            **self.additional_metrics
        }
        
        # Remove None values
        return {k: v for k, v in result.items() if v is not None}
