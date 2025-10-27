"""Helper utilities for the ads reporting system."""

from datetime import datetime, date
from pathlib import Path
from typing import Union, Optional
import re


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object of the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def parse_date_flexible(date_str: str) -> Optional[date]:
    """
    Parse a date string with multiple format support.
    
    Supports formats:
    - YYYY-MM-DD
    - MM/DD/YYYY
    - DD/MM/YYYY
    - YYYY/MM/DD
    - ISO 8601
    
    Args:
        date_str: Date string to parse
        
    Returns:
        date object or None if parsing fails
    """
    if not date_str or date_str == '' or str(date_str).lower() == 'nan':
        return None
        
    date_str = str(date_str).strip()
    
    # Common date formats
    formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%m-%d-%Y',
        '%d-%m-%Y',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None


def clean_numeric_value(value: Union[str, int, float]) -> float:
    """
    Clean and convert a value to float, handling currency symbols and formatting.
    
    Args:
        value: Value to clean (may include $, commas, etc.)
        
    Returns:
        Cleaned float value, 0.0 if conversion fails
    """
    if value is None or str(value).lower() in ['nan', 'none', '', 'null']:
        return 0.0
    
    if isinstance(value, (int, float)):
        return float(value)
    
    # Remove currency symbols, commas, spaces
    value_str = str(value).strip()
    value_str = re.sub(r'[$€£¥,\s]', '', value_str)
    
    # Handle parentheses for negative numbers
    if value_str.startswith('(') and value_str.endswith(')'):
        value_str = '-' + value_str[1:-1]
    
    try:
        return float(value_str)
    except ValueError:
        return 0.0


def generate_report_filename(
    report_type: str,
    start_date: date,
    end_date: Optional[date] = None,
    extension: str = "pdf"
) -> str:
    """
    Generate a standardized report filename.
    
    Args:
        report_type: Type of report (e.g., 'weekly_digest', 'performance')
        start_date: Report start date
        end_date: Report end date (optional)
        extension: File extension
        
    Returns:
        Formatted filename
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if end_date:
        date_range = f"{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}"
    else:
        date_range = start_date.strftime('%Y%m%d')
    
    return f"{report_type}_{date_range}_{timestamp}.{extension}"


def calculate_percentage_change(current: float, previous: float) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        current: Current value
        previous: Previous value
        
    Returns:
        Percentage change (e.g., 0.15 for 15% increase)
    """
    if previous == 0:
        return 0.0 if current == 0 else float('inf')
    
    return (current - previous) / previous


def format_currency(value: float, currency: str = "$") -> str:
    """
    Format a value as currency.
    
    Args:
        value: Numeric value
        currency: Currency symbol
        
    Returns:
        Formatted currency string
    """
    return f"{currency}{value:,.2f}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    Format a decimal value as percentage.
    
    Args:
        value: Decimal value (e.g., 0.15 for 15%)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimal_places}f}%"




