# Test Data Information

## 📁 Test CSV Files Generated

Three comprehensive test CSV files have been created in `data/uploads/`:

### 1. `test_tiktok_complete.csv`
**Platform**: TikTok  
**Records**: 42 (6 campaigns × 7 days)  
**Date Range**: October 1-7, 2024

**Campaigns Included**:
- **Holiday Sale 2024** - High-performing seasonal campaign
- **Brand Awareness Q4** - Lower ROAS, high impression campaign
- **New Product Launch** - Premium product, high CPP
- **Retargeting - Cart Abandoners** - Excellent ROAS (16x+), small budget
- **Influencer Collaboration** - Medium performance, viral potential
- **Budget Test Campaign** - Low budget, minimal conversions (tests alerts)

**Total Metrics**:
- Spend: ~$10,500
- Revenue: ~$74,000
- Conversions: ~2,800
- Average ROAS: ~7x

### 2. `test_meta_complete.csv`
**Platform**: Meta (Facebook/Instagram)  
**Records**: 42 (6 campaigns × 7 days)  
**Date Range**: October 1-7, 2024

**Campaigns Included**:
- **FB/IG - Dynamic Product Ads** - Standard e-commerce performance
- **Stories Engagement Campaign** - High engagement, moderate ROAS
- **Lead Generation - Newsletter** - Excellent ROAS (~17x)
- **Video Views Campaign** - Awareness campaign, lower conversions
- **Lookalike Audience Test** - High-performing audience targeting
- **Flash Sale - 24hr** through **Sunday Flash Deal** - Various promotional campaigns

**Total Metrics**:
- Spend: ~$11,500
- Revenue: ~$119,000
- Conversions: ~4,800
- Average ROAS: ~10x

### 3. `test_google_complete.csv`
**Platform**: Google Ads  
**Records**: 56 (8 campaigns × 7 days)  
**Date Range**: October 1-7, 2024

**Campaigns Included**:
- **Search - Brand Keywords** - High intent, premium traffic
- **Search - Generic Terms** - Broader reach, medium ROAS
- **Display Network - Remarketing** - Lower cost, retargeting
- **Shopping - Product Feed** - E-commerce, excellent ROAS
- **YouTube Video Ads** - Video advertising, awareness
- **Discovery Ads - New Feature** - Testing new ad format
- **Performance Max Campaign** - Automated campaign, high budget
- **Local Services Ads** - Local business targeting

**Total Metrics**:
- Spend: ~$18,500
- Revenue: ~$200,000
- Conversions: ~9,300
- Average ROAS: ~11x

## 📊 Combined Dataset Statistics

**Total Records**: 140  
**Total Spend**: $40,500  
**Total Revenue**: $393,000  
**Overall ROAS**: 9.7x  
**Total Conversions**: 16,900  
**Total Clicks**: 155,000  
**Total Impressions**: 6,750,000

## 🎯 What This Tests

### 1. **Platform Detection**
- Each CSV has different column names
- System automatically detects TikTok/Meta/Google format

### 2. **Data Quality Scenarios**
- ✅ High-performing campaigns (ROAS > 10x)
- ⚠️ Underperforming campaigns (ROAS < 2x)
- 🔴 Low budget campaigns with minimal results
- 📈 Various CPP ranges ($2-$50)
- 🎯 Different campaign objectives

### 3. **KPI Calculations**
- **ROAS**: Range from 2x to 19x across campaigns
- **CPC**: Range from $0.10 to $2.00
- **CPM**: Range from $1.50 to $25.00
- **CPP**: Range from $1.00 to $50.00
- **CTR**: Range from 1% to 8%
- **CVR**: Range from 2% to 10%

### 4. **Performance Alerts**
The test data will trigger various alerts:
- 🔴 **High Severity**: Budget Test Campaign (low ROAS, no conversions)
- 🟡 **Medium Severity**: Brand Awareness campaigns (below target ROAS)
- 🟢 **Good Performance**: Shopping, Lead Gen, Retargeting campaigns

