"""Weekly digest generation for email reports."""

from typing import List, Optional
from datetime import date, timedelta
import pandas as pd

from ..models.schemas import (
    WeeklyDigest, CampaignSummary, PerformanceAlert
)
from ..models.enums import AdPlatform, KPIMetric
from ..analytics.kpi_calculator import KPICalculator
from ..analytics.aggregator import DataAggregator
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DigestGenerator:
    """
    Generates weekly performance digests.
    
    Includes:
    - Week-over-week comparisons
    - Top performers
    - Performance alerts
    - Executive summary
    """
    
    def __init__(
        self,
        target_roas: float = 3.0,
        target_ctr: float = 0.02,
        target_cvr: float = 0.05,
        max_cpp: float = 50.0
    ):
        """
        Initialize digest generator with KPI thresholds.
        
        Args:
            target_roas: Target ROAS threshold
            target_ctr: Target CTR threshold
            target_cvr: Target CVR threshold
            max_cpp: Maximum acceptable cost per purchase
        """
        self.target_roas = target_roas
        self.target_ctr = target_ctr
        self.target_cvr = target_cvr
        self.max_cpp = max_cpp
        
        self.kpi_calculator = KPICalculator()
        self.aggregator = DataAggregator()
    
    def generate_weekly_digest(
        self,
        df: pd.DataFrame,
        week_end_date: Optional[date] = None
    ) -> WeeklyDigest:
        """
        Generate weekly performance digest.
        
        Args:
            df: Normalized DataFrame with all data
            week_end_date: End date of the week (defaults to today)
            
        Returns:
            WeeklyDigest object
        """
        if week_end_date is None:
            week_end_date = date.today()
        
        # Calculate week boundaries
        week_start = week_end_date - timedelta(days=6)
        prev_week_end = week_start - timedelta(days=1)
        prev_week_start = prev_week_end - timedelta(days=6)
        
        logger.info(f"Generating digest for {week_start} to {week_end_date}")
        
        # Filter data for current and previous weeks
        current_week_df = self.aggregator.filter_date_range(df, week_start, week_end_date)
        previous_week_df = self.aggregator.filter_date_range(df, prev_week_start, prev_week_end)
        
        # Calculate current week metrics
        current_metrics = self._calculate_period_metrics(current_week_df)
        
        # Calculate previous week metrics for comparison
        previous_metrics = self._calculate_period_metrics(previous_week_df)
        
        # Week-over-week changes
        wow_spend_change = self._calculate_change(
            current_metrics['spend'],
            previous_metrics['spend']
        )
        wow_revenue_change = self._calculate_change(
            current_metrics['revenue'],
            previous_metrics['revenue']
        )
        wow_roas_change = self._calculate_change(
            current_metrics['roas'],
            previous_metrics['roas']
        )
        
        # Get top campaigns
        top_campaigns = self._get_top_campaigns(current_week_df, top_n=5)
        
        # Generate alerts
        alerts = self._generate_alerts(current_week_df, top_campaigns)
        
        # Get active platforms
        platforms_active = [
            AdPlatform(p) for p in current_week_df['platform'].unique()
        ] if not current_week_df.empty else []
        
        # Get campaign count
        campaigns_count = current_week_df['campaign'].nunique() if not current_week_df.empty else 0
        
        digest = WeeklyDigest(
            week_start=week_start,
            week_end=week_end_date,
            total_spend=current_metrics['spend'],
            total_revenue=current_metrics['revenue'],
            total_conversions=current_metrics['conversions'],
            overall_roas=current_metrics['roas'],
            wow_spend_change=wow_spend_change,
            wow_revenue_change=wow_revenue_change,
            wow_roas_change=wow_roas_change,
            top_campaigns=top_campaigns,
            alerts=alerts,
            campaigns_count=campaigns_count,
            platforms_active=platforms_active
        )
        
        logger.info(f"Generated digest with {len(alerts)} alerts and {len(top_campaigns)} top campaigns")
        return digest
    
    def _calculate_period_metrics(self, df: pd.DataFrame) -> dict:
        """Calculate aggregated metrics for a period."""
        if df.empty:
            return {
                'spend': 0.0,
                'revenue': 0.0,
                'conversions': 0,
                'clicks': 0,
                'impressions': 0,
                'roas': 0.0
            }
        
        spend = df['spend'].sum()
        revenue = df['revenue'].sum()
        conversions = df['conversions'].sum()
        clicks = df['clicks'].sum()
        impressions = df['impressions'].sum()
        
        roas = self.kpi_calculator._calculate_roas(spend, revenue)
        
        return {
            'spend': spend,
            'revenue': revenue,
            'conversions': int(conversions),
            'clicks': int(clicks),
            'impressions': int(impressions),
            'roas': roas
        }
    
    def _calculate_change(self, current: float, previous: float) -> float:
        """Calculate percentage change."""
        if previous == 0:
            return 0.0 if current == 0 else float('inf')
        return (current - previous) / previous
    
    def _get_top_campaigns(
        self,
        df: pd.DataFrame,
        top_n: int = 5
    ) -> List[CampaignSummary]:
        """Get top performing campaigns."""
        if df.empty:
            return []
        
        summaries = self.kpi_calculator.calculate_multiple_campaigns(df)
        
        # Sort by revenue
        sorted_summaries = sorted(
            summaries,
            key=lambda x: x.total_revenue,
            reverse=True
        )
        
        return sorted_summaries[:top_n]
    
    def _generate_alerts(
        self,
        df: pd.DataFrame,
        summaries: List[CampaignSummary]
    ) -> List[PerformanceAlert]:
        """Generate performance alerts for underperforming campaigns."""
        alerts = []
        
        for summary in summaries:
            # ROAS alert
            if summary.roas < self.target_roas and summary.total_spend > 100:
                severity = 'high' if summary.roas < self.target_roas * 0.5 else 'medium'
                alerts.append(PerformanceAlert(
                    severity=severity,
                    campaign=summary.campaign,
                    platform=summary.platform,
                    metric=KPIMetric.ROAS,
                    current_value=summary.roas,
                    threshold_value=self.target_roas,
                    message=f"Campaign '{summary.campaign}' has ROAS of {summary.roas:.2f}x, "
                           f"below target of {self.target_roas:.2f}x"
                ))
            
            # CTR alert
            if summary.ctr < self.target_ctr and summary.total_impressions > 1000:
                alerts.append(PerformanceAlert(
                    severity='medium',
                    campaign=summary.campaign,
                    platform=summary.platform,
                    metric=KPIMetric.CTR,
                    current_value=summary.ctr,
                    threshold_value=self.target_ctr,
                    message=f"Campaign '{summary.campaign}' has low CTR of {summary.ctr*100:.2f}%, "
                           f"below target of {self.target_ctr*100:.2f}%"
                ))
            
            # CVR alert
            if summary.cvr < self.target_cvr and summary.total_clicks > 100:
                alerts.append(PerformanceAlert(
                    severity='medium',
                    campaign=summary.campaign,
                    platform=summary.platform,
                    metric=KPIMetric.CVR,
                    current_value=summary.cvr,
                    threshold_value=self.target_cvr,
                    message=f"Campaign '{summary.campaign}' has low CVR of {summary.cvr*100:.2f}%, "
                           f"below target of {self.target_cvr*100:.2f}%"
                ))
            
            # CPP alert
            if summary.cpp > self.max_cpp and summary.total_conversions > 0:
                alerts.append(PerformanceAlert(
                    severity='high',
                    campaign=summary.campaign,
                    platform=summary.platform,
                    metric=KPIMetric.CPP,
                    current_value=summary.cpp,
                    threshold_value=self.max_cpp,
                    message=f"Campaign '{summary.campaign}' has high cost per purchase of ${summary.cpp:.2f}, "
                           f"exceeds maximum of ${self.max_cpp:.2f}"
                ))
            
            # High spend, no conversions alert
            if summary.total_spend > 500 and summary.total_conversions == 0:
                alerts.append(PerformanceAlert(
                    severity='high',
                    campaign=summary.campaign,
                    platform=summary.platform,
                    metric=KPIMetric.CONVERSIONS,
                    current_value=0.0,
                    threshold_value=1.0,
                    message=f"Campaign '{summary.campaign}' has spent ${summary.total_spend:.2f} "
                           f"with no conversions"
                ))
        
        # Sort by severity
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        alerts.sort(key=lambda x: severity_order.get(x.severity, 3))
        
        return alerts
    
    def generate_html_summary(self, digest: WeeklyDigest) -> str:
        """
        Generate HTML summary for email.
        
        Args:
            digest: WeeklyDigest object
            
        Returns:
            HTML string
        """
        from ..utils.helpers import format_currency, format_percentage
        
        # Determine color for WoW changes
        def change_color(value):
            if value > 0:
                return '#2ecc71'  # Green
            elif value < 0:
                return '#e74c3c'  # Red
            return '#95a5a6'  # Gray
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .metric-card {{ 
                    background: #ecf0f1; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 5px;
                    border-left: 4px solid #3498db;
                }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
                .change {{ font-size: 16px; font-weight: bold; }}
                .alert {{ 
                    padding: 10px; 
                    margin: 10px 0; 
                    border-radius: 5px; 
                    border-left: 4px solid #e74c3c;
                }}
                .alert.high {{ background: #fadbd8; }}
                .alert.medium {{ background: #fcf3cf; border-left-color: #f39c12; }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 20px 0; 
                }}
                th, td {{ 
                    padding: 12px; 
                    text-align: left; 
                    border-bottom: 1px solid #ddd; 
                }}
                th {{ background-color: #34495e; color: white; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .footer {{ 
                    margin-top: 40px; 
                    padding-top: 20px; 
                    border-top: 1px solid #ddd; 
                    color: #7f8c8d; 
                    font-size: 12px; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Weekly Ads Performance Digest</h1>
                <p><strong>Period:</strong> {digest.week_start.strftime('%B %d, %Y')} - {digest.week_end.strftime('%B %d, %Y')}</p>
                
                <h2>Executive Summary</h2>
                
                <div class="metric-card">
                    <div>Total Spend</div>
                    <div class="metric-value">{format_currency(digest.total_spend)}</div>
                    <div class="change" style="color: {change_color(-digest.wow_spend_change)}">
                        WoW: {format_percentage(digest.wow_spend_change)}
                    </div>
                </div>
                
                <div class="metric-card">
                    <div>Total Revenue</div>
                    <div class="metric-value">{format_currency(digest.total_revenue)}</div>
                    <div class="change" style="color: {change_color(digest.wow_revenue_change)}">
                        WoW: {format_percentage(digest.wow_revenue_change)}
                    </div>
                </div>
                
                <div class="metric-card">
                    <div>Overall ROAS</div>
                    <div class="metric-value">{digest.overall_roas:.2f}x</div>
                    <div class="change" style="color: {change_color(digest.wow_roas_change)}">
                        WoW: {format_percentage(digest.wow_roas_change)}
                    </div>
                </div>
                
                <div class="metric-card">
                    <div>Total Conversions</div>
                    <div class="metric-value">{digest.total_conversions:,}</div>
                </div>
                
                <h2>Top Performing Campaigns</h2>
                <table>
                    <tr>
                        <th>Campaign</th>
                        <th>Platform</th>
                        <th>Revenue</th>
                        <th>ROAS</th>
                        <th>Conversions</th>
                    </tr>
        """
        
        for camp in digest.top_campaigns:
            html += f"""
                    <tr>
                        <td>{camp.campaign}</td>
                        <td>{camp.platform.value.upper()}</td>
                        <td>{format_currency(camp.total_revenue)}</td>
                        <td>{camp.roas:.2f}x</td>
                        <td>{camp.total_conversions:,}</td>
                    </tr>
            """
        
        html += """
                </table>
        """
        
        if digest.alerts:
            html += """
                <h2>⚠️ Performance Alerts</h2>
            """
            for alert in digest.alerts[:5]:  # Show top 5 alerts
                html += f"""
                <div class="alert {alert.severity}">
                    <strong>[{alert.severity.upper()}]</strong> {alert.message}
                </div>
                """
        
        html += f"""
                <div class="footer">
                    <p>This digest covers {digest.campaigns_count} campaigns across {len(digest.platforms_active)} platforms.</p>
                    <p>Generated automatically by Ads Auto-Reporting System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html




