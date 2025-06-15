"""
配置管理模块

负责系统配置文件的读写
"""
import os
import json
from pathlib import Path
from datetime import datetime


def read_config(config_file):
    """
    读取配置文件
    
    参数:
        config_file: 配置文件路径
    
    返回:
        dict: 配置文件内容
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config


def save_config(config, config_file):
    """
    保存配置到文件
    
    参数:
        config: 配置字典
        config_file: 配置文件路径
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def get_default_data_config():
    """
    获取默认数据获取配置
    
    返回:
        dict: 默认配置
    """
    return {
        "exchange_id": "okx",
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "start_time": datetime.now().strftime("%Y-%m-%d 00:00:00"),
        "end_time": (datetime.now().replace(hour=23, minute=59, second=59)).strftime("%Y-%m-%d %H:%M:%S"),
        "output_dir": "output"
    }


def ensure_data_config(config_path):
    """
    确保数据配置文件存在，如果不存在则创建默认配置
    
    参数:
        config_path: 配置目录路径
        
    返回:
        str: 配置文件路径
    """
    config_file = os.path.join(config_path, 'data_config.json')
    
    if not os.path.exists(config_file):
        # 创建默认配置
        default_config = get_default_data_config()
        save_config(default_config, config_file)
        
    return config_file 