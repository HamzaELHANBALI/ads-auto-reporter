"""KPI calculation engine for ad performance metrics."""

from typing import List, Dict, Optional
from datetime import date
import pandas as pd
from ..models.enums import KPIMetric, AdPlatform
from ..models.schemas import AdRecord, KPIResult, CampaignSummary
from ..utils.logger import get_logger

logger = get_logger(__name__)


class KPICalculator:
    """
    Calculates Key Performance Indicators for ad campaigns.
    
    Supports:
    - ROAS (Return on Ad Spend)
    - CPC (Cost Per Click)
    - CPM (Cost Per Mille/1000 impressions)
    - CPP (Cost Per Purchase/Conversion)
    - CTR (Click Through Rate)
    - CVR (Conversion Rate)
    """
    
    def __init__(self):
        """Initialize KPI calculator."""
        self.calculation_methods = {
            KPIMetric.ROAS: self._calculate_roas,
            KPIMetric.CPC: self._calculate_cpc,
            KPIMetric.CPM: self._calculate_cpm,
            KPIMetric.CPP: self._calculate_cpp,
            KPIMetric.CTR: self._calculate_ctr,
            KPIMetric.CVR: self._calculate_cvr,
        }
    
    def calculate_all_kpis(
        self,
        spend: float,
        revenue: float,
        impressions: int,
        clicks: int,
        conversions: int,
        period_start: date,
        period_end: date,
        campaign: Optional[str] = None,
        platform: Optional[AdPlatform] = None
    ) -> List[KPIResult]:
        """
        Calculate all KPIs for given metrics.
        
        Args:
            spend: Total ad spend
            revenue: Total revenue
            impressions: Total impressions
            clicks: Total clicks
            conversions: Total conversions
            period_start: Start date
            period_end: End date
            campaign: Campaign name (optional)
            platform: Platform (optional)
            
        Returns:
            List of KPIResult objects
        """
        results = []
        
        metrics_data = {
            'spend': spend,
            'revenue': revenue,
            'impressions': impressions,
            'clicks': clicks,
            'conversions': conversions
        }
        
        for metric, calc_func in self.calculation_methods.items():
            try:
                value = calc_func(**metrics_data)
                result = KPIResult(
                    metric=metric,
                    value=value,
                    period_start=period_start,
                    period_end=period_end,
                    campaign=campaign,
                    platform=platform
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to calculate {metric.value}: {e}")
                continue
        
        return results
    
    def calculate_kpi(
        self,
        metric: KPIMetric,
        spend: float = 0,
        revenue: float = 0,
        impressions: int = 0,
        clicks: int = 0,
        conversions: int = 0
    ) -> float:
        """
        Calculate a specific KPI.
        
        Args:
            metric: KPI metric to calculate
            spend: Total ad spend
            revenue: Total revenue
            impressions: Total impressions
            clicks: Total clicks
            conversions: Total conversions
            
        Returns:
            Calculated KPI value
        """
        calc_func = self.calculation_methods.get(metric)
        if not calc_func:
            raise ValueError(f"Unknown KPI metric: {metric}")
        
        return calc_func(
            spend=spend,
            revenue=revenue,
            impressions=impressions,
            clicks=clicks,
            conversions=conversions
        )
    
    def _calculate_roas(self, spend: float, revenue: float, **kwargs) -> float:
        """
        Calculate Return on Ad Spend.
        ROAS = Revenue / Spend
        """
        if spend == 0:
            return 0.0
        return revenue / spend
    
    def _calculate_cpc(self, spend: float, clicks: int, **kwargs) -> float:
        """
        Calculate Cost Per Click.
        CPC = Spend / Clicks
        """
        if clicks == 0:
            return 0.0
        return spend / clicks
    
    def _calculate_cpm(self, spend: float, impressions: int, **kwargs) -> float:
        """
        Calculate Cost Per Mille (1000 impressions).
        CPM = (Spend / Impressions) * 1000
        """
        if impressions == 0:
            return 0.0
        return (spend / impressions) * 1000
    
    def _calculate_cpp(self, spend: float, conversions: int, **kwargs) -> float:
        """
        Calculate Cost Per Purchase/Conversion.
        CPP = Spend / Conversions
        """
        if conversions == 0:
            return 0.0
        return spend / conversions
    
    def _calculate_ctr(self, impressions: int, clicks: int, **kwargs) -> float:
        """
        Calculate Click Through Rate.
        CTR = Clicks / Impressions
        """
        if impressions == 0:
            return 0.0
        return clicks / impressions
    
    def _calculate_cvr(self, clicks: int, conversions: int, **kwargs) -> float:
        """
        Calculate Conversion Rate.
        CVR = Conversions / Clicks
        """
        if clicks == 0:
            return 0.0
        return conversions / clicks
    
    def calculate_campaign_summary(
        self,
        records: List[AdRecord],
        campaign: str,
        platform: AdPlatform
    ) -> CampaignSummary:
        """
        Calculate comprehensive summary for a campaign.
        
        Args:
            records: List of AdRecord objects for the campaign
            campaign: Campaign name
            platform: Platform
            
        Returns:
            CampaignSummary object
        """
        if not records:
            raise ValueError("No records provided for campaign summary")
        
        # Aggregate metrics
        total_spend = sum(r.spend for r in records)
        total_revenue = sum(r.revenue for r in records)
        total_impressions = sum(r.impressions for r in records)
        total_clicks = sum(r.clicks for r in records)
        total_conversions = sum(r.conversions for r in records)
        
        # Calculate KPIs
        roas = self._calculate_roas(total_spend, total_revenue)
        cpc = self._calculate_cpc(total_spend, total_clicks)
        cpm = self._calculate_cpm(total_spend, total_impressions)
        cpp = self._calculate_cpp(total_spend, total_conversions)
        ctr = self._calculate_ctr(total_impressions, total_clicks)
        cvr = self._calculate_cvr(total_clicks, total_conversions)
        
        # Date range and activity
        dates = [r.date for r in records]
        period_start = min(dates)
        period_end = max(dates)
        days_active = len(set(dates))
        avg_daily_spend = total_spend / days_active if days_active > 0 else 0
        
        return CampaignSummary(
            campaign=campaign,
            platform=platform,
            period_start=period_start,
            period_end=period_end,
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
            days_active=days_active,
            avg_daily_spend=avg_daily_spend
        )
    
    def calculate_multiple_campaigns(
        self,
        df: pd.DataFrame
    ) -> List[CampaignSummary]:
        """
        Calculate summaries for all campaigns in a DataFrame.
        
        Args:
            df: Normalized DataFrame with ad records
            
        Returns:
            List of CampaignSummary objects
        """
        summaries = []
        
        # Group by campaign and platform
        for (campaign, platform), group in df.groupby(['campaign', 'platform']):
            try:
                records = [
                    AdRecord(
                        date=row['date'],
                        platform=AdPlatform(platform),
                        campaign=campaign,
                        spend=row['spend'],
                        impressions=row['impressions'],
                        clicks=row['clicks'],
                        conversions=row['conversions'],
                        revenue=row['revenue']
                    )
                    for _, row in group.iterrows()
                ]
                
                summary = self.calculate_campaign_summary(
                    records,
                    campaign,
                    AdPlatform(platform)
                )
                summaries.append(summary)
            except Exception as e:
                logger.error(f"Failed to calculate summary for {campaign}: {e}")
                continue
        
        logger.info(f"Calculated summaries for {len(summaries)} campaigns")
        return summaries
    
    def compare_periods(
        self,
        current_df: pd.DataFrame,
        previous_df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Compare KPIs between two time periods.
        
        Args:
            current_df: Current period data
            previous_df: Previous period data
            
        Returns:
            Dictionary of percentage changes
        """
        current_totals = self._calculate_totals(current_df)
        previous_totals = self._calculate_totals(previous_df)
        
        changes = {}
        for key in current_totals:
            current = current_totals[key]
            previous = previous_totals[key]
            
            if previous == 0:
                changes[f"{key}_change"] = 0.0 if current == 0 else float('inf')
            else:
                changes[f"{key}_change"] = (current - previous) / previous
        
        return changes
    
    def _calculate_totals(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate total metrics from DataFrame."""
        if df.empty:
            return {
                'spend': 0.0,
                'revenue': 0.0,
                'impressions': 0,
                'clicks': 0,
                'conversions': 0
            }
        
        spend = df['spend'].sum()
        revenue = df['revenue'].sum()
        impressions = df['impressions'].sum()
        clicks = df['clicks'].sum()
        conversions = df['conversions'].sum()
        
        return {
            'spend': spend,
            'revenue': revenue,
            'impressions': impressions,
            'clicks': clicks,
            'conversions': conversions,
            'roas': self._calculate_roas(spend, revenue),
            'cpc': self._calculate_cpc(spend, clicks),
            'cpm': self._calculate_cpm(spend, impressions),
            'cpp': self._calculate_cpp(spend, conversions),
            'ctr': self._calculate_ctr(impressions, clicks),
            'cvr': self._calculate_cvr(clicks, conversions)
        }




