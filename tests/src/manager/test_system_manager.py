"""
测试系统管理者模块
"""
import os
import pytest
from pathlib import Path
import sys
import tempfile

# 添加项目根目录到路径，以便导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.manager import SystemManager


class TestSystemManager:
    """测试系统管理者类"""
    
    def test_singleton(self):
        """测试单例模式"""
        # 创建两个实例
        manager1 = SystemManager()
        manager2 = SystemManager()
        
        # 验证两个实例是同一个对象
        assert manager1 is manager2
    
    def test_paths(self):
        """测试路径管理"""
        manager = SystemManager()
        
        # 验证是否有这些属性
        assert hasattr(manager, "RUNTIME_ROOT_PATH"), "缺少 RUNTIME_ROOT_PATH 属性"
        assert hasattr(manager, "CONFIG_PATH"), "缺少 CONFIG_PATH 属性"
        assert hasattr(manager, "OUTPUT_PATH"), "缺少 OUTPUT_PATH 属性"
        assert hasattr(manager, "DATA_PATH"), "缺少 DATA_PATH 属性"
        assert hasattr(manager, "LOG_PATH"), "缺少 LOG_PATH 属性"
        
        # 验证属性类型是否正确
        assert isinstance(manager.RUNTIME_ROOT_PATH, Path), "RUNTIME_ROOT_PATH 类型错误"
        assert isinstance(manager.CONFIG_PATH, Path), "CONFIG_PATH 类型错误"
        assert isinstance(manager.OUTPUT_PATH, Path), "OUTPUT_PATH 类型错误"
        assert isinstance(manager.DATA_PATH, Path), "DATA_PATH 类型错误"
        assert isinstance(manager.LOG_PATH, Path), "LOG_PATH 类型错误"
        
        # 验证路径是否存在
        assert manager.RUNTIME_ROOT_PATH.exists(), "RUNTIME_ROOT_PATH 路径不存在"
        assert manager.CONFIG_PATH.exists(), "CONFIG_PATH 路径不存在"
        assert manager.OUTPUT_PATH.exists(), "OUTPUT_PATH 路径不存在"
        assert manager.DATA_PATH.exists(), "DATA_PATH 路径不存在"
        assert manager.LOG_PATH.exists(), "LOG_PATH 路径不存在"
        
        # 验证路径是否符合预期
        assert manager.CONFIG_PATH == manager.RUNTIME_ROOT_PATH / 'config', "CONFIG_PATH 路径不符合预期"
        assert manager.OUTPUT_PATH == manager.RUNTIME_ROOT_PATH / 'output', "OUTPUT_PATH 路径不符合预期"
        assert manager.DATA_PATH == manager.OUTPUT_PATH / 'data', "DATA_PATH 路径不符合预期"
        assert manager.LOG_PATH == manager.OUTPUT_PATH / 'logs', "LOG_PATH 路径不符合预期"
    
    def test_initialize_system(self):
        """测试系统初始化"""
        manager = SystemManager()
        result = manager.initialize_system()
        
        # 验证初始化方法是否返回了自身
        assert result is manager