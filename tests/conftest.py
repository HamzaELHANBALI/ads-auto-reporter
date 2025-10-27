"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def fixtures_dir():
    """Path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_csv_files(fixtures_dir):
    """Dictionary of sample CSV files."""
    return {
        'tiktok': fixtures_dir / 'sample_tiktok.csv',
        'meta': fixtures_dir / 'sample_meta.csv',
        'google': fixtures_dir / 'sample_google.csv'
    }




