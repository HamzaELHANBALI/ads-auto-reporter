"""
Creator and Video Performance Analytics.

This module provides analytics specifically for tracking content creator
and video-level performance for employers monitoring their team's content.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import pandas as pd
from ..models.enums import AdPlatform
from .kpi_calculator import KPICalculator


@dataclass
class CreatorSummary:
    """Summary of a creator's performance."""
    creator_name: str
    total_videos: int
    total_spend: float
    total_revenue: float
    total_impressions: int
    total_clicks: int
    total_conversions: int
    roas: float
    cpc: float
    cpm: float
    cpp: float
    ctr: float
    cvr: float
    platforms: List[str]
    best_video: Optional[str] = None
    best_video_roas: Optional[float] = None


@dataclass
class VideoSummary:
    """Summary of a single video's performance."""
    video_id: str
    video_name: str
    creator_name: str
    platform: str
    campaign: str
    total_spend: float
    total_revenue: float
    total_impressions: int
    total_clicks: int
    total_conversions: int
    roas: float
    cpc: float
    cpm: float
    cpp: float
    ctr: float
    cvr: float
    days_active: int


class CreatorAnalytics:
    """Analytics engine for creator and video performance."""
    
    def __init__(self):
        """Initialize creator analytics."""
        self.kpi_calculator = KPICalculator()
    
    def has_creator_data(self, df: pd.DataFrame) -> bool:
        """
        Check if dataframe has creator tracking columns.
        
        Args:
            df: Input dataframe
            
        Returns:
            True if creator_name column exists and has data
        """
        return 'creator_name' in df.columns and df['creator_name'].notna().any()
    
    def has_video_data(self, df: pd.DataFrame) -> bool:
        """
        Check if dataframe has video tracking columns.
        
        Args:
            df: Input dataframe
            
        Returns:
            True if video columns exist and have data
        """
        return (
            'video_id' in df.columns and df['video_id'].notna().any() or
            'video_name' in df.columns and df['video_name'].notna().any()
        )
    
    def calculate_creator_summaries(self, df: pd.DataFrame) -> List[CreatorSummary]:
        """
        Calculate performance summary for each creator.
        
        Args:
            df: Normalized dataframe with creator_name column
            
        Returns:
            List of CreatorSummary objects
        """
        if not self.has_creator_data(df):
            return []
        
        summaries = []
        
        # Group by creator
        for creator, creator_df in df.groupby('creator_name'):
            if pd.isna(creator) or creator == '':
                continue
            
            # Calculate metrics
            total_spend = creator_df['spend'].sum()
            total_revenue = creator_df['revenue'].sum()
            total_impressions = creator_df['impressions'].sum()
            total_clicks = creator_df['clicks'].sum()
            total_conversions = creator_df['conversions'].sum()
            
            # Calculate KPIs
            roas = self.kpi_calculator._calculate_roas(total_spend, total_revenue)
            cpc = self.kpi_calculator._calculate_cpc(total_spend, total_clicks)
            cpm = self.kpi_calculator._calculate_cpm(total_spend, total_impressions)
            cpp = self.kpi_calculator._calculate_cpp(total_spend, total_conversions)
            ctr = self.kpi_calculator._calculate_ctr(total_impressions, total_clicks)
            cvr = self.kpi_calculator._calculate_cvr(total_clicks, total_conversions)
            
            # Get platforms used
            platforms = creator_df['platform'].unique().tolist()
            
            # Find best video
            best_video = None
            best_video_roas = None
            if self.has_video_data(creator_df):
                video_col = 'video_name' if 'video_name' in creator_df.columns else 'video_id'
                video_perf = creator_df.groupby(video_col).agg({
                    'spend': 'sum',
                    'revenue': 'sum'
                }).reset_index()
                video_perf['roas'] = video_perf.apply(
                    lambda x: self.kpi_calculator._calculate_roas(x['spend'], x['revenue']),
                    axis=1
                )
                if not video_perf.empty:
                    best_row = video_perf.loc[video_perf['roas'].idxmax()]
                    best_video = str(best_row[video_col])
                    best_video_roas = float(best_row['roas'])
            
            # Count unique videos
            video_count = 1  # Default
            if 'video_id' in creator_df.columns:
                video_count = creator_df['video_id'].nunique()
            elif 'video_name' in creator_df.columns:
                video_count = creator_df['video_name'].nunique()
            
            summary = CreatorSummary(
                creator_name=str(creator),
                total_videos=video_count,
                total_spend=total_spend,
                total_revenue=total_revenue,
                total_impressions=total_impressions,
                total_clicks=total_clicks,
                total_conversions=total_conversions,
                roas=roas,
                cpc=cpc,
                cpm=cpm,
                cpp=cpp,
                ctr=ctr,
                cvr=cvr,
                platforms=platforms,
                best_video=best_video,
                best_video_roas=best_video_roas
            )
            
            summaries.append(summary)
        
        return summaries
    
    def calculate_video_summaries(self, df: pd.DataFrame) -> List[VideoSummary]:
        """
        Calculate performance summary for each video.
        
        Args:
            df: Normalized dataframe with video columns
            
        Returns:
            List of VideoSummary objects
        """
        if not self.has_video_data(df):
            return []
        
        # Determine which video identifier to use
        video_col = None
        if 'video_id' in df.columns and df['video_id'].notna().any():
            video_col = 'video_id'
        elif 'video_name' in df.columns and df['video_name'].notna().any():
            video_col = 'video_name'
        else:
            return []
        
        summaries = []
        
        # Prepare grouping columns
        group_cols = [video_col]
        if 'creator_name' in df.columns:
            group_cols.append('creator_name')
        
        # Group by video (and creator if available)
        for group_key, video_df in df.groupby(group_cols):
            # Handle single vs multi-column grouping
            if isinstance(group_key, tuple):
                video_id = str(group_key[0])
                creator = str(group_key[1]) if len(group_key) > 1 else "Unknown"
            else:
                video_id = str(group_key)
                creator = "Unknown"
            
            # Get video name
            video_name = video_id
            if 'video_name' in video_df.columns and video_df['video_name'].notna().any():
                video_name = str(video_df['video_name'].iloc[0])
            
            # Get platform and campaign (first occurrence)
            platform = str(video_df['platform'].iloc[0])
            campaign = str(video_df['campaign'].iloc[0])
            
            # Calculate metrics
            total_spend = video_df['spend'].sum()
            total_revenue = video_df['revenue'].sum()
            total_impressions = video_df['impressions'].sum()
            total_clicks = video_df['clicks'].sum()
            total_conversions = video_df['conversions'].sum()
            
            # Calculate KPIs
            roas = self.kpi_calculator._calculate_roas(total_spend, total_revenue)
            cpc = self.kpi_calculator._calculate_cpc(total_spend, total_clicks)
            cpm = self.kpi_calculator._calculate_cpm(total_spend, total_impressions)
            cpp = self.kpi_calculator._calculate_cpp(total_spend, total_conversions)
            ctr = self.kpi_calculator._calculate_ctr(total_impressions, total_clicks)
            cvr = self.kpi_calculator._calculate_cvr(total_clicks, total_conversions)
            
            # Days active
            days_active = video_df['date'].nunique()
            
            summary = VideoSummary(
                video_id=video_id,
                video_name=video_name,
                creator_name=creator,
                platform=platform,
                campaign=campaign,
                total_spend=total_spend,
                total_revenue=total_revenue,
                total_impressions=total_impressions,
                total_clicks=total_clicks,
                total_conversions=total_conversions,
                roas=roas,
                cpc=cpc,
                cpm=cpm,
                cpp=cpp,
                ctr=ctr,
                cvr=cvr,
                days_active=days_active
            )
            
            summaries.append(summary)
        
        return summaries
    
    def get_creator_leaderboard(
        self, 
        df: pd.DataFrame, 
        metric: str = 'roas',
        top_n: int = 10
    ) -> List[CreatorSummary]:
        """
        Get leaderboard of top creators by specified metric.
        
        Args:
            df: Normalized dataframe
            metric: Metric to sort by ('roas', 'revenue', 'conversions', etc.)
            top_n: Number of top creators to return
            
        Returns:
            List of top CreatorSummary objects
        """
        summaries = self.calculate_creator_summaries(df)
        
        # Sort by metric
        sorted_summaries = sorted(
            summaries,
            key=lambda x: getattr(x, metric, 0),
            reverse=True
        )
        
        return sorted_summaries[:top_n]
    
    def get_video_leaderboard(
        self,
        df: pd.DataFrame,
        metric: str = 'roas',
        top_n: int = 10,
        creator: Optional[str] = None
    ) -> List[VideoSummary]:
        """
        Get leaderboard of top videos by specified metric.
        
        Args:
            df: Normalized dataframe
            metric: Metric to sort by
            top_n: Number of top videos to return
            creator: Optional filter by creator name
            
        Returns:
            List of top VideoSummary objects
        """
        summaries = self.calculate_video_summaries(df)
        
        # Filter by creator if specified
        if creator:
            summaries = [s for s in summaries if s.creator_name == creator]
        
        # Sort by metric
        sorted_summaries = sorted(
            summaries,
            key=lambda x: getattr(x, metric, 0),
            reverse=True
        )
        
        return sorted_summaries[:top_n]

