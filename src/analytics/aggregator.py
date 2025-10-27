"""Data aggregation for time-based analysis."""

from typing import Dict, List, Optional
from datetime import date, timedelta
import pandas as pd
from ..models.enums import ReportPeriod, AdPlatform
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DataAggregator:
    """
    Aggregates ad data by time periods and dimensions.
    
    Supports aggregation by:
    - Daily, weekly, monthly, quarterly
    - Campaign
    - Platform
    - Custom date ranges
    """
    
    def __init__(self):
        """Initialize data aggregator."""
        pass
    
    def aggregate_by_period(
        self,
        df: pd.DataFrame,
        period: ReportPeriod
    ) -> pd.DataFrame:
        """
        Aggregate data by time period.
        
        Args:
            df: Normalized DataFrame
            period: Aggregation period
            
        Returns:
            Aggregated DataFrame
        """
        if df.empty:
            logger.warning("Empty DataFrame provided for aggregation")
            return df
        
        # Ensure date column is datetime
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Determine grouping frequency
        freq_map = {
            ReportPeriod.DAILY: 'D',
            ReportPeriod.WEEKLY: 'W',
            ReportPeriod.MONTHLY: 'M',
            ReportPeriod.QUARTERLY: 'Q',
            ReportPeriod.ALL_TIME: None
        }
        
        freq = freq_map.get(period)
        
        if freq is None:  # ALL_TIME
            return self._aggregate_all(df)
        
        # Group by period and aggregate
        df['period'] = df['date'].dt.to_period(freq)
        
        aggregated = df.groupby('period').agg({
            'spend': 'sum',
            'revenue': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        # Convert period back to date
        aggregated['date'] = aggregated['period'].dt.to_timestamp()
        aggregated = aggregated.drop('period', axis=1)
        
        logger.info(f"Aggregated to {len(aggregated)} {period.value} periods")
        return aggregated
    
    def aggregate_by_campaign(
        self,
        df: pd.DataFrame,
        period: Optional[ReportPeriod] = None
    ) -> pd.DataFrame:
        """
        Aggregate data by campaign.
        
        Args:
            df: Normalized DataFrame
            period: Optional time period for additional grouping
            
        Returns:
            Aggregated DataFrame
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        group_cols = ['campaign', 'platform']
        
        if period and period != ReportPeriod.ALL_TIME:
            df['date'] = pd.to_datetime(df['date'])
            freq_map = {
                ReportPeriod.DAILY: 'D',
                ReportPeriod.WEEKLY: 'W',
                ReportPeriod.MONTHLY: 'M',
                ReportPeriod.QUARTERLY: 'Q'
            }
            freq = freq_map.get(period)
            df['period'] = df['date'].dt.to_period(freq)
            group_cols.append('period')
        
        aggregated = df.groupby(group_cols).agg({
            'spend': 'sum',
            'revenue': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum',
            'date': ['min', 'max']
        }).reset_index()
        
        # Flatten column names
        aggregated.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                             for col in aggregated.columns.values]
        
        if 'period' in aggregated.columns:
            aggregated['date'] = aggregated['period'].dt.to_timestamp()
            aggregated = aggregated.drop('period', axis=1)
        else:
            aggregated = aggregated.rename(columns={
                'date_min': 'period_start',
                'date_max': 'period_end'
            })
        
        logger.info(f"Aggregated to {len(aggregated)} campaign records")
        return aggregated
    
    def aggregate_by_platform(
        self,
        df: pd.DataFrame,
        period: Optional[ReportPeriod] = None
    ) -> pd.DataFrame:
        """
        Aggregate data by platform.
        
        Args:
            df: Normalized DataFrame
            period: Optional time period for additional grouping
            
        Returns:
            Aggregated DataFrame
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        group_cols = ['platform']
        
        if period and period != ReportPeriod.ALL_TIME:
            df['date'] = pd.to_datetime(df['date'])
            freq_map = {
                ReportPeriod.DAILY: 'D',
                ReportPeriod.WEEKLY: 'W',
                ReportPeriod.MONTHLY: 'M',
                ReportPeriod.QUARTERLY: 'Q'
            }
            freq = freq_map.get(period)
            df['period'] = df['date'].dt.to_period(freq)
            group_cols.append('period')
        
        aggregated = df.groupby(group_cols).agg({
            'spend': 'sum',
            'revenue': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum',
            'date': ['min', 'max']
        }).reset_index()
        
        # Flatten column names
        aggregated.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                             for col in aggregated.columns.values]
        
        if 'period' in aggregated.columns:
            aggregated['date'] = aggregated['period'].dt.to_timestamp()
            aggregated = aggregated.drop('period', axis=1)
        else:
            aggregated = aggregated.rename(columns={
                'date_min': 'period_start',
                'date_max': 'period_end'
            })
        
        logger.info(f"Aggregated to {len(aggregated)} platform records")
        return aggregated
    
    def _aggregate_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate all data into single row."""
        aggregated = pd.DataFrame([{
            'spend': df['spend'].sum(),
            'revenue': df['revenue'].sum(),
            'impressions': df['impressions'].sum(),
            'clicks': df['clicks'].sum(),
            'conversions': df['conversions'].sum(),
            'date_min': df['date'].min(),
            'date_max': df['date'].max()
        }])
        
        return aggregated
    
    def filter_date_range(
        self,
        df: pd.DataFrame,
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """
        Filter DataFrame by date range.
        
        Args:
            df: DataFrame to filter
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            Filtered DataFrame
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        mask = (df['date'] >= pd.to_datetime(start_date)) & \
               (df['date'] <= pd.to_datetime(end_date))
        
        filtered = df[mask].copy()
        
        logger.info(f"Filtered to {len(filtered)} rows between {start_date} and {end_date}")
        return filtered
    
    def get_top_campaigns(
        self,
        df: pd.DataFrame,
        metric: str = 'revenue',
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        Get top N campaigns by specified metric.
        
        Args:
            df: Normalized DataFrame
            metric: Metric to rank by (revenue, spend, conversions, etc.)
            top_n: Number of top campaigns to return
            
        Returns:
            DataFrame with top campaigns
        """
        if df.empty:
            return df
        
        # Aggregate by campaign
        campaign_totals = df.groupby(['campaign', 'platform']).agg({
            'spend': 'sum',
            'revenue': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        # Sort by metric
        if metric not in campaign_totals.columns:
            logger.warning(f"Metric '{metric}' not found, using 'revenue'")
            metric = 'revenue'
        
        top_campaigns = campaign_totals.nlargest(top_n, metric)
        
        logger.info(f"Retrieved top {len(top_campaigns)} campaigns by {metric}")
        return top_campaigns
    
    def calculate_daily_trends(
        self,
        df: pd.DataFrame,
        lookback_days: int = 30
    ) -> pd.DataFrame:
        """
        Calculate daily trends for the last N days.
        
        Args:
            df: Normalized DataFrame
            lookback_days: Number of days to look back
            
        Returns:
            DataFrame with daily metrics and trends
        """
        if df.empty:
            return df
        
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Get date range
        max_date = df['date'].max()
        min_date = max_date - timedelta(days=lookback_days)
        
        # Filter to lookback period
        recent_df = df[df['date'] >= min_date].copy()
        
        # Aggregate by day
        daily = recent_df.groupby('date').agg({
            'spend': 'sum',
            'revenue': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        # Calculate rolling averages
        daily['spend_7d_avg'] = daily['spend'].rolling(window=7, min_periods=1).mean()
        daily['revenue_7d_avg'] = daily['revenue'].rolling(window=7, min_periods=1).mean()
        
        # Calculate day-over-day changes
        daily['spend_change'] = daily['spend'].pct_change()
        daily['revenue_change'] = daily['revenue'].pct_change()
        
        logger.info(f"Calculated daily trends for {len(daily)} days")
        return daily




