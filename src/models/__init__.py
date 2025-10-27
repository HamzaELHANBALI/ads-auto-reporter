"""Data models and schemas for the ads reporting system."""

from .enums import AdPlatform, KPIMetric, ReportPeriod
from .schemas import (
    AdRecord,
    KPIResult,
    CampaignSummary,
    ReportConfig,
    EmailConfig
)

__all__ = [
    "AdPlatform",
    "KPIMetric",
    "ReportPeriod",
    "AdRecord",
    "KPIResult",
    "CampaignSummary",
    "ReportConfig",
    "EmailConfig"
]




