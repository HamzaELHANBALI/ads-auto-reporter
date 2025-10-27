"""
Main entry point for the Ads Auto-Reporting System.

This orchestrates the entire workflow:
1. CSV upload and normalization
2. KPI calculation
3. Dashboard generation
4. PDF export
5. Weekly digest email
"""

import sys
from pathlib import Path
from typing import List, Optional
from datetime import date, timedelta
import pandas as pd

from .config import Config, get_config, set_config
from .models.enums import AdPlatform, ReportPeriod
from .ingestion import CSVLoader, DataNormalizer, DataValidator
from .analytics import KPICalculator, DataAggregator
from .dashboard import PDFExporter
from .reporting import DigestGenerator, EmailSender
from .models.schemas import EmailConfig
from .utils.logger import setup_logger, get_logger
from .utils.helpers import generate_report_filename

logger = get_logger(__name__)


class AdsReportingSystem:
    """
    Main orchestration class for the Ads Auto-Reporting System.
    
    Workflow:
    1. Load and normalize CSV data from multiple platforms
    2. Validate data quality
    3. Calculate KPIs and generate summaries
    4. Create interactive dashboard
    5. Export PDF reports
    6. Send weekly email digests
    """
    
    def __init__(self, config: Config):
        """
        Initialize the reporting system.
        
        Args:
            config: System configuration
        """
        self.config = config
        self.config.ensure_directories()
        
        # Initialize components
        self.csv_loader = CSVLoader(config.upload_path)
        self.normalizer = DataNormalizer(config.column_mappings)
        self.validator = DataValidator()
        self.kpi_calculator = KPICalculator()
        self.aggregator = DataAggregator()
        self.pdf_exporter = PDFExporter(config.output_path)
        self.digest_generator = DigestGenerator(
            target_roas=config.target_roas,
            target_ctr=config.target_ctr,
            target_cvr=config.target_cvr,
            max_cpp=config.max_cpp
        )
        
        self.normalized_df: Optional[pd.DataFrame] = None
        
        logger.info("Ads Reporting System initialized")
    
    def load_and_normalize_data(
        self,
        csv_files: Optional[List[Path]] = None,
        auto_scan: bool = True
    ) -> pd.DataFrame:
        """
        Load CSV files and normalize to standard schema.
        
        Args:
            csv_files: List of CSV file paths (if None, auto-scan upload directory)
            auto_scan: Automatically scan upload directory if no files provided
            
        Returns:
            Normalized DataFrame
        """
        logger.info("Starting data ingestion and normalization")
        
        # Get CSV files
        if csv_files is None and auto_scan:
            csv_files = self.csv_loader.scan_upload_directory()
            if not csv_files:
                raise ValueError(f"No CSV files found in {self.config.upload_path}")
        elif csv_files is None:
            raise ValueError("No CSV files provided and auto_scan disabled")
        
        logger.info(f"Processing {len(csv_files)} CSV files")
        
        # Load all CSV files
        loaded_data = []
        for file_path in csv_files:
            try:
                df, platform = self.csv_loader.load_csv(file_path)
                loaded_data.append((df, platform))
                logger.info(f"Loaded {file_path.name} ({platform.value})")
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                continue
        
        if not loaded_data:
            raise ValueError("No files successfully loaded")
        
        # Normalize data
        self.normalized_df = self.normalizer.normalize_multiple(loaded_data)
        
        # Validate data
        is_valid, errors = self.validator.validate_dataframe(self.normalized_df)
        
        if not is_valid:
            error_summary = self.validator.get_summary(errors)
            logger.warning(
                f"Data validation found {error_summary['errors']} errors, "
                f"{error_summary['warnings']} warnings"
            )
            # Log first few errors
            for error in errors[:5]:
                logger.warning(str(error))
        
        # Save processed data
        processed_file = self.config.processed_path / f"normalized_data_{date.today().strftime('%Y%m%d')}.csv"
        self.normalized_df.to_csv(processed_file, index=False)
        logger.info(f"Saved normalized data to {processed_file}")
        
        return self.normalized_df
    
    def calculate_kpis(self) -> List:
        """
        Calculate KPIs for all campaigns.
        
        Returns:
            List of CampaignSummary objects
        """
        if self.normalized_df is None:
            raise RuntimeError("No data loaded. Call load_and_normalize_data() first.")
        
        logger.info("Calculating KPIs")
        
        summaries = self.kpi_calculator.calculate_multiple_campaigns(self.normalized_df)
        
        logger.info(f"Calculated KPIs for {len(summaries)} campaigns")
        
        return summaries
    
    def create_dashboard(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        run_server: bool = True
    ):
        """
        Create and optionally run interactive dashboard.
        
        Note: Legacy Dash dashboard. Use Streamlit version instead (streamlit_app.py)
        
        Args:
            host: Dashboard host (uses config if None)
            port: Dashboard port (uses config if None)
            run_server: Whether to run the server
        """
        logger.warning("Legacy Dash dashboard is deprecated. Use 'streamlit run streamlit_app.py' instead.")
        raise NotImplementedError(
            "Dash dashboard has been replaced with Streamlit. "
            "Run: streamlit run streamlit_app.py"
        )
    
    def export_pdf_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Export campaign summary report to PDF.
        
        Args:
            start_date: Report start date (defaults to 30 days ago)
            end_date: Report end date (defaults to today)
            output_filename: Custom filename
            
        Returns:
            Path to generated PDF
        """
        if self.normalized_df is None:
            raise RuntimeError("No data loaded. Call load_and_normalize_data() first.")
        
        # Default date range
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=self.config.lookback_days)
        
        logger.info(f"Exporting PDF report for {start_date} to {end_date}")
        
        # Filter data to date range
        filtered_df = self.aggregator.filter_date_range(
            self.normalized_df,
            start_date,
            end_date
        )
        
        # Calculate summaries
        summaries = self.kpi_calculator.calculate_multiple_campaigns(filtered_df)
        
        # Export to PDF
        pdf_path = self.pdf_exporter.export_campaign_summary(
            summaries,
            start_date,
            end_date,
            output_filename
        )
        
        logger.info(f"PDF report exported to {pdf_path}")
        return pdf_path
    
    def generate_weekly_digest(
        self,
        week_end_date: Optional[date] = None,
        export_pdf: bool = True
    ) -> tuple:
        """
        Generate weekly performance digest.
        
        Args:
            week_end_date: End date of the week (defaults to today)
            export_pdf: Whether to export PDF
            
        Returns:
            Tuple of (WeeklyDigest, pdf_path or None)
        """
        if self.normalized_df is None:
            raise RuntimeError("No data loaded. Call load_and_normalize_data() first.")
        
        logger.info("Generating weekly digest")
        
        # Generate digest
        digest = self.digest_generator.generate_weekly_digest(
            self.normalized_df,
            week_end_date
        )
        
        # Export to PDF
        pdf_path = None
        if export_pdf:
            pdf_path = self.pdf_exporter.export_weekly_digest(
                digest,
                digest.top_campaigns
            )
            logger.info(f"Weekly digest PDF: {pdf_path}")
        
        return digest, pdf_path
    
    def send_weekly_email(
        self,
        email_config: EmailConfig,
        week_end_date: Optional[date] = None
    ) -> bool:
        """
        Generate and send weekly digest email.
        
        Args:
            email_config: Email configuration
            week_end_date: End date of the week
            
        Returns:
            True if email sent successfully
        """
        logger.info("Preparing weekly email digest")
        
        # Generate digest and PDF
        digest, pdf_path = self.generate_weekly_digest(week_end_date, export_pdf=True)
        
        # Generate HTML body
        html_body = self.digest_generator.generate_html_summary(digest)
        
        # Send email
        email_sender = EmailSender(email_config)
        
        subject = f"Weekly Ads Performance Digest - {digest.week_start.strftime('%b %d')} to {digest.week_end.strftime('%b %d, %Y')}"
        
        success = email_sender.send_weekly_digest(
            subject=subject,
            html_body=html_body,
            pdf_path=pdf_path
        )
        
        if success:
            logger.info("Weekly email sent successfully")
        else:
            logger.error("Failed to send weekly email")
        
        return success
    
    def run_full_pipeline(
        self,
        csv_files: Optional[List[Path]] = None,
        email_config: Optional[EmailConfig] = None,
        generate_dashboard: bool = False,
        export_pdf: bool = True,
        send_email: bool = False
    ):
        """
        Run the complete reporting pipeline.
        
        Args:
            csv_files: CSV files to process
            email_config: Email configuration for digest
            generate_dashboard: Whether to create dashboard
            export_pdf: Whether to export PDF
            send_email: Whether to send email digest
        """
        logger.info("=" * 60)
        logger.info("Starting Ads Auto-Reporting Pipeline")
        logger.info("=" * 60)
        
        try:
            # Step 1: Load and normalize data
            logger.info("\n[1/5] Loading and normalizing data...")
            self.load_and_normalize_data(csv_files)
            logger.info(f"✓ Loaded {len(self.normalized_df)} records")
            
            # Step 2: Calculate KPIs
            logger.info("\n[2/5] Calculating KPIs...")
            summaries = self.calculate_kpis()
            logger.info(f"✓ Calculated KPIs for {len(summaries)} campaigns")
            
            # Step 3: Generate dashboard (optional)
            if generate_dashboard:
                logger.info("\n[3/5] Creating dashboard...")
                self.create_dashboard(run_server=False)
                logger.info("✓ Dashboard created (not started)")
            else:
                logger.info("\n[3/5] Skipping dashboard creation")
            
            # Step 4: Export PDF (optional)
            if export_pdf:
                logger.info("\n[4/5] Exporting PDF report...")
                pdf_path = self.export_pdf_report()
                logger.info(f"✓ PDF exported: {pdf_path}")
            else:
                logger.info("\n[4/5] Skipping PDF export")
            
            # Step 5: Send email (optional)
            if send_email and email_config:
                logger.info("\n[5/5] Sending weekly email digest...")
                success = self.send_weekly_email(email_config)
                if success:
                    logger.info("✓ Email sent successfully")
                else:
                    logger.error("✗ Email sending failed")
            else:
                logger.info("\n[5/5] Skipping email sending")
            
            logger.info("\n" + "=" * 60)
            logger.info("Pipeline completed successfully!")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"\n✗ Pipeline failed: {e}", exc_info=True)
            raise


def main():
    """Main entry point for CLI usage."""
    # Load configuration
    config_path = Path("config/config.yaml")
    config = Config.from_yaml(config_path)
    set_config(config)
    
    # Setup logging
    log_file = Path("logs") / f"ads_reporter_{date.today().strftime('%Y%m%d')}.log"
    log_file.parent.mkdir(exist_ok=True)
    setup_logger("ads_reporter", config.log_level, log_file)
    
    logger.info("Starting Ads Auto-Reporting System")
    
    # Initialize system
    system = AdsReportingSystem(config)
    
    # Run pipeline
    # Note: Email config should be loaded from environment or secure storage
    system.run_full_pipeline(
        csv_files=None,  # Auto-scan
        email_config=None,  # Skip email for now
        generate_dashboard=False,
        export_pdf=True,
        send_email=False
    )


if __name__ == "__main__":
    main()




