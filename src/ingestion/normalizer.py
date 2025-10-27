"""Data normalization for multi-platform ad data."""

from typing import Dict, List, Optional
import pandas as pd
from ..models.enums import AdPlatform, NORMALIZED_COLUMNS, OPTIONAL_COLUMNS
from ..models.schemas import AdRecord
from ..utils.helpers import parse_date_flexible, clean_numeric_value
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DataNormalizer:
    """
    Normalizes ad data from different platforms to a unified schema.
    
    Handles:
    - Column mapping
    - Date parsing
    - Numeric cleaning (currency symbols, commas)
    - Missing value handling
    """
    
    def __init__(self, column_mappings: Dict[str, Dict[str, str]]):
        """
        Initialize normalizer with platform-specific column mappings.
        
        Args:
            column_mappings: Dict of platform -> {standard_name: platform_column}
        """
        self.column_mappings = column_mappings
    
    def normalize(
        self,
        df: pd.DataFrame,
        platform: AdPlatform
    ) -> pd.DataFrame:
        """
        Normalize a platform-specific DataFrame to standard schema.
        
        Args:
            df: Raw DataFrame from platform
            platform: Ad platform
            
        Returns:
            Normalized DataFrame with standard columns
            
        Raises:
            ValueError: If required columns are missing
        """
        logger.info(f"Normalizing {len(df)} rows for platform: {platform.value}")
        
        # Get column mapping for this platform
        mapping = self.column_mappings.get(platform.value)
        if not mapping:
            raise ValueError(f"No column mapping found for platform: {platform.value}")
        
        # Store optional columns that exist in source data (case-insensitive, handle spaces)
        df_normalized_cols = {col.lower().replace(' ', '_'): col for col in df.columns}
        available_optional = {}
        for opt_col in OPTIONAL_COLUMNS:
            opt_col_normalized = opt_col.lower().replace(' ', '_')
            if opt_col_normalized in df_normalized_cols:
                available_optional[opt_col] = df_normalized_cols[opt_col_normalized]
        
        # Create normalized dataframe
        normalized_data = []
        
        for idx, row in df.iterrows():
            try:
                record = self._normalize_row(row, platform, mapping)
                if record:
                    # Add optional columns if they exist
                    for std_name, orig_name in available_optional.items():
                        if orig_name in row.index and pd.notna(row[orig_name]):
                            record[std_name] = str(row[orig_name]).strip()
                    
                    normalized_data.append(record)
            except Exception as e:
                logger.warning(f"Failed to normalize row {idx}: {e}")
                continue
        
        if not normalized_data:
            raise ValueError("No valid records after normalization")
        
        # Create DataFrame
        normalized_df = pd.DataFrame(normalized_data)
        
        # Ensure all required columns exist
        for col in NORMALIZED_COLUMNS:
            if col not in normalized_df.columns:
                normalized_df[col] = None if col in ['date', 'campaign'] else 0
        
        # Order columns: required first, then optional
        final_columns = NORMALIZED_COLUMNS.copy()
        for opt_col in OPTIONAL_COLUMNS:
            if opt_col in normalized_df.columns:
                final_columns.append(opt_col)
        
        normalized_df = normalized_df[final_columns]
        
        logger.info(f"Successfully normalized {len(normalized_df)} rows with optional columns: {list(available_optional.keys())}")
        return normalized_df
    
    def _normalize_row(
        self,
        row: pd.Series,
        platform: AdPlatform,
        mapping: Dict[str, str]
    ) -> Optional[Dict]:
        """
        Normalize a single row.
        
        Args:
            row: DataFrame row
            platform: Ad platform
            mapping: Column mapping
            
        Returns:
            Normalized record dict or None if invalid
        """
        # Extract and normalize date
        date_col = mapping.get('date')
        if not date_col or date_col not in row:
            return None
        
        date_value = parse_date_flexible(row[date_col])
        if not date_value:
            return None
        
        # Extract campaign name
        campaign_col = mapping.get('campaign')
        campaign_value = str(row.get(campaign_col, 'Unknown')).strip()
        if not campaign_value or campaign_value.lower() in ['nan', 'none', '']:
            campaign_value = 'Unknown'
        
        # Extract and clean numeric values
        spend = clean_numeric_value(row.get(mapping.get('spend', ''), 0))
        impressions = int(clean_numeric_value(row.get(mapping.get('impressions', ''), 0)))
        clicks = int(clean_numeric_value(row.get(mapping.get('clicks', ''), 0)))
        conversions = int(clean_numeric_value(row.get(mapping.get('conversions', ''), 0)))
        revenue = clean_numeric_value(row.get(mapping.get('revenue', ''), 0))
        
        return {
            'date': date_value,
            'platform': platform.value,
            'campaign': campaign_value,
            'spend': spend,
            'impressions': impressions,
            'clicks': clicks,
            'conversions': conversions,
            'revenue': revenue
        }
    
    def normalize_multiple(
        self,
        dataframes: List[tuple[pd.DataFrame, AdPlatform]]
    ) -> pd.DataFrame:
        """
        Normalize multiple DataFrames and combine them.
        
        Args:
            dataframes: List of (DataFrame, platform) tuples
            
        Returns:
            Combined normalized DataFrame
        """
        normalized_dfs = []
        
        for df, platform in dataframes:
            try:
                normalized_df = self.normalize(df, platform)
                normalized_dfs.append(normalized_df)
            except Exception as e:
                logger.error(f"Failed to normalize {platform.value} data: {e}")
                continue
        
        if not normalized_dfs:
            raise ValueError("No data successfully normalized")
        
        # Combine all normalized dataframes
        combined_df = pd.concat(normalized_dfs, ignore_index=True)
        
        # Sort by date
        combined_df = combined_df.sort_values('date')
        
        logger.info(f"Combined {len(normalized_dfs)} datasets into {len(combined_df)} rows")
        return combined_df
    
    def to_records(self, df: pd.DataFrame) -> List[AdRecord]:
        """
        Convert normalized DataFrame to validated AdRecord objects.
        
        Args:
            df: Normalized DataFrame
            
        Returns:
            List of validated AdRecord objects
        """
        records = []
        
        for idx, row in df.iterrows():
            try:
                record = AdRecord(
                    date=row['date'],
                    platform=AdPlatform(row['platform']),
                    campaign=row['campaign'],
                    spend=float(row['spend']),
                    impressions=int(row['impressions']),
                    clicks=int(row['clicks']),
                    conversions=int(row['conversions']),
                    revenue=float(row['revenue'])
                )
                records.append(record)
            except Exception as e:
                logger.warning(f"Failed to create AdRecord from row {idx}: {e}")
                continue
        
        logger.info(f"Created {len(records)} validated AdRecord objects")
        return records




