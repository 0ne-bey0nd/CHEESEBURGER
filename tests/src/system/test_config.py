"""
测试配置管理模块
"""
import os
import json
import pytest
import tempfile
import sys
from pathlib import Path

# 添加项目根目录到路径，以便导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.system.config import (
    read_config, save_config, get_default_data_config, ensure_data_config
)


class TestConfig:
    """测试配置管理模块"""
    
    def test_read_config(self):
        """测试读取配置文件"""
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
            with open(temp.name, 'w', encoding='utf-8') as f:
                config_data = {"test_key": "test_value", "number": 123}
                json.dump(config_data, f)
        
        try:
            # 读取临时配置文件
            config = read_config(temp.name)
            
            # 验证内容
            assert config == config_data
            
            # 验证不存在的配置文件
            with pytest.raises(FileNotFoundError):
                read_config("non_existent_file.json")
                
        finally:
            os.unlink(temp.name)
    
    def test_save_config(self):
        """测试保存配置"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
            pass
        
        try:
            # 保存配置
            config_data = {"test_key": "test_value", "number": 123}
            save_config(config_data, temp.name)
            
            # 验证文件内容
            with open(temp.name, 'r') as f:
                saved_config = json.load(f)
            
            assert saved_config == config_data
            
            # 测试创建不存在的目录
            nested_dir = os.path.join(tempfile.gettempdir(), "test_dir", "nested")
            nested_file = os.path.join(nested_dir, "config.json")
            
            # 确保目录不存在
            if os.path.exists(nested_dir):
                os.rmdir(nested_dir)
            
            # 保存配置到嵌套目录
            save_config(config_data, nested_file)
            
            # 验证目录和文件是否创建
            assert os.path.exists(nested_file)
            
            # 清理
            os.unlink(nested_file)
            os.rmdir(nested_dir)
            os.rmdir(os.path.dirname(nested_dir))
            
        finally:
            os.unlink(temp.name)
    
    def test_get_default_data_config(self):
        """测试获取默认数据配置"""
        config = get_default_data_config()
        
        # 验证必要字段是否存在
        assert "exchange_id" in config
        assert "symbol" in config
        assert "timeframe" in config
        assert "start_time" in config
        assert "end_time" in config
        assert "output_dir" in config
        
        # 验证字段类型
        assert isinstance(config["exchange_id"], str)
        assert isinstance(config["symbol"], str)
        assert isinstance(config["timeframe"], str)
        assert isinstance(config["start_time"], str)
        assert isinstance(config["end_time"], str)
        assert isinstance(config["output_dir"], str)
    
    def test_ensure_data_config(self):
        """测试确保数据配置文件存在"""
        # 使用临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 确保配置文件存在
            config_file = ensure_data_config(temp_dir)
            
            # 验证文件是否创建
            assert os.path.exists(config_file)
            
            # 验证文件内容
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # 验证是否包含默认配置的字段
            assert "exchange_id" in config
            assert "symbol" in config
            assert "timeframe" in config 