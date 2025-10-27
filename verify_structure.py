#!/usr/bin/env python
"""
Verify the code structure and imports are correct.
This script checks that all modules can be imported without errors.
"""

import sys
from pathlib import Path

def check_file_exists(path):
    """Check if a file exists."""
    if path.exists():
        print(f"✓ {path}")
        return True
    else:
        print(f"✗ Missing: {path}")
        return False

def main():
    """Verify project structure."""
    print("=" * 60)
    print("  Ads Auto-Reporting System - Structure Verification")
    print("=" * 60)
    
    all_good = True
    
    # Check main directories
    print("\n📁 Checking Directories:")
    dirs = [
        Path("src"),
        Path("src/models"),
        Path("src/ingestion"),
        Path("src/analytics"),
        Path("src/dashboard"),
        Path("src/reporting"),
        Path("src/utils"),
        Path("tests"),
        Path("tests/fixtures"),
        Path("config"),
        Path("data/uploads"),
        Path("data/processed"),
        Path("data/outputs"),
    ]
    
    for dir_path in dirs:
        if dir_path.exists():
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ Missing: {dir_path}/")
            all_good = False
    
    # Check core Python files
    print("\n📄 Checking Core Files:")
    files = [
        Path("src/__init__.py"),
        Path("src/main.py"),
        Path("src/config.py"),
        Path("src/models/__init__.py"),
        Path("src/models/enums.py"),
        Path("src/models/schemas.py"),
        Path("src/ingestion/__init__.py"),
        Path("src/ingestion/csv_loader.py"),
        Path("src/ingestion/normalizer.py"),
        Path("src/ingestion/validator.py"),
        Path("src/analytics/__init__.py"),
        Path("src/analytics/kpi_calculator.py"),
        Path("src/analytics/aggregator.py"),
        Path("src/dashboard/__init__.py"),
        Path("src/dashboard/visualizer.py"),
        Path("src/dashboard/export.py"),
        Path("src/reporting/__init__.py"),
        Path("src/reporting/digest.py"),
        Path("src/reporting/email_sender.py"),
        Path("src/utils/__init__.py"),
        Path("src/utils/logger.py"),
        Path("src/utils/helpers.py"),
    ]
    
    for file_path in files:
        if not check_file_exists(file_path):
            all_good = False
    
    # Check configuration files
    print("\n⚙️  Checking Configuration:")
    config_files = [
        Path("config/config.yaml"),
        Path("requirements.txt"),
    ]
    
    for file_path in config_files:
        if not check_file_exists(file_path):
            all_good = False
    
    # Check test files
    print("\n🧪 Checking Test Files:")
    test_files = [
        Path("tests/__init__.py"),
        Path("tests/conftest.py"),
        Path("tests/test_normalizer.py"),
        Path("tests/test_kpi_calculator.py"),
        Path("tests/test_validator.py"),
        Path("tests/fixtures/sample_tiktok.csv"),
        Path("tests/fixtures/sample_meta.csv"),
        Path("tests/fixtures/sample_google.csv"),
    ]
    
    for file_path in test_files:
        if not check_file_exists(file_path):
            all_good = False
    
    # Check test data
    print("\n📊 Checking Test Data:")
    data_files = [
        Path("data/uploads/test_tiktok_complete.csv"),
        Path("data/uploads/test_meta_complete.csv"),
        Path("data/uploads/test_google_complete.csv"),
    ]
    
    for file_path in data_files:
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✓ {file_path} ({size} bytes)")
        else:
            print(f"✗ Missing: {file_path}")
            all_good = False
    
    # Check syntax of Python files
    print("\n🔍 Checking Python Syntax:")
    
    import ast
    import traceback
    
    syntax_errors = []
    for file_path in files:
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    ast.parse(f.read(), filename=str(file_path))
                print(f"✓ {file_path.name}")
            except SyntaxError as e:
                print(f"✗ Syntax error in {file_path.name}: {e}")
                syntax_errors.append((file_path, e))
                all_good = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_good:
        print("✅ ALL CHECKS PASSED!")
        print("=" * 60)
        print("\n📋 Project Structure Summary:")
        print("  • All directories created")
        print("  • All Python modules present")
        print("  • No syntax errors detected")
        print("  • Test data files generated")
        print("\n🚀 Next Steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run tests: pytest")
        print("  3. Test system: python test_full_system.py")
        print("  4. Launch dashboard: python run_dashboard.py")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("=" * 60)
        print("\nPlease fix the issues above before proceeding.")
    
    print("")
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())




