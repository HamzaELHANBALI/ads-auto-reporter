"""
Data preprocessing for ad exports with missing columns.

Handles:
- Extracting dates from filenames
- Missing revenue columns
- Ad-level vs campaign-level exports
- TikTok specific formats
"""

import re
from pathlib import Path
from typing import Optional, Tuple
from datetime import date, datetime, timedelta
import pandas as pd
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DataPreprocessor:
    """Preprocesses ad data to ensure required columns exist."""
    
    # Date patterns in filenames
    DATE_PATTERNS = [
        # (2025-09-27 to 2025-10-27)
        r'\((\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})\)',
        # 2025-09-27_to_2025-10-27
        r'(\d{4}-\d{2}-\d{2})_to_(\d{4}-\d{2}-\d{2})',
        # Sep-27-2025_Oct-27-2025
        r'([A-Za-z]{3}-\d{2}-\d{4})_([A-Za-z]{3}-\d{2}-\d{4})',
    ]
    
    def __init__(self, default_aov: float = 30.0):
        """
        Initialize preprocessor.
        
        Args:
            default_aov: Default Average Order Value for revenue calculation
        """
        self.default_aov = default_aov
    
    def preprocess(
        self,
        df: pd.DataFrame,
        file_path: Path,
        platform: str
    ) -> pd.DataFrame:
        """
        Preprocess dataframe to add missing columns.
        
        Args:
            df: Raw dataframe
            file_path: Source file path (for date extraction)
            platform: Ad platform
            
        Returns:
            Preprocessed dataframe with all required columns
        """
        logger.info(f"Preprocessing {len(df)} rows from {file_path.name}")
        
        df = df.copy()
        
        # Add date column if missing
        if 'Date' not in df.columns and 'date' not in df.columns:
            df = self._add_date_column(df, file_path)
        
        # Add revenue column if missing
        if 'Revenue' not in df.columns and 'revenue' not in df.columns:
            df = self._add_revenue_column(df, platform)
        
        # Handle TikTok ad-level exports
        if platform == 'tiktok':
            df = self._handle_tiktok_adlevel(df)
        
        logger.info(f"Preprocessing complete. Columns: {list(df.columns)}")
        return df
    
    def _add_date_column(self, df: pd.DataFrame, file_path: Path) -> pd.DataFrame:
        """
        Add date column by extracting from filename or using midpoint.
        
        Args:
            df: Dataframe
            file_path: Source file path
            
        Returns:
            Dataframe with Date column
        """
        filename = file_path.name
        logger.info(f"Extracting date from filename: {filename}")
        
        # Try to extract date range from filename
        start_date, end_date = self._extract_date_range(filename)
        
        if start_date and end_date:
            # Use midpoint of range
            midpoint = start_date + (end_date - start_date) / 2
            df['Date'] = midpoint.strftime('%Y-%m-%d')
            logger.info(f"Using date range midpoint: {df['Date'].iloc[0]}")
        else:
            # Use today's date as fallback
            df['Date'] = date.today().strftime('%Y-%m-%d')
            logger.warning(f"Could not extract date from filename, using today: {df['Date'].iloc[0]}")
        
        return df
    
    def _extract_date_range(self, filename: str) -> Tuple[Optional[date], Optional[date]]:
        """
        Extract date range from filename.
        
        Args:
            filename: Filename to parse
            
        Returns:
            Tuple of (start_date, end_date) or (None, None)
        """
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, filename)
            if match:
                try:
                    start_str, end_str = match.groups()
                    
                    # Try different date formats
                    for date_format in ['%Y-%m-%d', '%b-%d-%Y', '%m-%d-%Y']:
                        try:
                            start_date = datetime.strptime(start_str, date_format).date()
                            end_date = datetime.strptime(end_str, date_format).date()
                            logger.info(f"Extracted date range: {start_date} to {end_date}")
                            return start_date, end_date
                        except ValueError:
                            continue
                except Exception as e:
                    logger.warning(f"Failed to parse dates: {e}")
                    continue
        
        return None, None
    
    def _add_revenue_column(self, df: pd.DataFrame, platform: str) -> pd.DataFrame:
        """
        Add revenue column if missing.
        
        Strategies:
        1. Use Cost per conversion * Conversions
        2. Use estimated AOV * Conversions
        3. Set to 0 if no conversion data
        
        Args:
            df: Dataframe
            platform: Ad platform
            
        Returns:
            Dataframe with Revenue column
        """
        logger.info("Adding missing Revenue column")
        
        # Check if we have conversion data
        conversion_col = self._find_column(df, ['Conversions', 'conversions', 'Conv.'])
        
        if conversion_col and conversion_col in df.columns:
            # Strategy 1: Use Cost per conversion if available
            cpp_col = self._find_column(df, ['Cost per conversion', 'cost_per_conversion'])
            
            if cpp_col and cpp_col in df.columns:
                # Revenue = Conversions * (Cost per conversion * ROAS estimate)
                # Assume ROAS of 3.0 as baseline
                df['Revenue'] = df[conversion_col] * df[cpp_col] * 3.0
                logger.info(f"Calculated revenue using: Conversions × CPP × 3.0")
            else:
                # Strategy 2: Use estimated AOV
                df['Revenue'] = df[conversion_col] * self.default_aov
                logger.info(f"Calculated revenue using: Conversions × ${self.default_aov} AOV")
        else:
            # Strategy 3: No conversion data, set to 0
            df['Revenue'] = 0.0
            logger.warning("No conversion data found, setting Revenue to 0")
        
        return df
    
    def _handle_tiktok_adlevel(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle TikTok ad-level exports with special column mapping.
        
        Args:
            df: Dataframe
            
        Returns:
            Dataframe with standardized columns
        """
        # Map "Ad group name" to "Campaign Name" if missing
        if 'Campaign Name' not in df.columns and 'Ad group name' in df.columns:
            df['Campaign Name'] = df['Ad group name']
            logger.info("Mapped 'Ad group name' → 'Campaign Name'")
        
        # Map "Ad name" to video tracking columns
        if 'Ad name' in df.columns:
            # Ad name often contains video filename
            df['Video Name'] = df['Ad name']
            logger.info("Mapped 'Ad name' → 'Video Name'")
        
        # Handle "Clicks (destination)" → "Clicks"
        if 'Clicks' not in df.columns and 'Clicks (destination)' in df.columns:
            df['Clicks'] = df['Clicks (destination)']
            logger.info("Mapped 'Clicks (destination)' → 'Clicks'")
        
        # Handle status columns (for filtering later)
        if 'Primary status' in df.columns:
            active_ads = df[df['Primary status'].str.lower().isin(['active', 'enabled'])].copy()
            if len(active_ads) < len(df):
                logger.info(f"Note: {len(df) - len(active_ads)} inactive ads in dataset")
        
        return df
    
    def _find_column(self, df: pd.DataFrame, candidates: list) -> Optional[str]:
        """
        Find first matching column from candidates.
        
        Args:
            df: Dataframe
            candidates: List of possible column names
            
        Returns:
            First matching column name or None
        """
        for col in candidates:
            if col in df.columns:
                return col
        return None

