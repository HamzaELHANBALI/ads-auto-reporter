"""Enumerations and constants for the ads reporting system."""

from enum import Enum
from typing import Final


class AdPlatform(str, Enum):
    """Supported advertising platforms."""
    TIKTOK = "tiktok"
    META = "meta"
    GOOGLE = "google"


class KPIMetric(str, Enum):
    """Key Performance Indicator metrics."""
    # Primary metrics
    SPEND = "spend"
    REVENUE = "revenue"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    
    # Calculated KPIs
    ROAS = "roas"  # Return on Ad Spend
    CPC = "cpc"    # Cost Per Click
    CPM = "cpm"    # Cost Per Mille (1000 impressions)
    CPP = "cpp"    # Cost Per Purchase/Conversion
    CTR = "ctr"    # Click Through Rate
    CVR = "cvr"    # Conversion Rate


class ReportPeriod(str, Enum):
    """Time period aggregation levels."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ALL_TIME = "all_time"


# Standard column names after normalization
NORMALIZED_COLUMNS: Final[list[str]] = [
    "date",
    "platform",
    "campaign",
    "spend",
    "impressions",
    "clicks",
    "conversions",
    "revenue"
]

# Optional columns for enhanced tracking (creator/video performance)
OPTIONAL_COLUMNS: Final[list[str]] = [
    "creator_name",      # Name of content creator/influencer/employee
    "video_id",          # Unique video identifier
    "video_name",        # Video title/name
    "ad_set_name",       # Ad set grouping
    "creative_type"      # e.g., 'video', 'image', 'carousel'
]

# KPI formulas as constants
KPI_FORMULAS: Final[dict[str, str]] = {
    "ROAS": "Revenue / Spend",
    "CPC": "Spend / Clicks",
    "CPM": "(Spend / Impressions) * 1000",
    "CPP": "Spend / Conversions",
    "CTR": "Clicks / Impressions",
    "CVR": "Conversions / Clicks"
}




