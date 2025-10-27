# 🚀 Deploy to Streamlit Cloud - Quick Guide

## Step 1: Push to GitHub

```bash
# Create a new repository on GitHub
# Go to: https://github.com/new
# Repository name: ads-auto-reporter (or your choice)
# Keep it public or private
# DO NOT initialize with README (we already have one)

# Then run these commands:
cd /Users/hamzaelhanbali/Desktop/ad_reporter

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/ads-auto-reporter.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 2: Deploy on Streamlit Cloud

### 2.1 Sign Up
1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with your GitHub account
3. Authorize Streamlit to access your repositories

### 2.2 Deploy App
1. Click **"New app"** button
2. Fill in the details:
   - **Repository:** `YOUR_USERNAME/ads-auto-reporter`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
   - **App URL:** Choose a custom subdomain (e.g., `my-ads-dashboard`)

3. Click **"Deploy!"**

### 2.3 Wait for Deployment
- Initial deployment takes 2-3 minutes
- You'll see a build log
- Once complete, your app will be live!

## Step 3: Access Your App

Your dashboard will be available at:
```
https://YOUR-APP-NAME.streamlit.app
```

## 📊 Using the Deployed App

### Upload CSV Files
1. The app will load sample data automatically
2. To use your own data:
   - Export CSV from TikTok/Meta/Google Ads
   - Upload via the Streamlit interface (we can add file uploader)

### Share with Team
- Just share the URL!
- Anyone with the link can view (if public)
- For private apps, manage access in Streamlit settings

## 🔒 Optional: Add Secrets

If you want to add email functionality or API keys:

1. Go to your app on Streamlit Cloud
2. Click **⋮ (menu)** → **Settings**
3. Go to **Secrets** tab
4. Add in TOML format:

```toml
[email]
smtp_server = "smtp.gmail.com"
smtp_port = 587
username = "your_email@gmail.com"
password = "your_app_password"

[api]
tiktok_key = "your_key"
meta_key = "your_key"
google_key = "your_key"
```

## 🔄 Update Your App

Every time you push to GitHub, Streamlit Cloud auto-deploys:

```bash
# Make changes to your code
git add .
git commit -m "Updated dashboard features"
git push

# Streamlit Cloud will automatically redeploy!
```

## 📈 Monitor Your App

- **View logs:** Click on app → "Manage app" → "Logs"
- **Analytics:** Built-in usage statistics
- **Reboot:** If stuck, click "Reboot app"

## 🎨 Customize

### Change Theme
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
```

### Add Custom Domain
1. Go to Settings → Custom domain
2. Add CNAME record to your DNS:
   ```
   CNAME dashboard.yourdomain.com → YOUR-APP.streamlit.app
   ```

## 🐛 Troubleshooting

**App won't start?**
- Check the logs for errors
- Verify `requirements.txt` has all dependencies
- Make sure `streamlit_app.py` is at root level

**Slow loading?**
- Add `@st.cache_data` to expensive functions (already done!)
- Optimize CSV file sizes

**Need help?**
- Streamlit Community: [discuss.streamlit.io](https://discuss.streamlit.io)
- Check logs: Click "Manage app" → "Logs"

## ✨ Your App is Live!

Once deployed, you'll have:
- ✅ Beautiful, modern dashboard
- ✅ Auto-updates on git push
- ✅ Free hosting (with usage limits)
- ✅ HTTPS enabled
- ✅ Shareable URL

Enjoy your Ads Auto-Reporting System! 🎉

