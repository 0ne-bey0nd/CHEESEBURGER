"""
测试路径管理模块
"""
import os
import pytest
from pathlib import Path
import sys
import tempfile

# 添加项目根目录到路径，以便导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.system.path import (
    get_runtime_root_path, get_config_path, get_output_path, 
    get_data_path, get_log_path
)


class TestPath:
    """测试路径管理"""
    
    def test_get_runtime_root_path(self):
        """测试获取运行根目录"""
        path = get_runtime_root_path()
        assert isinstance(path, Path)
        assert path.exists()
        
        # 验证路径指向项目根目录
        assert (path / "src").exists()
        assert (path / "tests").exists()
    
    def test_get_config_path(self):
        """测试获取配置目录"""
        # 使用默认参数
        path = get_config_path()
        assert isinstance(path, Path)
        assert path.exists()
        assert path.is_dir()
        
        # 使用自定义运行根目录
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = get_config_path(temp_dir)
            assert isinstance(custom_path, Path)
            assert custom_path.exists()
            assert custom_path.name == "config"
            assert str(custom_path).startswith(temp_dir)
    
    def test_get_output_path(self):
        """测试获取输出目录"""
        # 使用默认参数
        path = get_output_path()
        assert isinstance(path, Path)
        assert path.exists()
        assert path.is_dir()
        
        # 使用自定义运行根目录
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = get_output_path(temp_dir)
            assert isinstance(custom_path, Path)
            assert custom_path.exists()
            assert custom_path.name == "output"
            assert str(custom_path).startswith(temp_dir)
    
    def test_get_data_path(self):
        """测试获取数据目录"""
        # 使用默认参数
        path = get_data_path()
        assert isinstance(path, Path)
        assert path.exists()
        assert path.is_dir()
        
        # 使用自定义运行根目录
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = get_data_path(temp_dir)
            assert isinstance(custom_path, Path)
            assert custom_path.exists()
            assert custom_path.name == "data"
            assert str(custom_path).startswith(temp_dir)
    
    def test_get_log_path(self):
        """测试获取日志目录"""
        # 使用默认参数
        path = get_log_path()
        assert isinstance(path, Path)
        assert path.exists()
        assert path.is_dir()
        
        # 使用自定义输出目录
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = get_log_path(temp_dir)
            assert isinstance(custom_path, Path)
            assert custom_path.exists()
            assert custom_path.name == "logs"
            assert str(custom_path).startswith(temp_dir) 