### 5. **Week-over-Week Analysis**
Data spans 7 days allowing for:
- Daily trend analysis
- Weekly aggregation
- Performance consistency checks

## 🚀 How to Use

### Quick Test
```bash
# Run the complete system test
python test_full_system.py
```

This will:
1. Load all 3 CSV files
2. Normalize & validate data
3. Calculate all KPIs
4. Generate weekly digest
5. Export PDF reports
6. Show performance alerts
7. Display summary statistics

### Run Example Workflow
```bash
# Run with detailed output
python run_example.py
```

### Launch Interactive Dashboard
```bash
# View data in browser
python run_dashboard.py
# Then visit: http://localhost:8050
```

### Manual Testing
```python
from pathlib import Path
from src.main import AdsReportingSystem
from src.config import Config

# Initialize
config = Config.from_yaml('config/config.yaml')
system = AdsReportingSystem(config)

# Load test data
csv_files = [
    Path('data/uploads/test_tiktok_complete.csv'),
    Path('data/uploads/test_meta_complete.csv'),
    Path('data/uploads/test_google_complete.csv')
]

# Run pipeline
system.run_full_pipeline(
    csv_files=csv_files,
    export_pdf=True
)
```

## 📈 Expected Results

### Top Performing Campaigns (by ROAS)
1. **Lead Generation - Newsletter** (Meta) - ~17x ROAS
2. **Retargeting - Cart Abandoners** (TikTok) - ~16x ROAS
3. **Discovery Ads - New Feature** (Google) - ~19x ROAS
4. **Lookalike Audience Test** (Meta) - ~19x ROAS
5. **Shopping - Product Feed** (Google) - ~10x ROAS

### Campaigns That Will Trigger Alerts
1. **Budget Test Campaign** (TikTok) - Very low ROAS (~2x)
2. **Brand Awareness Q4** (TikTok) - Below target ROAS (~3.6x)
3. **Video Views Campaign** (Meta) - Lower conversions

### Platform Comparison
- **Google Ads**: Highest revenue, best overall performance
- **Meta**: Best engagement, high conversion rates
- **TikTok**: Most diverse performance, good retargeting results

## 🎨 Dashboard Visualizations

The test data will generate:
- **8 KPI Cards**: Spend, Revenue, ROAS, Conversions, CPC, CPP, CTR, CVR
- **Revenue vs Spend Chart**: 7-day time series
- **ROAS Trend**: Daily ROAS with target line
- **Platform Breakdown**: 3 pie charts (spend/revenue/conversions)
- **Conversion Funnel**: Impressions → Clicks → Conversions
- **Top Campaigns**: Bar charts comparing top 10 performers

## 📄 PDF Reports

Generated reports include:
- **Campaign Summary Report**: All campaigns with detailed metrics
- **Weekly Digest**: Executive summary with top performers and alerts
- **Performance Tables**: Sortable metrics by campaign/platform
- **Recommendations**: Based on performance thresholds

## ⚙️ Customization

### Modify Test Data
Edit the CSV files to test:
- Different date ranges
- Missing values
- Edge cases (zero spend, no conversions)
- Extreme metrics

### Adjust Thresholds
Edit `config/config.yaml`:
```yaml
kpis:
  target_roas: 3.0    # Adjust to see more/fewer alerts
  target_ctr: 0.02
  target_cvr: 0.05
  max_cpp: 50.0
```

### Add More Data
Simply add more rows to the CSV files or create new CSV files in `data/uploads/`

## 🐛 Troubleshooting

**Issue**: "No CSV files found"
- **Solution**: Make sure files are in `data/uploads/` directory

**Issue**: "Platform detection failed"
- **Solution**: Verify column names match the expected format

**Issue**: "PDF generation failed"
- **Solution**: Install missing dependencies: `pip install reportlab kaleido`

## 📚 Learn More

- See `README.md` for complete documentation
- Check `run_example.py` for usage examples
- Review `tests/` directory for unit tests
- Read `CHANGELOG.md` for version history




