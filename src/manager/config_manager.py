"""
配置管理器

负责系统配置的管理
"""
import os
from pathlib import Path

# 导入系统模块
from src.system.config import read_config, save_config, ensure_data_config


class ConfigManager:
    """
    配置管理器
    
    负责配置的读取、保存和管理
    """
    
    def __init__(self, system_manager=None):
        """
        初始化配置管理器
        
        参数:
            system_manager: 系统管理器实例
        """
        from src.manager import SystemManager
        self.system_manager = system_manager if system_manager else SystemManager()
    
    def read_config(self, config_name='data_config.json'):
        """
        读取指定配置文件
        
        参数:
            config_name: 配置文件名，默认为'data_config.json'
        
        返回:
            dict: 配置文件内容
        """
        config_file = self.system_manager.CONFIG_PATH / config_name
        
        # 如果是数据配置且不存在，则创建默认配置
        if config_name == 'data_config.json' and not config_file.exists():
            ensure_data_config(str(self.system_manager.CONFIG_PATH))
        
        return read_config(config_file)
    
    def save_config(self, config, config_name='data_config.json'):
        """
        保存配置到文件
        
        参数:
            config: 配置字典
            config_name: 配置文件名，默认为'data_config.json'
        """
        config_file = self.system_manager.CONFIG_PATH / config_name
        save_config(config, config_file) 