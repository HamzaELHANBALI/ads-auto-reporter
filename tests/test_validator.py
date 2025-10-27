"""Tests for data validation."""

import pytest
import pandas as pd
from datetime import date, timedelta

from src.ingestion.validator import DataValidator


@pytest.fixture
def valid_data():
    """Valid normalized data."""
    return pd.DataFrame({
        'date': [date.today(), date.today() - timedelta(days=1)],
        'platform': ['tiktok', 'meta'],
        'campaign': ['Campaign A', 'Campaign B'],
        'spend': [100.0, 200.0],
        'impressions': [10000, 20000],
        'clicks': [500, 1000],
        'conversions': [25, 50],
        'revenue': [300.0, 600.0]
    })


@pytest.fixture
def validator():
    """Data validator instance."""
    return DataValidator()


def test_validate_valid_data(validator, valid_data):
    """Test validation of valid data."""
    is_valid, errors = validator.validate_dataframe(valid_data)
    
    assert is_valid
    assert len(errors) == 0


def test_validate_empty_dataframe(validator):
    """Test validation of empty dataframe."""
    df = pd.DataFrame()
    is_valid, errors = validator.validate_dataframe(df)
    
    assert not is_valid
    assert len(errors) > 0
    assert any('empty' in str(e).lower() for e in errors)


def test_validate_missing_columns(validator):
    """Test validation with missing required columns."""
    df = pd.DataFrame({
        'date': [date.today()],
        'campaign': ['Campaign A']
        # Missing other required columns
    })
    
    is_valid, errors = validator.validate_dataframe(df)
    
    assert not is_valid
    assert any('missing' in str(e).lower() for e in errors)


def test_validate_negative_values(validator):
    """Test validation catches negative values."""
    df = pd.DataFrame({
        'date': [date.today()],
        'platform': ['tiktok'],
        'campaign': ['Campaign A'],
        'spend': [-100.0],  # Negative!
        'impressions': [10000],
        'clicks': [500],
        'conversions': [25],
        'revenue': [300.0]
    })
    
    is_valid, errors = validator.validate_dataframe(df)
    
    assert not is_valid
    assert any('negative' in str(e).lower() for e in errors)


def test_validate_clicks_exceed_impressions(validator):
    """Test validation catches logical inconsistency."""
    df = pd.DataFrame({
        'date': [date.today()],
        'platform': ['tiktok'],
        'campaign': ['Campaign A'],
        'spend': [100.0],
        'impressions': [1000],
        'clicks': [2000],  # More clicks than impressions!
        'conversions': [25],
        'revenue': [300.0]
    })
    
    is_valid, errors = validator.validate_dataframe(df)
    
    assert not is_valid
    assert any('clicks' in str(e).lower() and 'impressions' in str(e).lower() for e in errors)


def test_validate_conversions_exceed_clicks(validator):
    """Test warning for conversions exceeding clicks."""
    df = pd.DataFrame({
        'date': [date.today()],
        'platform': ['tiktok'],
        'campaign': ['Campaign A'],
        'spend': [100.0],
        'impressions': [10000],
        'clicks': [100],
        'conversions': [150],  # More conversions than clicks!
        'revenue': [300.0]
    })
    
    is_valid, errors = validator.validate_dataframe(df)
    
    # Should have warnings
    assert any('conversions' in str(e).lower() for e in errors)


def test_validate_high_cpc(validator):
    """Test warning for unusually high CPC."""
    df = pd.DataFrame({
        'date': [date.today()],
        'platform': ['tiktok'],
        'campaign': ['Campaign A'],
        'spend': [10000.0],  # Very high spend
        'impressions': [10000],
        'clicks': [10],  # Very low clicks -> high CPC
        'conversions': [1],
        'revenue': [100.0]
    })
    
    is_valid, errors = validator.validate_dataframe(df)
    
    # Should have CPC warning
    assert any('cpc' in str(e).lower() for e in errors)


def test_validate_duplicate_records(validator):
    """Test detection of duplicate records."""
    df = pd.DataFrame({
        'date': [date.today(), date.today()],  # Same date
        'platform': ['tiktok', 'tiktok'],  # Same platform
        'campaign': ['Campaign A', 'Campaign A'],  # Same campaign
        'spend': [100.0, 100.0],
        'impressions': [10000, 10000],
        'clicks': [500, 500],
        'conversions': [25, 25],
        'revenue': [300.0, 300.0]
    })
    
    is_valid, errors = validator.validate_dataframe(df)
    
    # Should have duplicate warning
    assert any('duplicate' in str(e).lower() for e in errors)


def test_validate_zero_spend_with_activity(validator):
    """Test warning for zero spend but has impressions/clicks."""
    df = pd.DataFrame({
        'date': [date.today()],
        'platform': ['tiktok'],
        'campaign': ['Campaign A'],
        'spend': [0.0],  # Zero spend
        'impressions': [10000],  # But has impressions
        'clicks': [500],  # And clicks
        'conversions': [0],
        'revenue': [0.0]
    })
    
    is_valid, errors = validator.validate_dataframe(df)
    
    # Should have warning about zero spend with activity
    assert any('zero spend' in str(e).lower() for e in errors)


def test_get_summary(validator, valid_data):
    """Test error summary generation."""
    df = pd.DataFrame({
        'date': [date.today()],
        'platform': ['tiktok'],
        'campaign': ['Campaign A'],
        'spend': [-100.0],  # Error: negative
        'impressions': [1000],
        'clicks': [2000],  # Error: exceeds impressions
        'conversions': [25],
        'revenue': [300.0]
    })
    
    is_valid, errors = validator.validate_dataframe(df)
    summary = validator.get_summary(errors)
    
    assert 'total' in summary
    assert 'errors' in summary
    assert 'warnings' in summary
    assert summary['errors'] >= 2


def test_validate_date_range(validator):
    """Test date range validation."""
    min_date = date(2024, 1, 1)
    max_date = date(2024, 12, 31)
    validator_with_dates = DataValidator(min_date=min_date, max_date=max_date)
    
    # Date outside range
    df = pd.DataFrame({
        'date': [date(2023, 1, 1)],  # Before min_date
        'platform': ['tiktok'],
        'campaign': ['Campaign A'],
        'spend': [100.0],
        'impressions': [10000],
        'clicks': [500],
        'conversions': [25],
        'revenue': [300.0]
    })
    
    is_valid, errors = validator_with_dates.validate_dataframe(df)
    
    # Should have date warning
    assert any('date' in str(e).lower() for e in errors)




