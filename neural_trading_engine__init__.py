"""
NeuralTrading Engine - Adaptive Market Intelligence System
A cognitive trading architecture with Council of Neural Specialists and Meta-Executor
"""

__version__ = "0.1.0"
__author__ = "Evolution Ecosystem"

from .core.trading_engine import TradingEngine
from .core.meta_executor import MetaExecutor
from .data.market_data_pipeline import MarketDataPipeline

__all__ = ["TradingEngine", "MetaExecutor", "MarketDataPipeline"]