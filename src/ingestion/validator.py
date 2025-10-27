"""Data quality validation for normalized ad data."""

from typing import List, Dict, Tuple
from datetime import date
import pandas as pd
from ..models.schemas import AdRecord
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ValidationError:
    """Represents a data validation error."""
    
    def __init__(
        self,
        severity: str,
        message: str,
        row_index: int = None,
        field: str = None
    ):
        self.severity = severity  # 'error', 'warning', 'info'
        self.message = message
        self.row_index = row_index
        self.field = field
    
    def __str__(self):
        location = f" (row {self.row_index}, field '{self.field}')" if self.row_index is not None else ""
        return f"[{self.severity.upper()}] {self.message}{location}"


class DataValidator:
    """
    Validates normalized ad data for quality and consistency.
    
    Checks:
    - Missing required fields
    - Negative values
    - Logical inconsistencies
    - Outliers
    - Date ranges
    """
    
    def __init__(
        self,
        min_date: date = None,
        max_date: date = None,
        max_cpc: float = 100.0,
        max_cpp: float = 500.0
    ):
        """
        Initialize validator with thresholds.
        
        Args:
            min_date: Minimum acceptable date
            max_date: Maximum acceptable date
            max_cpc: Maximum reasonable CPC
            max_cpp: Maximum reasonable cost per conversion
        """
        self.min_date = min_date
        self.max_date = max_date
        self.max_cpc = max_cpc
        self.max_cpp = max_cpp
    
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, List[ValidationError]]:
        """
        Validate a normalized DataFrame.
        
        Args:
            df: Normalized DataFrame
            
        Returns:
            Tuple of (is_valid, list of validation errors)
        """
        errors = []
        
        # Check for empty dataframe
        if df.empty:
            errors.append(ValidationError('error', 'DataFrame is empty'))
            return False, errors
        
        # Check required columns
        required_cols = ['date', 'platform', 'campaign', 'spend', 'impressions', 'clicks', 'conversions', 'revenue']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(ValidationError('error', f'Missing required columns: {missing_cols}'))
            return False, errors
        
        # Validate each row
        for idx, row in df.iterrows():
            row_errors = self._validate_row(row, idx)
            errors.extend(row_errors)
        
        # Check for duplicate records
        duplicates = df.duplicated(subset=['date', 'platform', 'campaign'], keep=False)
        if duplicates.any():
            dup_count = duplicates.sum()
            errors.append(ValidationError(
                'warning',
                f'Found {dup_count} duplicate records (same date, platform, campaign)'
            ))
        
        # Severity check
        error_count = sum(1 for e in errors if e.severity == 'error')
        is_valid = error_count == 0
        
        if errors:
            logger.warning(f"Validation found {len(errors)} issues ({error_count} errors)")
            for error in errors[:10]:  # Log first 10
                logger.debug(str(error))
        else:
            logger.info("Validation passed with no issues")
        
        return is_valid, errors
    
    def _validate_row(self, row: pd.Series, idx: int) -> List[ValidationError]:
        """
        Validate a single row.
        
        Args:
            row: DataFrame row
            idx: Row index
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Date validation
        if pd.isna(row['date']):
            errors.append(ValidationError('error', 'Missing date', idx, 'date'))
        elif self.min_date and row['date'] < self.min_date:
            errors.append(ValidationError('warning', f'Date before minimum: {row["date"]}', idx, 'date'))
        elif self.max_date and row['date'] > self.max_date:
            errors.append(ValidationError('warning', f'Date after maximum: {row["date"]}', idx, 'date'))
        
        # Campaign validation
        if pd.isna(row['campaign']) or str(row['campaign']).strip() == '':
            errors.append(ValidationError('error', 'Missing campaign name', idx, 'campaign'))
        
        # Numeric validations
        numeric_fields = ['spend', 'impressions', 'clicks', 'conversions', 'revenue']
        for field in numeric_fields:
            value = row[field]
            
            # Check for negative values
            if value < 0:
                errors.append(ValidationError('error', f'Negative value: {value}', idx, field))
            
            # Check for NaN
            if pd.isna(value):
                errors.append(ValidationError('error', f'Missing value', idx, field))
        
        # Logical consistency checks
        if row['clicks'] > row['impressions']:
            errors.append(ValidationError(
                'error',
                f'Clicks ({row["clicks"]}) exceeds impressions ({row["impressions"]})',
                idx,
                'clicks'
            ))
        
        if row['conversions'] > row['clicks']:
            errors.append(ValidationError(
                'warning',
                f'Conversions ({row["conversions"]}) exceeds clicks ({row["clicks"]})',
                idx,
                'conversions'
            ))
        
        # Check for unrealistic metrics
        if row['clicks'] > 0:
            cpc = row['spend'] / row['clicks']
            if cpc > self.max_cpc:
                errors.append(ValidationError(
                    'warning',
                    f'Unusually high CPC: ${cpc:.2f}',
                    idx,
                    'spend'
                ))
        
        if row['conversions'] > 0:
            cpp = row['spend'] / row['conversions']
            if cpp > self.max_cpp:
                errors.append(ValidationError(
                    'warning',
                    f'Unusually high cost per conversion: ${cpp:.2f}',
                    idx,
                    'spend'
                ))
        
        # Check for zero spend with activity
        if row['spend'] == 0 and (row['impressions'] > 0 or row['clicks'] > 0):
            errors.append(ValidationError(
                'warning',
                'Zero spend but has impressions/clicks',
                idx,
                'spend'
            ))
        
        return errors
    
    def validate_records(self, records: List[AdRecord]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate a list of AdRecord objects.
        
        Args:
            records: List of AdRecord objects
            
        Returns:
            Tuple of (is_valid, list of validation errors)
        """
        if not records:
            return False, [ValidationError('error', 'No records to validate')]
        
        # Convert to DataFrame for validation
        df = pd.DataFrame([{
            'date': r.date,
            'platform': r.platform.value,
            'campaign': r.campaign,
            'spend': r.spend,
            'impressions': r.impressions,
            'clicks': r.clicks,
            'conversions': r.conversions,
            'revenue': r.revenue
        } for r in records])
        
        return self.validate_dataframe(df)
    
    def get_summary(self, errors: List[ValidationError]) -> Dict[str, int]:
        """
        Get summary statistics of validation errors.
        
        Args:
            errors: List of validation errors
            
        Returns:
            Summary dictionary
        """
        return {
            'total': len(errors),
            'errors': sum(1 for e in errors if e.severity == 'error'),
            'warnings': sum(1 for e in errors if e.severity == 'warning'),
            'info': sum(1 for e in errors if e.severity == 'info')
        }




