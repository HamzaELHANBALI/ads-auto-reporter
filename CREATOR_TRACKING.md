# 👤 Creator & Video Performance Tracking

## Overview

The Ads Auto-Reporter now supports tracking individual content creators and their video performance. This feature allows employers to monitor which content creators (employees, freelancers, or influencers) are driving the best results.

---

## 🎯 Use Cases

- **Agency Teams**: Track performance of different video editors/creators
- **Influencer Campaigns**: Monitor which influencers drive best ROI
- **Employee Performance**: See which team members create the most effective ads
- **Video Testing**: Compare performance across different video creatives

---

## 📊 How to Enable Creator Tracking

### Step 1: Add Creator Columns to Your CSV

Simply add one or more of these optional columns to your CSV exports:

| Column Name | Description | Example |
|------------|-------------|---------|
| `creator_name` | Name of the content creator/employee | "John Doe", "Sarah Marketing" |
| `video_id` | Unique identifier for the video | "VID_12345", "ad_creative_001" |
| `video_name` | Descriptive name/title of the video | "Summer Sale Promo", "Product Demo V2" |
| `ad_set_name` | Ad set grouping (optional) | "Retargeting Ads", "Prospecting" |
| `creative_type` | Type of creative (optional) | "video", "image", "carousel" |

### Step 2: CSV Format Example

```csv
date,platform,campaign,creator_name,video_name,spend,impressions,clicks,conversions,revenue
2024-10-01,tiktok,Fall Campaign,John Doe,Product Demo V1,150.00,50000,2500,125,750.00
2024-10-01,meta,Fall Campaign,Sarah Smith,Customer Testimonial,200.00,75000,3000,150,900.00
2024-10-02,tiktok,Fall Campaign,John Doe,Product Demo V2,175.00,60000,3200,180,1080.00
```

---

## 📈 What You Get

Once you upload a CSV with creator data, a new **"👤 Creators"** tab will automatically appear in the dashboard with:

### 🏆 Top Creators Leaderboard
- **Horizontal bar charts** showing Revenue vs Spend per creator
- **Sortable by**: ROAS, Revenue, Conversions, CTR, CVR
- **Color-coded performance** indicators (🟢 Excellent, 🟡 Good, 🔴 Needs Work)
- **Platform breakdown** - see which platforms each creator uses
- **Best video** - automatically identifies each creator's top-performing video

### 📊 Creator Performance Table
Shows for each creator:
- Number of videos created
- ROAS (Return on Ad Spend)
- Total Revenue & Spend
- Click-through Rate (CTR)
- Platforms used
- Best performing video

### 🎬 Top Performing Videos
- **Filterable by creator** - focus on one person's work
- **Sortable metrics**: ROAS, Revenue, Conversions
- **Shows**:
  - Video name
  - Creator
  - Platform
  - Performance metrics (ROAS, Revenue, Spend, CTR)
  - Days active
- **Adjustable count** - view top 5 to 50 videos

### 📥 Export Options
- Export Creator Performance (CSV)
- Export Video Performance (CSV)
- All data includes timestamps for tracking over time

---

## 🎬 Platform-Specific Instructions

### TikTok Ads

When exporting from TikTok Ads Manager:

1. Go to **Reports** → **Custom Report**
2. Add these columns to your export:
   - Date
   - Campaign Name
   - **Creative Name** (maps to `video_name`)
   - **Creative ID** (maps to `video_id`)
   - Spend, Impressions, Clicks, Conversions, Revenue
3. Manually add a `creator_name` column after export (Excel/Google Sheets)

### Meta (Facebook/Instagram)

When exporting from Meta Ads Manager:

1. Go to **Ads Manager** → **Reports**
2. Columns to include:
   - Reporting starts
   - Campaign name
   - **Ad name** (can map to `video_name`)
   - **Ad ID** (can map to `video_id`)
   - Amount spent, Impressions, Link clicks, Conversions, Purchase value
3. Add `creator_name` column manually or use **custom fields** if you've set them up

### Google Ads

1. Go to **Campaigns** → **Download**
2. Include:
   - Day
   - Campaign
   - **Ad** (maps to `video_name`)
   - Cost, Impr., Clicks, Conv., Conv. value
3. Add `creator_name` as a custom column

---

## 💡 Best Practices

### Naming Conventions

✅ **Good creator names:**
- "John Doe"
- "sarah_video_team"
- "Creator_JD"

❌ **Avoid:**
- Empty or missing names
- Generic names like "Team" or "Video"
- Inconsistent spelling (use same name across all rows)

