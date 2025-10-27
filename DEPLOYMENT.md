# Deployment Guide

## 🚀 Deployment Options

### 1. **Streamlit Cloud** (Recommended - Free & Easy)

**Steps:**
1. Push your code to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository: `hamzaelhanbali/ad_reporter`
6. Main file path: `streamlit_app.py`
7. Click "Deploy"

**Configuration:**
- Your app will be live at: `https://[app-name].streamlit.app`
- Upload CSV files via the web interface
- Automatic updates when you push to GitHub

---

### 2. **Heroku Deployment**

**Create `Procfile`:**
```
web: sh setup.sh && streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

**Create `setup.sh`:**
```bash
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

**Deploy:**
```bash
heroku login
heroku create your-app-name
git push heroku main
```

---

### 3. **Docker Deployment**

**Build and run:**
```bash
docker build -t ads-reporter .
docker run -p 8501:8501 ads-reporter
```

**Docker Compose:**
```bash
docker-compose up
```

---

### 4. **AWS/GCP/Azure**

**Using EC2/Compute Engine/VM:**
```bash
# SSH into your instance
git clone https://github.com/hamzaelhanbali/ad_reporter.git
cd ad_reporter
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py --server.port=80 --server.address=0.0.0.0
```

**Using App Service/App Engine:**
- Deploy with `gcloud app deploy` or equivalent
- Set `streamlit_app.py` as entry point

---

## 🔐 Environment Variables

Create a `.env` file for sensitive data:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Optional: API Keys
TIKTOK_API_KEY=your_key
META_API_KEY=your_key
GOOGLE_API_KEY=your_key
```

**For Streamlit Cloud:**
- Go to App Settings → Secrets
- Add secrets in TOML format

---

## 📊 Data Upload

**Option 1: Manual Upload via UI**
- Use the file uploader in the dashboard
- CSV files are processed in-memory

**Option 2: Mount Storage**
- Connect to S3/GCS/Azure Blob
- Automatically sync CSV files

**Option 3: API Integration**
- Connect directly to TikTok/Meta/Google Ads APIs
- Real-time data fetching

---

## 🔧 Configuration for Production

**Update `config/config.yaml`:**
```yaml
system:
  log_level: "WARNING"  # Less verbose in production
  
dashboard:
  host: "0.0.0.0"  # Accept all connections
  debug: false  # Disable debug mode
```

---

## 📈 Monitoring

**Recommended Tools:**
- **Sentry** for error tracking
- **Google Analytics** for usage stats
- **Uptime Robot** for availability monitoring

---

## 🔒 Security Checklist

- ✅ Use environment variables for secrets
- ✅ Enable HTTPS (automatic on Streamlit Cloud)
- ✅ Set up authentication if needed
- ✅ Validate all CSV inputs
- ✅ Rate limit API endpoints
- ✅ Regular dependency updates

---

## 📱 Custom Domain

**Streamlit Cloud:**
- Settings → Domain → Add custom domain
- Update DNS CNAME record

**Other Platforms:**
- Configure reverse proxy (nginx)
- Set up SSL certificate (Let's Encrypt)

---

## 🐛 Troubleshooting

**Issue: App won't start**
```bash
# Check logs
streamlit run streamlit_app.py --server.headless=false
```

**Issue: Missing dependencies**
```bash
pip install -r requirements.txt --upgrade
```

**Issue: Memory errors**
- Increase container memory
- Enable caching with `@st.cache_data`

---

## 📚 Additional Resources

- [Streamlit Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)
- [Heroku Python Guide](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

