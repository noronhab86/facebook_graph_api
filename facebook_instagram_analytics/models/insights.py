"""
Insights model for Facebook and Instagram analytics data.
Defines data structures for social media metrics and insights.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date


@dataclass
class MetricValue:
    """Value for a specific metric, with date and value."""
    
    date: Union[str, datetime, date]
    value: Union[int, float]
    
    def __post_init__(self):
        """Convert string date to datetime."""
        if isinstance(self.date, str):
            self.date = datetime.strptime(self.date, "%Y-%m-%d")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'date': self.date.strftime("%Y-%m-%d") if isinstance(self.date, (datetime, date)) else self.date,
            'value': self.value
        }


@dataclass
class Metric:
    """Represents a single metric (e.g., page_impressions) and its values over time."""
    
    name: str
    values: List[MetricValue] = field(default_factory=list)
    
    @property
    def total(self) -> Union[int, float]:
        """Calculate the total of all values."""
        return sum(v.value for v in self.values)
    
    @property
    def average(self) -> float:
        """Calculate the average of all values."""
        if not self.values:
            return 0.0
        return self.total / len(self.values)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'values': [v.to_dict() for v in self.values],
            'total': self.total,
            'average': self.average
        }


@dataclass
class AccountInsights:
    """Insights for a specific account."""
    
    account_id: str
    metrics: Dict[str, Metric] = field(default_factory=dict)
    
    def add_metric(self, name: str, values: List[Dict[str, Any]]) -> None:
        """Add a metric to the insights."""
        metric_values = []
        for value_data in values:
            date_value = value_data.get('end_time', value_data.get('date', ''))
            if isinstance(date_value, str) and 'T' in date_value:
                # Handle Facebook API datetime format (e.g., "2023-01-01T00:00:00+0000")
                date_value = date_value.split('T')[0]
            
            metric_values.append(MetricValue(
                date=date_value,
                value=value_data.get('value', 0)
            ))
        
        self.metrics[name] = Metric(name=name, values=metric_values)
    
    def get_metric(self, name: str) -> Optional[Metric]:
        """Get a specific metric by name."""
        return self.metrics.get(name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'account_id': self.account_id,
            'metrics': {name: metric.to_dict() for name, metric in self.metrics.items()}
        }


@dataclass
class Post:
    """Represents a social media post (Facebook or Instagram)."""
    
    id: str
    account_id: str
    platform: str  # 'Facebook' or 'Instagram'
    message: Optional[str] = None
    created_time: Optional[Union[str, datetime]] = None
    permalink: Optional[str] = None
    media_type: Optional[str] = None
    insights: Dict[str, Union[int, float]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert string created_time to datetime."""
        if isinstance(self.created_time, str):
            # Handle Facebook API datetime format (e.g., "2023-01-01T00:00:00+0000")
            if 'T' in self.created_time:
                self.created_time = datetime.strptime(
                    self.created_time.split('+')[0], 
                    "%Y-%m-%dT%H:%M:%S"
                )
            else:
                self.created_time = datetime.strptime(self.created_time, "%Y-%m-%d")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'account_id': self.account_id,
            'platform': self.platform,
            'message': self.message,
            'created_time': self.created_time.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.created_time, datetime) else self.created_time,
            'permalink': self.permalink,
            'media_type': self.media_type,
            'views': self.insights.get('impressions', self.insights.get('views', 0)),
            'reach': self.insights.get('reach', 0),
            'likes': self.insights.get('likes', self.insights.get('engagement', 0))
        }


@dataclass
class Demographics:
    """Demographic data for an account's audience."""
    
    account_id: str
    age_gender: Dict[str, Union[int, float]] = field(default_factory=dict)
    location: Dict[str, Union[int, float]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'account_id': self.account_id,
            'age_gender': self.age_gender,
            'location': self.location
        }
    
    def to_dataframes(self) -> Dict[str, 'pd.DataFrame']:
        """Convert to pandas DataFrames."""
        import pandas as pd
        
        age_gender_df = pd.DataFrame([
            {'category': k, 'value': v} 
            for k, v in self.age_gender.items()
        ])
        
        location_df = pd.DataFrame([
            {'country': k, 'value': v} 
            for k, v in self.location.items()
        ])
        
        return {
            'age_gender': age_gender_df,
            'location': location_df
        }


@dataclass
class AdData:
    """Data for a Facebook Ad."""
    
    account_id: str
    campaign_id: str
    campaign_name: str
    reach: int = 0
    impressions: int = 0
    cost_per_result: float = 0.0
    amount_spent: float = 0.0
    region: str = "Unknown"
    platform_device: str = "Unknown"
    age: str = "Unknown"
    gender: str = "Unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'account_id': self.account_id,
            'campaign_id': self.campaign_id,
            'campaign_name': self.campaign_name,
            'reach': self.reach,
            'impressions': self.impressions,
            'cost_per_result': self.cost_per_result,
            'amount_spent': self.amount_spent,
            'region': self.region,
            'platform_device': self.platform_device,
            'age': self.age,
            'gender': self.gender
        }


@dataclass
class ConsolidatedMetrics:
    """Consolidated metrics for all accounts."""
    
    facebook: Dict[str, Union[int, float]] = field(default_factory=lambda: {
        'views': 0, 'reach': 0, 'likes': 0, 'follows': 0
    })
    instagram: Dict[str, Union[int, float]] = field(default_factory=lambda: {
        'views': 0, 'reach': 0, 'likes': 0, 'follows': 0
    })
    accounts: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_account_data(
        self, 
        account_id: str, 
        name: str, 
        account_type: str, 
        views: int = 0, 
        reach: int = 0, 
        likes: int = 0, 
        follows: int = 0
    ) -> None:
        """Add account data to consolidated metrics."""
        account_data = {
            'id': account_id,
            'name': name,
            'type': account_type,
            'views': views,
            'reach': reach,
            'likes': likes,
            'follows': follows
        }
        
        platform = 'facebook' if account_type == 'Facebook Page' else 'instagram'
        metrics = getattr(self, platform)
        
        metrics['views'] += views
        metrics['reach'] += reach
        metrics['likes'] += likes
        metrics['follows'] += follows
        
        self.accounts.append(account_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'facebook': self.facebook,
            'instagram': self.instagram,
            'accounts': self.accounts
        }
