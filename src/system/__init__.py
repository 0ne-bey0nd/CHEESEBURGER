"""
系统模块包

包含系统路径、配置等基础功能
"""
from src.system.init import initialize_system
from src.system.constants import VERSION, SUPPORTED_EXCHANGES, SUPPORTED_TIMEFRAMES

__all__ = [
    'initialize_system',
    'VERSION',
    'SUPPORTED_EXCHANGES',
    'SUPPORTED_TIMEFRAMES'
]
