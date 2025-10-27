"""CSV file loading and initial parsing."""

from pathlib import Path
from typing import Optional, List
import pandas as pd
from ..models.enums import AdPlatform
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CSVLoader:
    """
    Handles CSV file uploading and initial parsing.
    
    Supports multiple file encodings and detects platform automatically
    based on column names if not specified.
    """
    
    PLATFORM_SIGNATURES = {
        AdPlatform.TIKTOK: ['Campaign Name', 'Cost', 'Date'],
        AdPlatform.META: ['campaign_name', 'spend', 'reporting_starts'],
        AdPlatform.GOOGLE: ['Campaign', 'Day', 'Impr.', 'Cost']
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
        Load a CSV file and detect platform if not specified.
        
        Args:
            file_path: Path to CSV file
            platform: Ad platform (auto-detected if None)
            encoding: File encoding (tries multiple if fails)
            
        Returns:
            Tuple of (DataFrame, detected platform)
            
        Raises:
            ValueError: If file cannot be loaded or platform detected
        """
        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")
        
        logger.info(f"Loading CSV: {file_path}")
        
        # Try multiple encodings
        encodings = [encoding, 'utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        
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
        
        for platform, signature_cols in self.PLATFORM_SIGNATURES.items():
            # Check if at least 2 signature columns match
            matches = sum(1 for col in signature_cols if col in columns)
            if matches >= 2:
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
        Scan upload directory for CSV files.
        
        Returns:
            List of CSV file paths
        """
        csv_files = list(self.upload_path.glob("*.csv"))
        logger.info(f"Found {len(csv_files)} CSV files in {self.upload_path}")
        return csv_files




