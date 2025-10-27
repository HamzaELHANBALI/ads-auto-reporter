# Installation Guide

## Issue: pip is broken

Your system has Python 3.13.1 but pip appears to be corrupted. Here's how to fix it:

### Option 1: Reinstall pip (Recommended)

```bash
# Download get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

# Install pip
python3 get-pip.py

# Verify installation
pip3 --version
```

### Option 2: Use Python venv (Best Practice)

```bash
# Navigate to project
cd /Users/hamzaelhanbali/Desktop/ad_reporter

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the example
python run_example.py
```

### Option 3: Reinstall Python via Homebrew

```bash
# Uninstall current Python
brew uninstall python@3.13

# Reinstall Python (includes pip)
brew install python@3.13

# Verify
python3 --version
pip3 --version
```

### Option 4: Use conda (if you have it)

```bash
# Create conda environment
conda create -n ads_reporter python=3.11

# Activate environment
conda activate ads_reporter

# Install dependencies
pip install -r requirements.txt
```

## After Fixing pip

Once pip is working, run:

```bash
# Install all dependencies
cd /Users/hamzaelhanbali/Desktop/ad_reporter
pip install -r requirements.txt

# Run the example workflow
python run_example.py

# Or test the full system
python test_full_system.py

# Or launch the dashboard
python run_dashboard.py
```

## Quick Test (No Dependencies)

You can verify the code structure without dependencies:

```bash
python verify_structure.py
```

This checks that all files are present and have correct syntax (which already passed ✅).

## Expected Output

Once dependencies are installed, `run_example.py` will:

1. Load 3 CSV files (TikTok, Meta, Google)
2. Normalize ~140 records across 20 campaigns
3. Calculate KPIs for all campaigns
4. Show top 3 campaigns by revenue
5. Generate weekly digest with performance alerts
6. Export PDF reports
7. Display summary statistics

The full test (`test_full_system.py`) performs 10 comprehensive tests covering all functionality.

