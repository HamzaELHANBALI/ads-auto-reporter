"""Tests for KPI calculation."""

import pytest
from datetime import date

from src.analytics.kpi_calculator import KPICalculator
from src.models.enums import KPIMetric, AdPlatform
from src.models.schemas import AdRecord


@pytest.fixture
def kpi_calculator():
    """KPI calculator instance."""
    return KPICalculator()


@pytest.fixture
def sample_metrics():
    """Sample metrics for testing."""
    return {
        'spend': 1000.0,
        'revenue': 3000.0,
        'impressions': 100000,
        'clicks': 5000,
        'conversions': 150
    }


def test_calculate_roas(kpi_calculator, sample_metrics):
    """Test ROAS calculation."""
    roas = kpi_calculator.calculate_kpi(KPIMetric.ROAS, **sample_metrics)
    
    assert roas == 3.0  # 3000 / 1000


def test_calculate_cpc(kpi_calculator, sample_metrics):
    """Test CPC calculation."""
    cpc = kpi_calculator.calculate_kpi(KPIMetric.CPC, **sample_metrics)
    
    assert cpc == 0.2  # 1000 / 5000


def test_calculate_cpm(kpi_calculator, sample_metrics):
    """Test CPM calculation."""
    cpm = kpi_calculator.calculate_kpi(KPIMetric.CPM, **sample_metrics)
    
    assert cpm == 10.0  # (1000 / 100000) * 1000


def test_calculate_cpp(kpi_calculator, sample_metrics):
    """Test CPP calculation."""
    cpp = kpi_calculator.calculate_kpi(KPIMetric.CPP, **sample_metrics)
    
    assert round(cpp, 2) == 6.67  # 1000 / 150


def test_calculate_ctr(kpi_calculator, sample_metrics):
    """Test CTR calculation."""
    ctr = kpi_calculator.calculate_kpi(KPIMetric.CTR, **sample_metrics)
    
    assert ctr == 0.05  # 5000 / 100000


def test_calculate_cvr(kpi_calculator, sample_metrics):
    """Test CVR calculation."""
    cvr = kpi_calculator.calculate_kpi(KPIMetric.CVR, **sample_metrics)
    
    assert cvr == 0.03  # 150 / 5000


def test_calculate_all_kpis(kpi_calculator, sample_metrics):
    """Test calculation of all KPIs."""
    results = kpi_calculator.calculate_all_kpis(
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
        **sample_metrics
    )
    
    assert len(results) == 6  # 6 KPI metrics
    metrics = {r.metric for r in results}
    assert KPIMetric.ROAS in metrics
    assert KPIMetric.CPC in metrics
    assert KPIMetric.CPM in metrics


def test_zero_division_handling(kpi_calculator):
    """Test handling of zero division."""
    # Zero spend
    roas = kpi_calculator.calculate_kpi(
        KPIMetric.ROAS,
        spend=0,
        revenue=100
    )
    assert roas == 0.0
    
    # Zero clicks
    cpc = kpi_calculator.calculate_kpi(
        KPIMetric.CPC,
        spend=100,
        clicks=0
    )
    assert cpc == 0.0
    
    # Zero conversions
    cpp = kpi_calculator.calculate_kpi(
        KPIMetric.CPP,
        spend=100,
        conversions=0
    )
    assert cpp == 0.0


def test_calculate_campaign_summary(kpi_calculator):
    """Test campaign summary calculation."""
    records = [
        AdRecord(
            date=date(2024, 1, 1),
            platform=AdPlatform.TIKTOK,
            campaign='Test Campaign',
            spend=100.0,
            impressions=10000,
            clicks=500,
            conversions=25,
            revenue=300.0
        ),
        AdRecord(
            date=date(2024, 1, 2),
            platform=AdPlatform.TIKTOK,
            campaign='Test Campaign',
            spend=150.0,
            impressions=15000,
            clicks=750,
            conversions=35,
            revenue=450.0
        )
    ]
    
    summary = kpi_calculator.calculate_campaign_summary(
        records,
        'Test Campaign',
        AdPlatform.TIKTOK
    )
    
    assert summary.campaign == 'Test Campaign'
    assert summary.platform == AdPlatform.TIKTOK
    assert summary.total_spend == 250.0
    assert summary.total_revenue == 750.0
    assert summary.total_conversions == 60
    assert summary.days_active == 2
    assert summary.roas == 3.0


def test_negative_kpis(kpi_calculator):
    """Test that KPIs handle edge cases properly."""
    # Negative revenue should still calculate
    roas = kpi_calculator.calculate_kpi(
        KPIMetric.ROAS,
        spend=100,
        revenue=-50
    )
    assert roas == -0.5
    
    # Very high CPC
    cpc = kpi_calculator.calculate_kpi(
        KPIMetric.CPC,
        spend=10000,
        clicks=1
    )
    assert cpc == 10000.0




