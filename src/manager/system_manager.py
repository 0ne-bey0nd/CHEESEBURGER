"""
系统管理者模块

负责管理系统级别的资源、常量和初始化流程
"""
import os
import sys
from pathlib import Path

# 导入系统模块
from src.system.path import (
    get_runtime_root_path, get_config_path, 
    get_output_path, get_data_path, get_log_path
)
from src.system.constants import VERSION, SUPPORTED_EXCHANGES, SUPPORTED_TIMEFRAMES


class SystemManager:
    """
    系统管理者类
    
    负责系统的初始化和全局资源的管理
    """
    # 单例实例
    _instance = None
    
    # 预先定义所有属性
    RUNTIME_ROOT_PATH = None
    CONFIG_PATH = None
    OUTPUT_PATH = None
    DATA_PATH = None
    LOG_PATH = None
    
    # 系统常量
    VERSION = VERSION
    SUPPORTED_EXCHANGES = SUPPORTED_EXCHANGES
    SUPPORTED_TIMEFRAMES = SUPPORTED_TIMEFRAMES
    
    def __new__(cls, *args, **kwargs):
        """实现单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 初始化标志
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化系统管理者"""
        # 防止重复初始化
        if self._initialized:
            return
            
        # 初始化路径
        self._initialize_paths()
        
        # 标记为已初始化
        self._initialized = True
    
    def _initialize_paths(self):
        """初始化系统路径"""
        # 运行根目录
        self.RUNTIME_ROOT_PATH = get_runtime_root_path()
        
        # 将项目根目录添加到系统路径
        if str(self.RUNTIME_ROOT_PATH) not in sys.path:
            sys.path.insert(0, str(self.RUNTIME_ROOT_PATH))
        
        # 配置目录
        self.CONFIG_PATH = get_config_path(self.RUNTIME_ROOT_PATH)
        
        # 输出目录
        self.OUTPUT_PATH = get_output_path(self.RUNTIME_ROOT_PATH)
        
        # 数据目录
        self.DATA_PATH = get_data_path(self.RUNTIME_ROOT_PATH)
        
        # 日志目录
        self.LOG_PATH = get_log_path(self.OUTPUT_PATH)
    
    def initialize_system(self):
        """
        系统初始化方法，初始化各个模块
        
        返回:
            self: 系统管理者实例本身
        """
        return self
