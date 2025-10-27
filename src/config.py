"""Configuration management for the ads reporting system."""

from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml
from pydantic import BaseModel, validator
from .utils.logger import get_logger

logger = get_logger(__name__)


class Config(BaseModel):
    """System configuration."""
    
    # Paths
    config_file: Path
    upload_path: Path
    processed_path: Path
    output_path: Path
    
    # System settings
    project_name: str = "Ads Auto-Reporting System"
    version: str = "1.0.0"
    log_level: str = "INFO"
    
    # Data settings
    supported_platforms: list[str] = ["tiktok", "meta", "google"]
    column_mappings: Dict[str, Dict[str, str]] = {}
    
    # KPI thresholds
    target_roas: float = 3.0
    target_ctr: float = 0.02
    target_cvr: float = 0.05
    max_cpp: float = 50.0
    
    # Dashboard
    dashboard_host: str = "127.0.0.1"
    dashboard_port: int = 8050
    dashboard_debug: bool = False
    
    # Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    use_tls: bool = True
    sender_name: str = "Ads Reporting System"
    
    # Reporting
    lookback_days: int = 30
    comparison_period_days: int = 7
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
    
    @validator('upload_path', 'processed_path', 'output_path', pre=True)
    def ensure_path(cls, v):
        """Ensure paths are Path objects."""
        return Path(v) if not isinstance(v, Path) else v
    
    @classmethod
    def from_yaml(cls, config_path: Union[str, Path]) -> "Config":
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to config.yaml
            
        Returns:
            Config instance
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return cls._default_config(config_path)
        
        try:
            with open(config_path, 'r') as f:
                yaml_data = yaml.safe_load(f)
            
            # Flatten nested YAML structure
            config_dict = {
                'config_file': config_path,
                'upload_path': yaml_data.get('data', {}).get('upload_path', 'data/uploads'),
                'processed_path': yaml_data.get('data', {}).get('processed_path', 'data/processed'),
                'output_path': yaml_data.get('data', {}).get('output_path', 'data/outputs'),
                'project_name': yaml_data.get('system', {}).get('project_name', 'Ads Auto-Reporting System'),
                'version': yaml_data.get('system', {}).get('version', '1.0.0'),
                'log_level': yaml_data.get('system', {}).get('log_level', 'INFO'),
                'supported_platforms': yaml_data.get('data', {}).get('supported_platforms', ['tiktok', 'meta', 'google']),
                'column_mappings': yaml_data.get('data', {}).get('column_mappings', {}),
                'target_roas': yaml_data.get('kpis', {}).get('target_roas', 3.0),
                'target_ctr': yaml_data.get('kpis', {}).get('target_ctr', 0.02),
                'target_cvr': yaml_data.get('kpis', {}).get('target_cvr', 0.05),
                'max_cpp': yaml_data.get('kpis', {}).get('max_cpp', 50.0),
                'dashboard_host': yaml_data.get('dashboard', {}).get('host', '127.0.0.1'),
                'dashboard_port': yaml_data.get('dashboard', {}).get('port', 8050),
                'dashboard_debug': yaml_data.get('dashboard', {}).get('debug', False),
                'smtp_server': yaml_data.get('email', {}).get('smtp_server', 'smtp.gmail.com'),
                'smtp_port': yaml_data.get('email', {}).get('smtp_port', 587),
                'use_tls': yaml_data.get('email', {}).get('use_tls', True),
                'sender_name': yaml_data.get('email', {}).get('sender_name', 'Ads Reporting System'),
                'lookback_days': yaml_data.get('reporting', {}).get('lookback_days', 30),
                'comparison_period_days': yaml_data.get('reporting', {}).get('comparison_period_days', 7),
            }
            
            logger.info(f"Loaded configuration from {config_path}")
            return cls(**config_dict)
            
        except Exception as e:
            logger.error(f"Error loading config: {e}, using defaults")
            return cls._default_config(config_path)
    
    @classmethod
    def _default_config(cls, config_path: Path) -> "Config":
        """Create default configuration."""
        return cls(
            config_file=config_path,
            upload_path=Path("data/uploads"),
            processed_path=Path("data/processed"),
            output_path=Path("data/outputs"),
        )
    
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        for path in [self.upload_path, self.processed_path, self.output_path]:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {path}")


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        # Try to load from default location
        default_path = Path("config/config.yaml")
        _config = Config.from_yaml(default_path)
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config




