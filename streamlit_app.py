"""
Streamlit App - Entry point for the beautiful dashboard.
Run with: streamlit run streamlit_app.py
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from src.main import AdsReportingSystem
from src.config import Config
from src.dashboard.streamlit_dashboard import run_streamlit_dashboard
from src.utils.logger import setup_logger

# Cache data loading
@st.cache_data
def load_data():
    """Load and process ad data."""
    # Setup logging
    log_file = Path("logs") / "streamlit_dashboard.log"
    log_file.parent.mkdir(exist_ok=True)
    setup_logger("ads_reporter", "INFO", log_file)
    
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
            csv_files = sample_files
    
    if not csv_files:
        return None
    
    # Load and process data
    df = system.load_and_normalize_data(csv_files=csv_files)
    return df

# Main app
def main():
    # Load data
    with st.spinner("Loading ad performance data..."):
        df = load_data()
    
    if df is None:
        st.error("⚠️ No CSV files found! Please add CSV files to data/uploads/")
        st.info("Expected CSV format: TikTok, Meta (Facebook/Instagram), or Google Ads exports")
        st.stop()
    
    # Run dashboard
    run_streamlit_dashboard(df)

if __name__ == "__main__":
    main()

