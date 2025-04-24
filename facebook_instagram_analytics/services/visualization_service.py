"""
Visualization service for analytics data.
Generates visualizations and charts for analytics data.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Any, Union, Tuple
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environment

from facebook_instagram_analytics.models.insights import ConsolidatedMetrics, Demographics, AdData
from facebook_instagram_analytics.utils.logging_utils import get_logger, LogPerformance
from facebook_instagram_analytics.utils.date_utils import create_filename_timestamp

# Initialize logger
logger = get_logger(__name__)


class VisualizationService:
    """Service for generating visualizations of analytics data."""
    
    def __init__(self, output_dir: str = "visualizations"):
        """
        Initialize the visualization service.
        
        Args:
            output_dir (str, optional): Directory to save visualizations.
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")
        
        logger.info("Initialized Visualization Service")
    
    def generate_metrics_comparison(
        self, 
        metrics: ConsolidatedMetrics, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> str:
        """
        Generate comparison visualizations for Facebook and Instagram metrics.
        
        Args:
            metrics (ConsolidatedMetrics): Consolidated metrics data.
            start_date (str, optional): Start date for the title.
            end_date (str, optional): End date for the title.
            
        Returns:
            str: Path to the saved visualization file.
        """
        logger.info("Generating metrics comparison visualization")
        
        # Create a DataFrame for the metrics
        fb_metrics = metrics.facebook
        ig_metrics = metrics.instagram
        
        metrics_df = pd.DataFrame({
            'Platform': ['Facebook', 'Instagram'],
            'Views': [fb_metrics['views'], ig_metrics['views']],
            'Reach': [fb_metrics['reach'], ig_metrics['reach']],
            'Likes': [fb_metrics['likes'], ig_metrics['likes']],
            'Follows': [fb_metrics['follows'], ig_metrics['follows']]
        })
        
        with LogPerformance(logger, "Creating metrics comparison chart"):
            # Create bar charts in a 2x2 grid
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            
            # Set a title for the entire figure
            title = "Facebook vs Instagram Metrics"
            if start_date and end_date:
                title += f" ({start_date} to {end_date})"
            fig.suptitle(title, fontsize=16)
            
            metrics_to_plot = ['Views', 'Reach', 'Likes', 'Follows']
            positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
            
            for metric, pos in zip(metrics_to_plot, positions):
                ax = axes[pos]
                metrics_df.plot.bar(x='Platform', y=metric, ax=ax, legend=False)
                ax.set_title(metric)
                ax.set_ylabel(metric)
                
                # Add value labels on top of each bar
                for p in ax.patches:
                    value = int(p.get_height())
                    ax.annotate(
                        f"{value:,}",
                        (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom',
                        fontsize=10
                    )
            
            plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to make room for title
            
            # Generate filename with timestamp
            timestamp = create_filename_timestamp()
            filename = f"metrics_comparison_{timestamp}.png"
            if start_date and end_date:
                date_str = f"{start_date}_to_{end_date}".replace("-", "")
                filename = f"metrics_comparison_{date_str}_{timestamp}.png"
            
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300)
            plt.close(fig)
        
        logger.info(f"Saved metrics comparison visualization to: {filepath}")
        return filepath
    
    def generate_platform_metrics_breakdown(
        self, 
        metrics: ConsolidatedMetrics
    ) -> str:
        """
        Generate a breakdown of metrics for each account.
        
        Args:
            metrics (ConsolidatedMetrics): Consolidated metrics data.
            
        Returns:
            str: Path to the saved visualization file.
        """
        logger.info("Generating platform metrics breakdown visualization")
        
        if not metrics.accounts:
            logger.warning("No account data available for visualization")
            return ""
        
        # Create DataFrame from accounts data
        accounts_df = pd.DataFrame(metrics.accounts)
        
        with LogPerformance(logger, "Creating platform metrics breakdown chart"):
            # Create a figure with subplots for each metric
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle("Metrics by Account", fontsize=16)
            
            metrics_to_plot = ['views', 'reach', 'likes', 'follows']
            positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
            titles = ['Views', 'Reach', 'Likes', 'Follows']
            
            for metric, pos, title in zip(metrics_to_plot, positions, titles):
                ax = axes[pos]
                
                # Sort by the metric value in descending order
                sorted_df = accounts_df.sort_values(by=metric, ascending=False)
                
                # Plot horizontal bar chart
                bars = ax.barh(sorted_df['name'], sorted_df[metric])
                ax.set_title(title)
                ax.set_xlabel(title)
                
                # Add platform type colors
                for i, bar in enumerate(bars):
                    platform = sorted_df.iloc[i]['type']
                    color = 'royalblue' if platform == 'Facebook Page' else 'mediumorchid'
                    bar.set_color(color)
                
                # Add value labels
                for i, v in enumerate(sorted_df[metric]):
                    ax.text(
                        v + (v * 0.01),  # Slight offset
                        i,
                        f"{int(v):,}",
                        va='center',
                        fontsize=9
                    )
                
                # Add legend only once
                if pos == (0, 0):
                    from matplotlib.patches import Patch
                    legend_elements = [
                        Patch(facecolor='royalblue', label='Facebook'),
                        Patch(facecolor='mediumorchid', label='Instagram')
                    ]
                    ax.legend(handles=legend_elements, loc='lower right')
            
            plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to make room for title
            
            # Generate filename with timestamp
            timestamp = create_filename_timestamp()
            filename = f"account_metrics_breakdown_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300)
            plt.close(fig)
        
        logger.info(f"Saved platform metrics breakdown visualization to: {filepath}")
        return filepath
    
    def generate_demographics_visualization(
        self, 
        demographics: Demographics, 
        account_name: str
    ) -> Dict[str, str]:
        """
        Generate visualizations for demographic data.
        
        Args:
            demographics (Demographics): Demographics data.
            account_name (str): Name of the account.
            
        Returns:
            dict: Paths to the saved visualization files.
        """
        logger.info(f"Generating demographics visualizations for {account_name}")
        
        result = {
            'age_gender': '',
            'location': ''
        }
        
        # Check if we have age/gender data
        if demographics.age_gender:
            with LogPerformance(logger, "Creating age/gender demographics chart"):
                # Create DataFrame and sort it
                age_gender_df = pd.DataFrame([
                    {'category': k, 'value': v} 
                    for k, v in demographics.age_gender.items()
                ])
                
                # Extract gender and age range for better visualization
                age_gender_df['gender'] = age_gender_df['category'].apply(lambda x: x.split('.')[0])
                age_gender_df['age_range'] = age_gender_df['category'].apply(lambda x: x.split('.')[1] if '.' in x else 'Unknown')
                
                # Create figure for age/gender breakdown
                fig, ax = plt.subplots(figsize=(12, 8))
                
                # Group by gender and age range
                pivot_df = age_gender_df.pivot_table(
                    index='age_range',
                    columns='gender',
                    values='value',
                    aggfunc='sum'
                ).fillna(0)
                
                # Plot grouped bar chart
                pivot_df.plot(kind='bar', ax=ax)
                
                ax.set_title(f"Age and Gender Distribution - {account_name}")
                ax.set_ylabel('Number of Users')
                ax.set_xlabel('Age Range')
                
                plt.tight_layout()
                
                # Generate filename with timestamp
                timestamp = create_filename_timestamp()
                filename = f"demographics_age_gender_{account_name}_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)
                plt.savefig(filepath, dpi=300)
                plt.close(fig)
                
                result['age_gender'] = filepath
                logger.info(f"Saved age/gender demographics visualization to: {filepath}")
        
        # Check if we have location data
        if demographics.location:
            with LogPerformance(logger, "Creating location demographics chart"):
                # Create DataFrame and sort it by value descending
                location_df = pd.DataFrame([
                    {'country': k, 'value': v} 
                    for k, v in demographics.location.items()
                ])
                location_df = location_df.sort_values('value', ascending=False)
                
                # Take the top 15 countries for readability
                top_countries = location_df.head(15)
                
                # Create figure for location breakdown
                fig, ax = plt.subplots(figsize=(12, 8))
                
                # Plot horizontal bar chart
                bars = ax.barh(top_countries['country'], top_countries['value'])
                
                ax.set_title(f"Top Countries Distribution - {account_name}")
                ax.set_xlabel('Number of Users')
                
                # Add value labels
                for i, v in enumerate(top_countries['value']):
                    ax.text(
                        v + (v * 0.01),  # Slight offset
                        i,
                        f"{int(v):,}",
                        va='center'
                    )
                
                plt.tight_layout()
                
                # Generate filename with timestamp
                timestamp = create_filename_timestamp()
                filename = f"demographics_location_{account_name}_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)
                plt.savefig(filepath, dpi=300)
                plt.close(fig)
                
                result['location'] = filepath
                logger.info(f"Saved location demographics visualization to: {filepath}")
        
        return result
    
    def generate_ads_performance_visualization(
        self, 
        ads_data: List[AdData], 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate visualizations for Facebook Ads performance data.
        
        Args:
            ads_data (list): List of ad data objects.
            start_date (str, optional): Start date for the title.
            end_date (str, optional): End date for the title.
            
        Returns:
            dict: Paths to the saved visualization files.
        """
        logger.info("Generating ads performance visualizations")
        
        if not ads_data:
            logger.warning("No ads data available for visualization")
            return {}
        
        result = {}
        
        # Create DataFrame
        ads_df = pd.DataFrame([ad.to_dict() for ad in ads_data])
        
        # Generate Campaign Performance Visualization
        with LogPerformance(logger, "Creating campaign performance chart"):
            # Aggregate by campaign
            campaign_df = ads_df.groupby('campaign_name').agg({
                'impressions': 'sum',
                'reach': 'sum',
                'amount_spent': 'sum'
            }).reset_index()
            
            # Sort by amount spent
            campaign_df = campaign_df.sort_values('amount_spent', ascending=False)
            
            # Take top 10 campaigns by spend
            top_campaigns = campaign_df.head(10)
            
            # Create figure
            fig, ax1 = plt.subplots(figsize=(14, 10))
            
            # Plot bars for amount spent
            bars = ax1.bar(top_campaigns['campaign_name'], top_campaigns['amount_spent'], color='royalblue')
            ax1.set_xlabel('Campaign')
            ax1.set_ylabel('Amount Spent ($)', color='royalblue')
            ax1.tick_params(axis='y', labelcolor='royalblue')
            
            # Rotate x-axis labels for readability
            plt.xticks(rotation=45, ha='right')
            
            # Create second y-axis for impressions
            ax2 = ax1.twinx()
            ax2.plot(top_campaigns['campaign_name'], top_campaigns['impressions'], 'ro-', label='Impressions')
            ax2.plot(top_campaigns['campaign_name'], top_campaigns['reach'], 'go-', label='Reach')
            ax2.set_ylabel('Count', color='red')
            ax2.tick_params(axis='y', labelcolor='red')
            ax2.legend()
            
            # Add title
            title = "Top Campaigns by Spend"
            if start_date and end_date:
                title += f" ({start_date} to {end_date})"
            plt.title(title)
            
            # Add value labels to bars
            for bar in bars:
                height = bar.get_height()
                ax1.text(
                    bar.get_x() + bar.get_width()/2.,
                    height * 1.02,
                    f"${height:,.2f}",
                    ha='center',
                    va='bottom',
                    rotation=0,
                    fontsize=9
                )
            
            plt.tight_layout()
            
            # Generate filename with timestamp
            timestamp = create_filename_timestamp()
            filename = f"ads_campaign_performance_{timestamp}.png"
            if start_date and end_date:
                date_str = f"{start_date}_to_{end_date}".replace("-", "")
                filename = f"ads_campaign_performance_{date_str}_{timestamp}.png"
            
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300)
            plt.close(fig)
            
            result['campaign_performance'] = filepath
            logger.info(f"Saved campaign performance visualization to: {filepath}")
        
        # Generate Demographic Breakdown Visualization
        with LogPerformance(logger, "Creating ads demographic breakdown chart"):
            # Age breakdown
            age_df = ads_df.groupby('age').agg({
                'impressions': 'sum',
                'amount_spent': 'sum'
            }).reset_index()
            
            # Gender breakdown
            gender_df = ads_df.groupby('gender').agg({
                'impressions': 'sum',
                'amount_spent': 'sum'
            }).reset_index()
            
            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
            
            # Plot age breakdown
            age_bars = ax1.bar(age_df['age'], age_df['amount_spent'], color='skyblue')
            ax1.set_title('Ad Spend by Age Group')
            ax1.set_xlabel('Age Group')
            ax1.set_ylabel('Amount Spent ($)')
            
            # Add value labels
            for bar in age_bars:
                height = bar.get_height()
                ax1.text(
                    bar.get_x() + bar.get_width()/2.,
                    height * 1.02,
                    f"${height:,.2f}",
                    ha='center',
                    va='bottom',
                    fontsize=9
                )
            
            # Plot gender breakdown
            gender_bars = ax2.bar(gender_df['gender'], gender_df['amount_spent'], color='lightcoral')
            ax2.set_title('Ad Spend by Gender')
            ax2.set_xlabel('Gender')
            ax2.set_ylabel('Amount Spent ($)')
            
            # Add value labels
            for bar in gender_bars:
                height = bar.get_height()
                ax2.text(
                    bar.get_x() + bar.get_width()/2.,
                    height * 1.02,
                    f"${height:,.2f}",
                    ha='center',
                    va='bottom',
                    fontsize=9
                )
            
            # Add overall title
            fig.suptitle("Ad Spend Demographics", fontsize=16)
            if start_date and end_date:
                fig.suptitle(f"Ad Spend Demographics ({start_date} to {end_date})", fontsize=16)
            
            plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to make room for title
            
            # Generate filename with timestamp
            timestamp = create_filename_timestamp()
            filename = f"ads_demographics_{timestamp}.png"
            if start_date and end_date:
                date_str = f"{start_date}_to_{end_date}".replace("-", "")
                filename = f"ads_demographics_{date_str}_{timestamp}.png"
            
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300)
            plt.close(fig)
            
            result['demographics'] = filepath
            logger.info(f"Saved ads demographics visualization to: {filepath}")
        
        # Generate Platform/Device Breakdown Visualization
        with LogPerformance(logger, "Creating platform/device breakdown chart"):
            # Platform breakdown
            platform_df = ads_df.groupby('platform_device').agg({
                'impressions': 'sum',
                'reach': 'sum',
                'amount_spent': 'sum'
            }).reset_index()
            
            # Sort by amount spent
            platform_df = platform_df.sort_values('amount_spent', ascending=False)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(
                platform_df['amount_spent'], 
                labels=platform_df['platform_device'],
                autopct='%1.1f%%',
                startangle=90,
                shadow=False,
                wedgeprops={'edgecolor': 'w', 'linewidth': 1}
            )
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
            
            # Add title
            title = "Ad Spend by Platform/Device"
            if start_date and end_date:
                title += f" ({start_date} to {end_date})"
            plt.title(title)
            
            # Add legend with absolute values
            legend_labels = [
                f"{platform}: ${spent:,.2f}" 
                for platform, spent in zip(platform_df['platform_device'], platform_df['amount_spent'])
            ]
            plt.legend(wedges, legend_labels, loc="best", bbox_to_anchor=(1, 0, 0.5, 1))
            
            plt.tight_layout()
            
            # Generate filename with timestamp
            timestamp = create_filename_timestamp()
            filename = f"ads_platform_device_{timestamp}.png"
            if start_date and end_date:
                date_str = f"{start_date}_to_{end_date}".replace("-", "")
                filename = f"ads_platform_device_{date_str}_{timestamp}.png"
            
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300)
            plt.close(fig)
            
            result['platform_device'] = filepath
            logger.info(f"Saved platform/device breakdown visualization to: {filepath}")
        
        return result
