"""
Streamlit App - Entry point for the beautiful dashboard.
Run with: streamlit run streamlit_app.py
"""

from pathlib import Path
import sys
import tempfile
import io

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
from src.main import AdsReportingSystem
from src.config import Config
from src.dashboard.streamlit_dashboard import run_streamlit_dashboard
from src.utils.logger import setup_logger

# Cache data loading
@st.cache_data
def load_data_from_files(csv_files):
    """Load and process ad data from file paths."""
    # Setup logging
    log_file = Path("logs") / "streamlit_dashboard.log"
    log_file.parent.mkdir(exist_ok=True)
    setup_logger("ads_reporter", "INFO", log_file)
    
    # Load configuration
    config_path = Path("config/config.yaml")
    config = Config.from_yaml(config_path)
    
    # Initialize system
    system = AdsReportingSystem(config)
    
    # Load and process data
    df = system.load_and_normalize_data(csv_files=csv_files)
    return df

def load_data_from_uploads(uploaded_files):
    """Load and process ad data from uploaded files."""
    # Setup logging
    log_file = Path("logs") / "streamlit_dashboard.log"
    log_file.parent.mkdir(exist_ok=True)
    setup_logger("ads_reporter", "INFO", log_file)
    
    # Load configuration
    config_path = Path("config/config.yaml")
    config = Config.from_yaml(config_path)
    
    # Initialize system
    system = AdsReportingSystem(config)
    
    # Save uploaded files to temp directory
    temp_files = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for uploaded_file in uploaded_files:
            temp_path = Path(tmpdir) / uploaded_file.name
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            temp_files.append(temp_path)
        
        # Load and process data
        df = system.load_and_normalize_data(csv_files=temp_files)
    
    return df

# Main app
def main():
    st.set_page_config(
        page_title="Ads Performance Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Sidebar for file upload
    with st.sidebar:
        st.title("📁 Data Source")
        
        data_source = st.radio(
            "Choose data source:",
            ["📊 Use Sample Data", "📤 Upload CSV Files"]
        )
        
        if data_source == "📤 Upload CSV Files":
            st.markdown("---")
            st.subheader("Upload Your CSV Files")
            st.info("Upload CSV exports from TikTok, Meta, or Google Ads")
            
            uploaded_files = st.file_uploader(
                "Choose CSV files",
                type=['csv'],
                accept_multiple_files=True,
                help="You can upload multiple CSV files at once"
            )
            
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
                for file in uploaded_files:
                    st.write(f"- {file.name}")
            else:
                st.warning("⚠️ Please upload at least one CSV file")
        else:
            st.info("📊 Currently showing sample data")
            st.caption("Switch to 'Upload CSV Files' to use your own data")
    
    # Load data based on source
    df = None
    
    if data_source == "📤 Upload CSV Files":
        if uploaded_files:
            with st.spinner("Processing uploaded files..."):
                try:
                    df = load_data_from_uploads(uploaded_files)
                    st.sidebar.success(f"✅ Loaded {len(df)} records")
                except Exception as e:
                    st.error(f"❌ Error processing files: {str(e)}")
                    st.info("Please check that your CSV files are in the correct format")
                    st.stop()
        else:
            st.warning("⚠️ Please upload CSV files using the sidebar")
            st.info("**Supported formats:**\n- TikTok Ads CSV export\n- Meta (Facebook/Instagram) Ads CSV export\n- Google Ads CSV export")
            st.stop()
    else:
        # Use sample/existing data
        with st.spinner("Loading sample data..."):
            config_path = Path("config/config.yaml")
            config = Config.from_yaml(config_path)
            
            # Check for data
            csv_files = list(config.upload_path.glob("*.csv"))
            if not csv_files:
                # Try sample data
                sample_files = list(Path("tests/fixtures").glob("*.csv"))
                if sample_files:
                    csv_files = sample_files
            
            if not csv_files:
                st.error("⚠️ No sample data found!")
                st.info("Please upload your own CSV files")
                st.stop()
            
            df = load_data_from_files(csv_files)
    
    # Run dashboard
    if df is not None and not df.empty:
        run_streamlit_dashboard(df)
    else:
        st.error("No data to display")

if __name__ == "__main__":
    main()