### Video Tracking

✅ **Good video names:**
- "Product Demo - Version 2"
- "Testimonial_Customer_ABC"
- "Holiday_Sale_2024_V1"

❌ **Avoid:**
- Very long names (will be truncated in display)
- Special characters that break CSV parsing
- Duplicate names for different videos (use version numbers)

### Workflow Recommendation

1. **Set up naming standards** with your team first
2. **Use a spreadsheet** to maintain creator→video mappings
3. **Export raw data** from ad platforms
4. **Merge creator column** using VLOOKUP or similar
5. **Upload to dashboard**

---

## 📋 Sample CSV Template

Download or create a CSV with this structure:

```csv
date,platform,campaign,creator_name,video_id,video_name,spend,impressions,clicks,conversions,revenue
2024-10-01,tiktok,Q4_Campaign,Alice_Marketing,VID001,Holiday_Promo_V1,250.00,100000,5000,250,1500.00
2024-10-01,meta,Q4_Campaign,Bob_Creative,VID002,Product_Demo,300.00,150000,6000,300,1800.00
2024-10-02,tiktok,Q4_Campaign,Alice_Marketing,VID003,Holiday_Promo_V2,275.00,110000,5500,290,1740.00
2024-10-02,google,Q4_Campaign,Charlie_Design,VID004,Testimonial_1,200.00,80000,4000,200,1200.00
```

---

## 🔍 Features

### Automatic Detection
The dashboard automatically detects if your CSV has creator/video columns and shows the Creators tab only when data is available.

### Backward Compatible
Old CSVs without creator columns will still work perfectly - the Creators tab simply won't appear.

### Flexible Column Requirements
- **Minimum**: Just add `creator_name` to track creators
- **Recommended**: Add `creator_name` + (`video_name` OR `video_id`)
- **Full**: Add all optional columns for maximum insights

---

## ❓ FAQ

**Q: Do I need all the optional columns?**  
A: No! Just `creator_name` alone will enable creator tracking. Video columns are optional but recommended.

**Q: Can I have multiple creators per video?**  
A: Not currently - each row should have one creator. If a video is a collaboration, you could use "Alice & Bob" as the creator name.

**Q: What if I only want to track videos, not creators?**  
A: Just add `video_name` or `video_id` columns without `creator_name`. You'll see video performance without creator attribution.

**Q: Can I use this with existing data?**  
A: Yes! If you have historical ad data, just add the creator/video columns retroactively and re-upload.

**Q: Does this work with uploaded CSVs in Streamlit?**  
A: Absolutely! Upload your enhanced CSV through the file uploader and the Creators tab will appear automatically.

---

## 📈 Metrics Explained

### Creator-Level Metrics
- **Total Videos**: Number of unique videos/ads created by this person
- **ROAS**: Return on Ad Spend - how many dollars of revenue per dollar spent
- **Revenue/Spend**: Total money generated vs money invested
- **CTR**: Click-Through Rate - % of impressions that led to clicks
- **Platforms**: Which ad platforms this creator's content ran on
- **Best Video**: The video with the highest ROAS

### Video-Level Metrics
- **Days Active**: How many unique days this video ran ads
- **Platform**: Where the video was promoted
- **ROAS**: Performance specifically for this video
- **Conversions**: Number of purchases/actions driven by this video

---

## 🎉 Example Use Case

### Scenario: Marketing Agency with 5 Video Creators

**Setup:**
1. Export ad performance from TikTok and Meta
2. Add `creator_name` column: "Alice", "Bob", "Charlie", "Diana", "Eve"
3. Add `video_name` for each ad creative
4. Upload to dashboard

**Insights You'll Get:**
- 📊 "Alice generates 5.2x ROAS - highest on the team!"
- 🎬 "Bob's 'Customer Testimonial V3' is the #1 performing video"
- 📉 "Charlie's videos need improvement - only 1.8x ROAS"
- 🏆 "Diana is most versatile - performs well on all 3 platforms"
- 💡 "Eve creates fewer videos but has the highest CTR"

**Action:**
- Assign more budget to Alice's videos
- Have Alice train Charlie on techniques
- Test Diana's creative style on more platforms
- Ask Bob to create more testimonial-style videos

---

## 🚀 Getting Started

1. **Add creator_name to your next CSV export**
2. **Upload to the dashboard**
3. **Click the new "👤 Creators" tab**
4. **Start tracking performance!**

That's it! The feature is designed to be simple and automatic.

---

Need help? Check the main [README.md](./README.md) or [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) for setup instructions.

