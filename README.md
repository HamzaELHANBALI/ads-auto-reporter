# 📊 Ads Auto-Reporting System v1.0

A production-ready, automated reporting system for multi-platform advertising campaigns (TikTok, Meta, Google Ads). Transform raw CSV data into actionable insights with automated KPI calculations, interactive dashboards, PDF reports, and weekly email digests.

## 🚀 Features

- **Multi-Platform Support**: TikTok, Meta (Facebook/Instagram), Google Ads
- **Intelligent Data Normalization**: Automatically detects and normalizes platform-specific CSV formats
- **Comprehensive KPI Calculations**: ROAS, CPC, CPM, CPP, CTR, CVR
- **Interactive Dashboard**: Real-time visualizations with Plotly & Dash
- **PDF Export**: Professional, multi-page reports with tables and charts
- **Weekly Email Digests**: Automated performance summaries with alerts
- **Data Validation**: Built-in quality checks and anomaly detection
- **Clean Architecture**: Modular, testable, and maintainable codebase

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Contributing](#contributing)

## 🔧 Installation

### Prerequisites

- Python 3.9+
- pip or conda
- (Optional) Docker for containerized deployment

### Standard Installation

```bash
# Clone the repository
git clone <repository-url>
cd ad_reporter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p data/{uploads,processed,outputs} logs
```

### Docker Installation

```bash
# Build the Docker image
docker-compose build

# Run the system
docker-compose up
```

## ⚡ Quick Start

### 1. Upload CSV Files

Place your ad platform CSV exports in the `data/uploads/` directory:

```
data/uploads/
├── tiktok_campaign_data.csv
├── meta_ads_export.csv
└── google_ads_report.csv
```

### 2. Configure Settings

Edit `config/config.yaml` to customize:
- KPI thresholds
- Email settings
- Report preferences

### 3. Run the System

```bash
# Run the full pipeline
python -m src.main

# Or use the interactive Python API
python
>>> from src.main import AdsReportingSystem
>>> from src.config import Config
>>> 
>>> config = Config.from_yaml('config/config.yaml')
>>> system = AdsReportingSystem(config)
>>> system.run_full_pipeline()
```

### 4. View Results

- **Processed Data**: `data/processed/normalized_data_YYYYMMDD.csv`
- **PDF Reports**: `data/outputs/weekly_digest_YYYYMMDD.pdf`
- **Logs**: `logs/ads_reporter_YYYYMMDD.log`

## 🏗️ Architecture

```
ads-auto-reporting/
├── src/                          # Source code
│   ├── models/                   # Data models & schemas
│   │   ├── enums.py             # Platform/metric enumerations
│   │   └── schemas.py           # Pydantic data models
│   ├── ingestion/               # Data loading & normalization
│   │   ├── csv_loader.py        # CSV file handling
│   │   ├── normalizer.py        # Multi-platform normalization
│   │   └── validator.py         # Data quality validation
│   ├── analytics/               # KPI calculation engine
│   │   ├── kpi_calculator.py   # KPI computation
│   │   └── aggregator.py        # Time-based aggregation
│   ├── dashboard/               # Visualization & export
│   │   ├── visualizer.py        # Interactive dashboard
│   │   └── export.py            # PDF generation
│   ├── reporting/               # Email & digests
│   │   ├── digest.py            # Weekly digest generator
│   │   └── email_sender.py      # Email dispatch
│   ├── utils/                   # Utilities
│   │   ├── logger.py            # Logging setup
│   │   └── helpers.py           # Helper functions
│   ├── config.py                # Configuration management
│   └── main.py                  # Main orchestration
├── tests/                        # Test suite
│   ├── test_normalizer.py
│   ├── test_kpi_calculator.py
│   ├── test_validator.py
│   └── fixtures/                # Sample data
├── config/
│   └── config.yaml              # System configuration
├── requirements.txt
└── README.md
```

## 📖 Usage Guide

### Data Ingestion

#### Upload CSV Files

```python
from pathlib import Path
from src.main import AdsReportingSystem
from src.config import Config

config = Config.from_yaml('config/config.yaml')
system = AdsReportingSystem(config)

# Option 1: Auto-scan uploads directory
df = system.load_and_normalize_data()

# Option 2: Specify files explicitly
csv_files = [
    Path('data/uploads/tiktok_data.csv'),
    Path('data/uploads/meta_data.csv')
]
df = system.load_and_normalize_data(csv_files=csv_files)
```

#### Platform-Specific CSV Formats

**TikTok CSV Format:**
```csv
Date,Campaign Name,Cost,Impressions,Clicks,Conversions,Revenue
2024-01-01,Summer Sale,$150.50,15000,750,38,$1140.00
```

**Meta CSV Format:**
```csv
reporting_starts,campaign_name,spend,impressions,link_clicks,actions:offsite_conversion.fb_pixel_purchase,action_values:offsite_conversion.fb_pixel_purchase
2024-01-01,Retargeting,180.00,20000,900,45,1350.00
```

**Google Ads CSV Format:**
```csv
Day,Campaign,Cost,Impr.,Clicks,Conv.,Conv. value
2024-01-01,Search - Brand,120.00,18000,600,30,900.00
```

### KPI Calculation

```python
# Calculate KPIs for all campaigns
summaries = system.calculate_kpis()

# Access individual campaign metrics
for summary in summaries:
    print(f"{summary.campaign}: ROAS={summary.roas:.2f}x, CPP=${summary.cpp:.2f}")

# Calculate specific KPI
from src.analytics import KPICalculator
from src.models.enums import KPIMetric

calculator = KPICalculator()
roas = calculator.calculate_kpi(
    KPIMetric.ROAS,
    spend=1000.0,
    revenue=3000.0
)
print(f"ROAS: {roas}x")  # Output: ROAS: 3.0x
```

### Dashboard Visualization

```python
# Create and launch interactive dashboard
system.create_dashboard(
    host='0.0.0.0',
    port=8050,
    run_server=True
)
# Access at http://localhost:8050
```

### PDF Report Export

```python
from datetime import date, timedelta

# Export last 30 days
end_date = date.today()
start_date = end_date - timedelta(days=30)

pdf_path = system.export_pdf_report(
    start_date=start_date,
    end_date=end_date,
    output_filename='monthly_report.pdf'
)
print(f"Report exported to: {pdf_path}")
```

### Weekly Email Digest

```python
from src.models.schemas import EmailConfig

# Configure email
email_config = EmailConfig(
    smtp_server='smtp.gmail.com',
    smtp_port=587,
    username='your_email@gmail.com',
    password='your_app_password',
    sender_email='your_email@gmail.com',
    recipients=['stakeholder1@company.com', 'stakeholder2@company.com']
)

# Send weekly digest
success = system.send_weekly_email(email_config)
```

## ⚙️ Configuration

### config/config.yaml

```yaml
system:
  project_name: "Ads Auto-Reporting System"
  log_level: "INFO"

data:
  upload_path: "data/uploads"
  processed_path: "data/processed"
  output_path: "data/outputs"

kpis:
  target_roas: 3.0      # Target Return on Ad Spend
  target_ctr: 0.02      # Target Click-Through Rate (2%)
  target_cvr: 0.05      # Target Conversion Rate (5%)
  max_cpp: 50.0         # Maximum Cost Per Purchase

dashboard:
  host: "127.0.0.1"
  port: 8050
  debug: false

email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  use_tls: true
  sender_name: "Ads Reporting System"

reporting:
  lookback_days: 30
  comparison_period_days: 7
```

### Environment Variables

For sensitive data, use environment variables:

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export EMAIL_USERNAME="your_email@gmail.com"
export EMAIL_PASSWORD="your_app_password"
```

Then in code:

```python
from src.reporting import EmailSender

email_sender = EmailSender.from_env(
    sender_email='your_email@gmail.com',
    recipients=['recipient@company.com']
)
```

## 📊 KPI Formulas

| KPI | Formula | Description |
|-----|---------|-------------|
| **ROAS** | `Revenue / Spend` | Return on Ad Spend |
| **CPC** | `Spend / Clicks` | Cost Per Click |
| **CPM** | `(Spend / Impressions) × 1000` | Cost Per Mille (1000 impressions) |
| **CPP** | `Spend / Conversions` | Cost Per Purchase/Conversion |
| **CTR** | `Clicks / Impressions` | Click-Through Rate |
| **CVR** | `Conversions / Clicks` | Conversion Rate |

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_kpi_calculator.py

# Run with verbose output
pytest -v
```

### Test Structure

```
tests/
├── test_normalizer.py      # Data normalization tests
├── test_kpi_calculator.py  # KPI calculation tests
├── test_validator.py       # Data validation tests
└── fixtures/               # Sample CSV data
    ├── sample_tiktok.csv
    ├── sample_meta.csv
    └── sample_google.csv
```

## 🔍 Data Validation

The system includes comprehensive validation:

- **Required Fields**: Date, campaign, spend, impressions, clicks, conversions, revenue
- **Negative Values**: Detects and flags negative metrics
- **Logical Consistency**: Clicks shouldn't exceed impressions
- **Anomaly Detection**: High CPC, zero spend with activity
- **Duplicate Detection**: Same date/platform/campaign combinations

Example validation output:

```
[WARNING] Campaign 'Summer Sale' has ROAS of 1.5x, below target of 3.0x
[ERROR] Campaign 'Brand Awareness' - Clicks (2000) exceeds impressions (1000)
[WARNING] Campaign 'Product Launch' has unusually high CPC: $15.50
```

## 📧 Email Digest Features

The weekly digest includes:

- **Executive Summary**: Total spend, revenue, ROAS with week-over-week changes
- **Top Performers**: Best campaigns by revenue
- **Performance Alerts**: Underperforming campaigns and anomalies
- **Platform Breakdown**: Performance by advertising platform
- **PDF Attachment**: Detailed report with visualizations

## 🐛 Troubleshooting

### Common Issues

**Issue**: CSV files not loading
```
Solution: Check file encoding (try UTF-8, Latin-1)
- Verify column names match expected format
- Check for empty rows or malformed data
```

**Issue**: Dashboard not starting
```
Solution: Check if port 8050 is available
- Try different port: system.create_dashboard(port=8051)
- Check firewall settings
```

**Issue**: Email not sending
```
Solution: Verify SMTP credentials
- Use app-specific password for Gmail
- Check TLS/SSL settings
- Test connection: email_sender.test_connection()
```

## 📚 API Reference

### Main Classes

#### `AdsReportingSystem`
Main orchestration class for the entire workflow.

```python
system = AdsReportingSystem(config)
system.load_and_normalize_data()
system.calculate_kpis()
system.create_dashboard()
system.export_pdf_report()
system.send_weekly_email(email_config)
```

#### `KPICalculator`
Calculate performance metrics.

```python
calculator = KPICalculator()
roas = calculator.calculate_kpi(KPIMetric.ROAS, spend=100, revenue=300)
```

#### `DataNormalizer`
Normalize multi-platform CSV data.

```python
normalizer = DataNormalizer(column_mappings)
df = normalizer.normalize(raw_df, AdPlatform.TIKTOK)
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all public methods
- Write tests for new features

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with Python, Pandas, Plotly, Dash
- PDF generation with ReportLab
- Validation with Pydantic

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: support@adsreporting.com
- Documentation: https://docs.adsreporting.com

---

**Version**: 1.0.0  
**Last Updated**: October 2024  
**Status**: Production Ready ✅




