"""Tests for data normalization."""

import pytest
import pandas as pd
from datetime import date

from src.ingestion.normalizer import DataNormalizer
from src.models.enums import AdPlatform


@pytest.fixture
def tiktok_sample_data():
    """Sample TikTok CSV data."""
    return pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Campaign Name': ['Campaign A', 'Campaign B', 'Campaign A'],
        'Cost': ['$100.50', '$250.00', '$150.75'],
        'Impressions': [10000, 25000, 15000],
        'Clicks': [500, 1200, 750],
        'Conversions': [25, 60, 35],
        'Revenue': ['$500.00', '$1800.00', '$700.00']
    })


@pytest.fixture
def meta_sample_data():
    """Sample Meta CSV data."""
    return pd.DataFrame({
        'reporting_starts': ['2024-01-01', '2024-01-02'],
        'campaign_name': ['Meta Campaign 1', 'Meta Campaign 2'],
        'spend': [200.00, 350.00],
        'impressions': [20000, 35000],
        'link_clicks': [800, 1400],
        'actions:offsite_conversion.fb_pixel_purchase': [40, 70],
        'action_values:offsite_conversion.fb_pixel_purchase': [1200.00, 2100.00]
    })


@pytest.fixture
def column_mappings():
    """Column mappings for testing."""
    return {
        'tiktok': {
            'date': 'Date',
            'campaign': 'Campaign Name',
            'spend': 'Cost',
            'impressions': 'Impressions',
            'clicks': 'Clicks',
            'conversions': 'Conversions',
            'revenue': 'Revenue'
        },
        'meta': {
            'date': 'reporting_starts',
            'campaign': 'campaign_name',
            'spend': 'spend',
            'impressions': 'impressions',
            'clicks': 'link_clicks',
            'conversions': 'actions:offsite_conversion.fb_pixel_purchase',
            'revenue': 'action_values:offsite_conversion.fb_pixel_purchase'
        }
    }


def test_normalize_tiktok_data(tiktok_sample_data, column_mappings):
    """Test normalization of TikTok data."""
    normalizer = DataNormalizer(column_mappings)
    
    result = normalizer.normalize(tiktok_sample_data, AdPlatform.TIKTOK)
    
    assert len(result) == 3
    assert list(result.columns) == ['date', 'platform', 'campaign', 'spend', 'impressions', 'clicks', 'conversions', 'revenue']
    assert result['platform'].iloc[0] == 'tiktok'
    assert result['spend'].iloc[0] == 100.50
    assert result['campaign'].iloc[0] == 'Campaign A'


def test_normalize_meta_data(meta_sample_data, column_mappings):
    """Test normalization of Meta data."""
    normalizer = DataNormalizer(column_mappings)
    
    result = normalizer.normalize(meta_sample_data, AdPlatform.META)
    
    assert len(result) == 2
    assert result['platform'].iloc[0] == 'meta'
    assert result['spend'].iloc[0] == 200.00
    assert result['campaign'].iloc[0] == 'Meta Campaign 1'


def test_normalize_multiple(tiktok_sample_data, meta_sample_data, column_mappings):
    """Test normalization of multiple platform data."""
    normalizer = DataNormalizer(column_mappings)
    
    dataframes = [
        (tiktok_sample_data, AdPlatform.TIKTOK),
        (meta_sample_data, AdPlatform.META)
    ]
    
    result = normalizer.normalize_multiple(dataframes)
    
    assert len(result) == 5  # 3 TikTok + 2 Meta
    assert set(result['platform'].unique()) == {'tiktok', 'meta'}


def test_to_records(tiktok_sample_data, column_mappings):
    """Test conversion to AdRecord objects."""
    normalizer = DataNormalizer(column_mappings)
    
    normalized = normalizer.normalize(tiktok_sample_data, AdPlatform.TIKTOK)
    records = normalizer.to_records(normalized)
    
    assert len(records) == 3
    assert records[0].platform == AdPlatform.TIKTOK
    assert records[0].spend == 100.50
    assert isinstance(records[0].date, date)


def test_handle_missing_values(column_mappings):
    """Test handling of missing values."""
    data = pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02'],
        'Campaign Name': ['Campaign A', None],
        'Cost': ['$100.50', None],
        'Impressions': [10000, None],
        'Clicks': [500, None],
        'Conversions': [25, None],
        'Revenue': ['$500.00', None]
    })
    
    normalizer = DataNormalizer(column_mappings)
    result = normalizer.normalize(data, AdPlatform.TIKTOK)
    
    # Should handle missing values gracefully
    assert len(result) >= 1
    assert result['spend'].iloc[0] == 100.50


def test_clean_currency_values(column_mappings):
    """Test cleaning of currency values."""
    data = pd.DataFrame({
        'Date': ['2024-01-01'],
        'Campaign Name': ['Campaign A'],
        'Cost': ['$1,234.56'],
        'Impressions': [10000],
        'Clicks': [500],
        'Conversions': [25],
        'Revenue': ['$5,678.90']
    })
    
    normalizer = DataNormalizer(column_mappings)
    result = normalizer.normalize(data, AdPlatform.TIKTOK)
    
    assert result['spend'].iloc[0] == 1234.56
    assert result['revenue'].iloc[0] == 5678.90




