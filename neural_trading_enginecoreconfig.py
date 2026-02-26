"""
Configuration management for NeuralTrading Engine
Uses Pydantic for validation with environment variable support
"""
import os
from typing import Optional, Dict, Any, List
from pydantic import BaseSettings, Field, validator
from loguru import logger
from pathlib import Path

class TradingConfig(BaseSettings):
    """Main configuration class for trading engine"""
    
    # Environment
    environment: str = Field(default="development", env="TRADING_ENV")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Firebase Configuration (CRITICAL - Priority as per constraints)
    firebase_project_id: Optional[str] = Field(env="FIREBASE_PROJECT_ID")
    firebase_credentials_path: Optional[str] = Field(env="FIREBASE_CREDENTIALS_PATH")
    
    # Exchange Configuration
    exchange_id: str = Field(default="binance", env="EXCHANGE_ID")
    api_key: Optional[str] = Field(env="API_KEY")
    api_secret: Optional[str] = Field(env="API_SECRET")
    
    # Trading Parameters
    max_position_size: float = Field(default=0.1, ge=0.001, le=1.0)  # 10% of portfolio max
    max_daily_loss: float = Field(default=0.02, ge=0.0, le=0.5)  # 2% max daily loss
    trading_symbols: List[str] = Field(default=["BTC/USDT", "ETH/USDT"])
    
    # Model Parameters
    lookback_window: int = Field(default=100, ge=10, le=1000)
    prediction_horizon: int = Field(default=5, ge=1, le=50)
    retrain_interval: int = Field(default=24, ge=1)  # hours
    
    # Risk Management
    enable_stop_loss: bool = Field(default=True)
    stop_loss_pct: float = Field(default=0.02, ge=0.001, le=0.1)
    enable_take_profit: bool = Field(default=True)
    take_profit_pct: float = Field(default=0.04, ge=0.01, le=0.2)
    
    # Data Pipeline
    data_update_frequency: int = Field(default=60, ge=1)  # seconds
    max_data_points: int = Field(default=10000, ge=1000)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @validator("firebase_credentials_path")
    def validate_firebase_creds(cls, v):
        """Validate Firebase credentials file exists"""
        if v and not Path(v).exists():
            logger.warning(f"Firebase credentials file not found: {v}")
            # Don't raise error, as we might use other auth methods
        return v
    
    @validator("trading_symbols")
    def validate_symbols(cls, v):
        """Ensure trading symbols are properly formatted"""
        validated = []
        for symbol in v:
            if "/" not in symbol:
                logger.warning(f"Invalid symbol format: {symbol}. Expected format: BTC/USDT")
                continue
            validated.append(symbol.upper())
        return validated
    
    def get_exchange_config(self) -> Dict[str, Any]:
        """Get exchange configuration safely"""
        config = {
            "exchange_id": self.exchange_id,
            "options": {"defaultType": "spot"}
        }
        
        # Only add API keys if provided (for paper trading support)
        if self.api_key and self.api_secret:
            config.update({
                "apiKey": self.api_key,
                "secret": self.api_secret
            })
            logger.info(f"API keys configured for {self.exchange_id}")
        else:
            logger.warning("Running in paper trading mode - no API keys configured")
            
        return config

# Global configuration instance
config = TradingConfig()

def validate_config():
    """Validate configuration and log warnings"""
    warnings = []
    
    if not config.firebase_project_id:
        warnings.append("Firebase project ID not set - some features disabled")
    
    if config.environment == "production" and (not config.api_key or not config.api_secret):
        warnings.append("Production environment without API keys - trading disabled")
    
    if warnings