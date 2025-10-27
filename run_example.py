#!/usr/bin/env python
"""
Example script demonstrating the Ads Auto-Reporting System.

This script shows how to:
1. Load sample CSV data
2. Normalize and validate data
3. Calculate KPIs
4. Generate reports
"""

from pathlib import Path
from datetime import date, timedelta

from src.main import AdsReportingSystem
from src.config import Config
from src.utils.logger import setup_logger

def main():
    """Run example workflow."""
    
    # Setup logging
    setup_logger("ads_reporter", "INFO")
    
    print("=" * 60)
    print("Ads Auto-Reporting System - Example Run")
    print("=" * 60)
    
    # Load configuration
    config_path = Path("config/config.yaml")
    config = Config.from_yaml(config_path)
    
    # Initialize system
    system = AdsReportingSystem(config)
    
    # Check for sample data
    sample_files = list(Path("tests/fixtures").glob("*.csv"))
    
    if not sample_files:
        print("\n⚠️  No sample CSV files found in tests/fixtures/")
        print("Please add some CSV files to data/uploads/ or tests/fixtures/")
        return
    
    print(f"\n✓ Found {len(sample_files)} sample CSV files")
    
    # Load and normalize data
    print("\n[1/4] Loading and normalizing data...")
    try:
        df = system.load_and_normalize_data(csv_files=sample_files)
        print(f"✓ Successfully loaded {len(df)} records")
        print(f"  - Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"  - Platforms: {', '.join(df['platform'].unique())}")
        print(f"  - Campaigns: {df['campaign'].nunique()}")
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return
    
    # Calculate KPIs
    print("\n[2/4] Calculating KPIs...")
    try:
        summaries = system.calculate_kpis()
        print(f"✓ Calculated KPIs for {len(summaries)} campaigns")
        
        # Show top 3 campaigns by revenue
        top_campaigns = sorted(summaries, key=lambda x: x.total_revenue, reverse=True)[:3]
        print("\n  Top 3 Campaigns by Revenue:")
        for i, campaign in enumerate(top_campaigns, 1):
            print(f"    {i}. {campaign.campaign} ({campaign.platform.value})")
            print(f"       Revenue: ${campaign.total_revenue:,.2f} | ROAS: {campaign.roas:.2f}x")
    except Exception as e:
        print(f"✗ Error calculating KPIs: {e}")
        return
    
    # Generate weekly digest
    print("\n[3/4] Generating weekly digest...")
    try:
        digest, pdf_path = system.generate_weekly_digest(export_pdf=True)
        print(f"✓ Generated digest for week of {digest.week_start}")
        print(f"  - Total Spend: ${digest.total_spend:,.2f}")
        print(f"  - Total Revenue: ${digest.total_revenue:,.2f}")
        print(f"  - Overall ROAS: {digest.overall_roas:.2f}x")
        print(f"  - Alerts: {len(digest.alerts)}")
        if pdf_path:
            print(f"  - PDF Report: {pdf_path}")
    except Exception as e:
        print(f"✗ Error generating digest: {e}")
        return
    
    # Export campaign summary
    print("\n[4/4] Exporting PDF report...")
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        pdf_path = system.export_pdf_report(
            start_date=start_date,
            end_date=end_date
        )
        print(f"✓ PDF report exported to: {pdf_path}")
    except Exception as e:
        print(f"✗ Error exporting PDF: {e}")
        return
    
    print("\n" + "=" * 60)
    print("✓ Example workflow completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Add your own CSV files to data/uploads/")
    print("2. Configure email settings in config/config.yaml")
    print("3. Run: python -m src.main")
    print("4. Or launch dashboard: python run_dashboard.py")
    print("")

if __name__ == "__main__":
    main()




