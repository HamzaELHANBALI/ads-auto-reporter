"""Pydantic schemas for data validation and serialization."""

from datetime import date, datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field, EmailStr, validator
from .enums import AdPlatform, KPIMetric, ReportPeriod


class AdRecord(BaseModel):
    """Normalized ad performance record."""
    date: date
    platform: AdPlatform
    campaign: str
    spend: float = Field(ge=0, description="Ad spend in currency units")
    impressions: int = Field(ge=0, description="Number of ad impressions")
    clicks: int = Field(ge=0, description="Number of clicks")
    conversions: int = Field(ge=0, description="Number of conversions/purchases")
    revenue: float = Field(ge=0, description="Revenue generated")
    
    @validator('spend', 'revenue')
    def round_currency(cls, v):
        """Round currency values to 2 decimal places."""
        return round(v, 2)
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            date: lambda v: v.isoformat()
        }


class KPIResult(BaseModel):
    """KPI calculation result."""
    metric: KPIMetric
    value: float
    period_start: date
    period_end: date
    campaign: Optional[str] = None
    platform: Optional[AdPlatform] = None
    
    @validator('value')
    def round_value(cls, v):
        """Round KPI values to 4 decimal places."""
        return round(v, 4)


class CampaignSummary(BaseModel):
    """Aggregated campaign performance summary."""
    campaign: str
    platform: AdPlatform
    period_start: date
    period_end: date
    
    # Aggregated metrics
    total_spend: float
    total_revenue: float
    total_impressions: int
    total_clicks: int
    total_conversions: int
    
    # Calculated KPIs
    roas: float
    cpc: float
    cpm: float
    cpp: float
    ctr: float
    cvr: float
    
    # Performance indicators
    days_active: int
    avg_daily_spend: float
    
    @validator('roas', 'cpc', 'cpm', 'cpp', 'ctr', 'cvr')
    def round_kpi(cls, v):
        """Round KPI values."""
        return round(v, 4)


class ReportConfig(BaseModel):
    """Configuration for report generation."""
    period: ReportPeriod
    start_date: date
    end_date: date
    platforms: List[AdPlatform] = Field(default_factory=list)
    campaigns: List[str] = Field(default_factory=list)
    include_charts: bool = True
    include_recommendations: bool = True
    
    @validator('end_date')
    def end_after_start(cls, v, values):
        """Validate end date is after start date."""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class EmailConfig(BaseModel):
    """Email delivery configuration."""
    smtp_server: str
    smtp_port: int = 587
    username: str
    password: str
    sender_email: EmailStr
    sender_name: str = "Ads Reporting"
    recipients: List[EmailStr]
    cc: List[EmailStr] = Field(default_factory=list)
    use_tls: bool = True
    
    class Config:
        """Pydantic configuration."""
        # Hide sensitive data in repr
        fields = {
            'password': {'exclude': True}
        }


class PerformanceAlert(BaseModel):
    """Alert for underperforming or overperforming campaigns."""
    severity: str = Field(description="low, medium, high")
    campaign: str
    platform: AdPlatform
    metric: KPIMetric
    current_value: float
    threshold_value: float
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WeeklyDigest(BaseModel):
    """Weekly performance digest data structure."""
    week_start: date
    week_end: date
    
    # Overall metrics
    total_spend: float
    total_revenue: float
    total_conversions: int
    overall_roas: float
    
    # Week-over-week comparison
    wow_spend_change: float
    wow_revenue_change: float
    wow_roas_change: float
    
    # Top performers
    top_campaigns: List[CampaignSummary]
    
    # Alerts
    alerts: List[PerformanceAlert] = Field(default_factory=list)
    
    # Summary statistics
    campaigns_count: int
    platforms_active: List[AdPlatform]




