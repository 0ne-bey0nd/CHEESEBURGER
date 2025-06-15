"""
日志配置模块

定义日志格式、级别和其他配置选项
"""
import os
import json
import logging
from pathlib import Path
import sys

# 默认日志配置
DEFAULT_LOG_CONFIG = {
    "level": "info",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "filename_format": "cheeseburger_{timestamp}.log",
    "console_output": True,
    "file_output": True,
    "max_bytes": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# 日志级别映射
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

# 获取日志级别
def get_log_level(level_name):
    """
    根据字符串获取日志级别
    
    参数:
        level_name: 日志级别名称，可以是字符串或直接是int级别
        
    返回:
        int: 日志级别常量
    """
    if isinstance(level_name, int):
        return level_name
    
    return LOG_LEVELS.get(level_name.lower(), logging.INFO)

def load_log_config(config_path=None):
    """
    从配置文件加载日志配置
    
    参数:
        config_path: 配置文件路径，如果为None则查找默认位置
        
    返回:
        dict: 日志配置字典
    """
    # 默认配置
    config = DEFAULT_LOG_CONFIG.copy()
    
    # 如果未指定配置路径，尝试查找默认位置
    if config_path is None:
        # 尝试获取项目根目录
        try:
            if hasattr(sys.modules.get('src.config', None), 'RUNTIME_ROOT_PATH'):
                from src.config import RUNTIME_ROOT_PATH
                root_path = RUNTIME_ROOT_PATH
            else:
                # 获取当前脚本所在目录的上级目录的上级目录
                root_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))).resolve()
            
            # 检查config目录下是否有log_config.json
            config_path = os.path.join(root_path, 'config', 'log_config.json')
        except Exception:
            # 如果出现任何异常，使用默认配置
            return config
    
    # 如果配置文件存在，从中加载配置
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # 更新默认配置
                config.update(user_config)
        except Exception as e:
            # 如果加载配置出错，记录错误并使用默认配置
            print(f"加载日志配置文件出错: {e}，将使用默认配置")
    
    return config 