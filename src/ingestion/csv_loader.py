"""CSV and Excel file loading and initial parsing."""

from pathlib import Path
from typing import Optional, List
import pandas as pd
from ..models.enums import AdPlatform
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CSVLoader:
    """
    Handles CSV and Excel file uploading and initial parsing.
    
    Supports multiple file encodings and detects platform automatically
    based on column names if not specified.
    
    Supported formats:
    - CSV (.csv)
    - Excel (.xlsx, .xls)
    """
    
    PLATFORM_SIGNATURES = {
        AdPlatform.TIKTOK: [
            ['Campaign Name', 'Cost', 'Date'],  # Campaign-level export
            ['Ad name', 'Ad group name', 'Cost', 'Impressions', 'Clicks (destination)']  # Ad-level export
        ],
        AdPlatform.META: [['campaign_name', 'spend', 'reporting_starts']],
        AdPlatform.GOOGLE: [['Campaign', 'Day', 'Impr.', 'Cost']]
    }
    
    def __init__(self, upload_path: Optional[Path] = None):
        """
        Initialize CSV loader.
        
        Args:
            upload_path: Directory for uploaded CSV files
        """
        self.upload_path = upload_path or Path("data/uploads")
        self.upload_path.mkdir(parents=True, exist_ok=True)
    
    def load_csv(
        self,
        file_path: Path,
        platform: Optional[AdPlatform] = None,
        encoding: str = 'utf-8'
    ) -> tuple[pd.DataFrame, AdPlatform]:
        """
        Load a CSV or Excel file and detect platform if not specified.
        
        Args:
            file_path: Path to CSV or Excel file
            platform: Ad platform (auto-detected if None)
            encoding: File encoding for CSV (tries multiple if fails)
            
        Returns:
            Tuple of (DataFrame, detected platform)
            
        Raises:
            ValueError: If file cannot be loaded or platform detected
        """
        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")
        
        logger.info(f"Loading file: {file_path}")
        
        # Determine file type and load accordingly
        file_extension = file_path.suffix.lower()
        df = None
        
        if file_extension in ['.xlsx', '.xls']:
            # Load Excel file
            try:
                df = pd.read_excel(file_path)
                logger.info(f"Successfully loaded Excel file with {len(df)} rows")
            except Exception as e:
                raise ValueError(f"Failed to load Excel file: {e}")
        else:
            # Load CSV file with multiple encoding attempts
            encodings = [encoding, 'utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            
            for enc in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=enc)
                    logger.debug(f"Successfully loaded with encoding: {enc}")
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    logger.error(f"Error loading CSV with {enc}: {e}")
                    continue
            
            if df is None:
                raise ValueError(f"Failed to load CSV with any encoding: {file_path}")
        
        # Detect platform if not specified
        if platform is None:
            platform = self._detect_platform(df)
            if platform is None:
                raise ValueError(
                    f"Could not detect platform from CSV columns: {list(df.columns)}"
                )
            logger.info(f"Detected platform: {platform.value}")
        
        # Basic validation
        if df.empty:
            raise ValueError("CSV file is empty")
        
        logger.info(f"Loaded {len(df)} rows from {file_path.name}")
        return df, platform
    
    def _detect_platform(self, df: pd.DataFrame) -> Optional[AdPlatform]:
        """
        Detect ad platform based on column names.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Detected platform or None
        """
        columns = set(df.columns)
        
        for platform, signatures in self.PLATFORM_SIGNATURES.items():
            # signatures can be a list of lists (multiple possible formats per platform)
            if not isinstance(signatures[0], list):
                # Old format compatibility
                signatures = [signatures]
            
            for signature_cols in signatures:
                # Check if at least 2 signature columns match
                matches = sum(1 for col in signature_cols if col in columns)
                if matches >= 2:
                    logger.info(f"Detected platform: {platform.value}")
                    return platform
        
        return None
    
    def load_multiple(
        self,
        file_paths: List[Path],
        platform: Optional[AdPlatform] = None
    ) -> List[tuple[pd.DataFrame, AdPlatform, Path]]:
        """
        Load multiple CSV files.
        
        Args:
            file_paths: List of file paths
            platform: Platform (if same for all files)
            
        Returns:
            List of (DataFrame, platform, file_path) tuples
        """
        results = []
        
        for file_path in file_paths:
            try:
                df, detected_platform = self.load_csv(file_path, platform)
                results.append((df, detected_platform, file_path))
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                continue
        
        logger.info(f"Successfully loaded {len(results)} of {len(file_paths)} files")
        return results
    
    def scan_upload_directory(self) -> List[Path]:
        """
        Scan upload directory for CSV and Excel files.
        
        Returns:
            List of file paths (CSV and Excel)
        """
        csv_files = list(self.upload_path.glob("*.csv"))
        xlsx_files = list(self.upload_path.glob("*.xlsx"))
        xls_files = list(self.upload_path.glob("*.xls"))
        
        all_files = csv_files + xlsx_files + xls_files
        logger.info(f"Found {len(all_files)} files ({len(csv_files)} CSV, {len(xlsx_files)} XLSX, {len(xls_files)} XLS) in {self.upload_path}")
        return all_files




