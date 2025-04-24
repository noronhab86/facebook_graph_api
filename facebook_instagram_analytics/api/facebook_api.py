"""
Facebook Graph API client for Facebook Instagram Analytics.
Handles API requests and error handling.
"""

import json
import time
import requests
from typing import Dict, Any, Optional, List, Union

from facebook_instagram_analytics.config import (
    FACEBOOK_ACCESS_TOKEN, 
    FACEBOOK_BASE_URL,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY
)
from facebook_instagram_analytics.utils.logging_utils import get_logger, LogPerformance

# Initialize logger
logger = get_logger(__name__)


class FacebookGraphAPI:
    """Client for the Facebook Graph API."""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the Facebook Graph API client.
        
        Args:
            access_token (str, optional): Facebook API access token.
                If not provided, will use the token from environment variables.
        
        Raises:
            ValueError: If no access token is provided or available.
        """
        self.access_token = access_token or FACEBOOK_ACCESS_TOKEN
        if not self.access_token:
            logger.error("No Facebook access token provided")
            raise ValueError(
                "Facebook access token is required. Please provide it or set "
                "FACEBOOK_ACCESS_TOKEN in your .env file."
            )
        
        self.base_url = FACEBOOK_BASE_URL
        logger.info(f"Initialized Facebook Graph API client with API version {self.base_url.split('/')[-1]}")
    
    def make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        method: str = 'GET',
        timeout: int = REQUEST_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        retry_delay: int = RETRY_DELAY
    ) -> Optional[Dict[str, Any]]:
        """
        Make a request to the Facebook Graph API with retry logic.
        
        Args:
            endpoint (str): API endpoint to request.
            params (dict, optional): Request parameters.
            method (str, optional): HTTP method (GET, POST).
            timeout (int, optional): Request timeout in seconds.
            max_retries (int, optional): Maximum number of retries for failed requests.
            retry_delay (int, optional): Delay between retries in seconds.
            
        Returns:
            dict or None: API response as a dictionary, or None if request failed.
        """
        if params is None:
            params = {}
        
        # Add access token to parameters
        params['access_token'] = self.access_token
        
        url = f"{self.base_url}/{endpoint}"
        logger.debug(f"Making {method} request to {endpoint}")
        
        retries = 0
        while retries <= max_retries:
            try:
                with LogPerformance(logger, f"API request to {endpoint}"):
                    if method.upper() == 'GET':
                        response = requests.get(url, params=params, timeout=timeout)
                    elif method.upper() == 'POST':
                        response = requests.post(url, json=params, timeout=timeout)
                    else:
                        logger.error(f"Unsupported HTTP method: {method}")
                        return None
                
                # Check for API errors
                if response.status_code != 200:
                    error_info = response.json() if response.text else {"message": "Unknown error"}
                    logger.error(
                        f"API error {response.status_code} for {endpoint}: "
                        f"{error_info.get('message', 'Unknown error')}"
                    )
                    
                    # Check if error is rate-limiting related
                    if response.status_code == 429 or 'rate limit' in str(error_info).lower():
                        wait_time = retry_delay * (2 ** retries)  # Exponential backoff
                        logger.warning(f"Rate limit hit, waiting {wait_time} seconds")
                        time.sleep(wait_time)
                        retries += 1
                        continue
                    
                    return None
                
                # Parse and return JSON response
                result = response.json()
                logger.debug(f"Successful API response from {endpoint}")
                return result
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request to {endpoint} timed out (attempt {retries+1}/{max_retries+1})")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error for {endpoint} (attempt {retries+1}/{max_retries+1})")
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response from {endpoint}: {response.text[:100]}...")
                return None
            except Exception as e:
                logger.error(f"Unexpected error for {endpoint}: {str(e)}")
                return None
            
            # Retry logic
            if retries < max_retries:
                wait_time = retry_delay * (2 ** retries)  # Exponential backoff
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1
            else:
                logger.error(f"Max retries ({max_retries}) reached for {endpoint}")
                return None
        
        return None
    
    def get_paginated_results(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        results_key: str = 'data'
    ) -> List[Dict[str, Any]]:
        """
        Get paginated results from the Facebook Graph API.
        
        Args:
            endpoint (str): API endpoint to request.
            params (dict, optional): Request parameters.
            limit (int, optional): Number of items per page.
            results_key (str, optional): Key in response that contains the results.
            
        Returns:
            list: Combined list of all results across pages.
        """
        if params is None:
            params = {}
        
        params['limit'] = limit
        
        all_results = []
        next_page_url = None
        
        with LogPerformance(logger, f"Paginated request to {endpoint}"):
            while True:
                if next_page_url:
                    # Remove base URL to get just the endpoint and parameters
                    relative_url = next_page_url.replace(self.base_url + '/', '')
                    # Split endpoint and parameters
                    parts = relative_url.split('?')
                    if len(parts) > 1:
                        endpoint = parts[0]
                        # Parse parameters from URL
                        params = {}
                        for param in parts[1].split('&'):
                            key, value = param.split('=')
                            params[key] = value
                
                response = self.make_request(endpoint, params)
                
                if not response or results_key not in response:
                    break
                
                # Add current page results
                all_results.extend(response[results_key])
                logger.debug(f"Retrieved {len(response[results_key])} items from {endpoint}")
                
                # Check for next page
                if 'paging' in response and 'next' in response['paging']:
                    next_page_url = response['paging']['next']
                else:
                    break
        
        logger.info(f"Retrieved a total of {len(all_results)} items from {endpoint}")
        return all_results
