#!/usr/bin/env python
"""
Launch the interactive dashboard for Ads Auto-Reporting System.

This script:
1. Loads sample or uploaded CSV data
2. Processes and normalizes the data
3. Launches an interactive dashboard on http://localhost:8050
"""

from pathlib import Path
import sys

from src.main import AdsReportingSystem
from src.config import Config
from src.utils.logger import setup_logger

def main():
    """Launch the dashboard."""
    
    # Setup logging
    log_file = Path("logs") / "dashboard.log"
    log_file.parent.mkdir(exist_ok=True)
    setup_logger("ads_reporter", "INFO", log_file)
    
    print("\n" + "=" * 60)
    print("Ads Auto-Reporting System - Interactive Dashboard")
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
    
    # Launch dashboard
    host = config.dashboard_host
    port = config.dashboard_port
    
    print("Launching dashboard...")
    print(f"\n🚀 Dashboard will be available at: http://{host}:{port}")
    print("\nPress Ctrl+C to stop the dashboard\n")
    print("=" * 60 + "\n")
    
    try:
        system.create_dashboard(
            host=host,
            port=port,
            run_server=True
        )
    except KeyboardInterrupt:
        print("\n\n✓ Dashboard stopped")
    except Exception as e:
        print(f"\n✗ Error running dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()




