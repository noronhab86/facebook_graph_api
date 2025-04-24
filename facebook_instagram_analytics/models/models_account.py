"""
Account model for Facebook and Instagram accounts.
Defines data structures for social media accounts.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class SocialMediaAccount:
    """Base class for social media accounts."""
    
    id: str
    name: str
    account_type: str
    category: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert account to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'account_type': self.account_type,
            'category': self.category,
            **self.additional_data
        }


@dataclass
class FacebookPage(SocialMediaAccount):
    """Facebook Page account."""
    
    def __init__(
        self, 
        id: str, 
        name: str, 
        category: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            id=id,
            name=name,
            account_type="Facebook Page",
            category=category,
            additional_data=kwargs
        )
    
    @property
    def page_id(self) -> str:
        """Get the Facebook Page ID."""
        return self.id


@dataclass
class InstagramAccount(SocialMediaAccount):
    """Instagram Business account."""
    
    def __init__(
        self, 
        id: str, 
        username: str, 
        category: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            id=id,
            name=username,
            account_type="Instagram",
            category=category or "Instagram Business Account",
            additional_data=kwargs
        )
    
    @property
    def instagram_id(self) -> str:
        """Get the Instagram account ID."""
        return self.id
    
    @property
    def username(self) -> str:
        """Get the Instagram username."""
        return self.name


@dataclass
class AdAccount(SocialMediaAccount):
    """Facebook Ads account."""
    
    def __init__(
        self, 
        id: str, 
        name: str, 
        **kwargs
    ):
        super().__init__(
            id=id,
            name=name,
            account_type="Ad Account",
            category="Facebook Ads",
            additional_data=kwargs
        )
    
    @property
    def ad_account_id(self) -> str:
        """Get the Ad Account ID."""
        return self.id


@dataclass
class AccountCollection:
    """Collection of social media accounts."""
    
    facebook_pages: List[FacebookPage] = field(default_factory=list)
    instagram_accounts: List[InstagramAccount] = field(default_factory=list)
    ad_accounts: List[AdAccount] = field(default_factory=list)
    
    def add_account(self, account: SocialMediaAccount) -> None:
        """Add an account to the appropriate collection."""
        if isinstance(account, FacebookPage):
            self.facebook_pages.append(account)
        elif isinstance(account, InstagramAccount):
            self.instagram_accounts.append(account)
        elif isinstance(account, AdAccount):
            self.ad_accounts.append(account)
        else:
            raise ValueError(f"Unsupported account type: {type(account)}")
    
    def get_all_accounts(self) -> List[SocialMediaAccount]:
        """Get all accounts in the collection."""
        return self.facebook_pages + self.instagram_accounts + self.ad_accounts
    
    def find_by_id(self, account_id: str) -> Optional[SocialMediaAccount]:
        """Find an account by ID."""
        for account in self.get_all_accounts():
            if account.id == account_id:
                return account
        return None
    
    def to_list_of_dicts(self) -> List[Dict[str, Any]]:
        """Convert all accounts to list of dictionaries."""
        return [account.to_dict() for account in self.get_all_accounts()]