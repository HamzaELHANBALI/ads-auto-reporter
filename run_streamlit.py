#!/usr/bin/env python
"""
Launch the Streamlit Dashboard for Ads Auto-Reporting System.

This script:
1. Loads and processes CSV data
2. Launches a beautiful Streamlit dashboard
3. Provides interactive filtering and visualization
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import AdsReportingSystem
from src.config import Config
from src.dashboard.streamlit_dashboard import run_streamlit_dashboard
from src.utils.logger import setup_logger

def main():
    """Load data and run Streamlit dashboard."""
    
    # Setup logging
    log_file = Path("logs") / "streamlit_dashboard.log"
    log_file.parent.mkdir(exist_ok=True)
    setup_logger("ads_reporter", "INFO", log_file)
    
    print("\n" + "=" * 60)
    print("📊 Ads Auto-Reporting System - Streamlit Dashboard")
    print("=" * 60 + "\n")
    
    # Load configuration
    config_path = Path("config/config.yaml")
    config = Config.from_yaml(config_path)
    
    # Initialize system
    system = AdsReportingSystem(config)
    
    # Check for data
    csv_files = list(config.upload_path.glob("*.csv"))
    if not csv_files:
        # Try sample data
        sample_files = list(Path("tests/fixtures").glob("*.csv"))
        if sample_files:
            print("ℹ️  Using sample data from tests/fixtures/")
            csv_files = sample_files
        else:
            print("⚠️  No CSV files found!")
            print(f"   Please add CSV files to: {config.upload_path}")
            sys.exit(1)
    
    print(f"✓ Found {len(csv_files)} CSV files\n")
    
    # Load and process data
    print("Loading and processing data...")
    try:
        df = system.load_and_normalize_data(csv_files=csv_files)
        print(f"✓ Loaded {len(df)} records\n")
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        sys.exit(1)
    
    print("🚀 Launching Streamlit dashboard...")
    print("   Dashboard will open in your browser automatically")
    print("   URL: http://localhost:8501")
    print("\n" + "=" * 60 + "\n")
    
    # Run dashboard
    run_streamlit_dashboard(df)

if __name__ == "__main__":
    # Need to use streamlit run command
    import streamlit.web.cli as stcli
    import sys
    
    # Set up streamlit args
    sys.argv = ["streamlit", "run", __file__, "--server.port=8501", "--server.headless=true"]
    sys.exit(stcli.main())

