"""
Analytics models for Facebook API.

This module contains data models for analytics and insights data from
Facebook and Instagram. These models provide structured access to
performance metrics and analytics data.
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
    description: Optional[str] = None
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
            'description': self.description,
            'values': [v.to_dict() for v in self.values],
            'total': self.total,
            'average': self.average
        }


@dataclass
class InsightPeriod:
    """Represents the period for an insight (day, week, month, lifetime)."""
    
    period: str  # 'day', 'week', 'month', or 'lifetime'
    values: List[Dict[str, Any]]  # Raw values from the API
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'period': self.period,
            'values': self.values
        }


@dataclass
class Insight:
    """Represents a Facebook insight with its periods and values."""
    
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    periods: Dict[str, InsightPeriod] = field(default_factory=dict)
    
    def add_period(self, period: str, values: List[Dict[str, Any]]) -> None:
        """Add a period to the insight."""
        self.periods[period] = InsightPeriod(period=period, values=values)
    
    def get_period(self, period: str) -> Optional[InsightPeriod]:
        """Get a specific period by name."""
        return self.periods.get(period)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'title': self.title,
            'description': self.description,
            'periods': {period: period_data.to_dict() for period, period_data in self.periods.items()}
        }


@dataclass
class PageInsights:
    """Collection of insights for a Facebook Page."""
    
    page_id: str
    insights: Dict[str, Insight] = field(default_factory=dict)
    
    def add_insight(self, name: str, title: Optional[str] = None, description: Optional[str] = None) -> Insight:
        """Add an insight to the collection."""
        insight = Insight(name=name, title=title, description=description)
        self.insights[name] = insight
        return insight
    
    def get_insight(self, name: str) -> Optional[Insight]:
        """Get a specific insight by name."""
        return self.insights.get(name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'page_id': self.page_id,
            'insights': {name: insight.to_dict() for name, insight in self.insights.items()}
        }


@dataclass
class PostInsights:
    """Collection of insights for a Facebook Post."""
    
    post_id: str
    insights: Dict[str, Insight] = field(default_factory=dict)
    
    def add_insight(self, name: str, title: Optional[str] = None, description: Optional[str] = None) -> Insight:
        """Add an insight to the collection."""
        insight = Insight(name=name, title=title, description=description)
        self.insights[name] = insight
        return insight
    
    def get_insight(self, name: str) -> Optional[Insight]:
        """Get a specific insight by name."""
        return self.insights.get(name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'post_id': self.post_id,
            'insights': {name: insight.to_dict() for name, insight in self.insights.items()}
        }


@dataclass
class InstagramInsights:
    """Collection of insights for an Instagram Business Account."""
    
    account_id: str
    insights: Dict[str, Insight] = field(default_factory=dict)
    
    def add_insight(self, name: str, title: Optional[str] = None, description: Optional[str] = None) -> Insight:
        """Add an insight to the collection."""
        insight = Insight(name=name, title=title, description=description)
        self.insights[name] = insight
        return insight
    
    def get_insight(self, name: str) -> Optional[Insight]:
        """Get a specific insight by name."""
        return self.insights.get(name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'account_id': self.account_id,
            'insights': {name: insight.to_dict() for name, insight in self.insights.items()}
        }


@dataclass
class Demographics:
    """Demographic data for an account's audience."""
    
    account_id: str
    account_type: str  # 'facebook_page' or 'instagram_account'
    age_gender: Dict[str, Union[int, float]] = field(default_factory=dict)
    location: Dict[str, Union[int, float]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'account_id': self.account_id,
            'account_type': self.account_type,
            'age_gender': self.age_gender,
            'location': self.location
        }


@dataclass
class ConsolidatedMetrics:
    """Consolidated metrics for a set of accounts."""
    
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
        
        platform = 'facebook' if account_type == 'facebook_page' else 'instagram'
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
