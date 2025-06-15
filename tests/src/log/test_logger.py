"""
测试日志记录器模块
"""
import os
import logging
import tempfile
import pytest
from pathlib import Path
import sys
import json

# 添加项目根目录到路径，以便导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.log.logger import setup_logger, get_logger, _get_log_directory, _create_formatter
from src.log.config import get_log_level, load_log_config


class TestLogger:
    """测试日志记录器"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时目录用于存放日志
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_dir = self.temp_dir.name
        
        # 创建临时配置文件
        self.temp_config_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_config_dir.name, "log_config.json")
        
        # 重置全局日志记录器
        import src.log.logger
        src.log.logger._GLOBAL_LOGGER = None
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        # 关闭临时文件处理器
        import src.log.logger
        for handler in src.log.logger._FILE_HANDLERS:
            handler.close()
        
        # 清理临时目录
        self.temp_dir.cleanup()
        self.temp_config_dir.cleanup()
    
    def test_get_log_directory(self):
        """测试获取日志目录"""
        # 使用指定目录
        log_dir = _get_log_directory(self.log_dir)
        assert log_dir == self.log_dir
        
        # 使用默认目录
        default_dir = _get_log_directory()
        assert os.path.exists(default_dir)
        assert os.path.basename(default_dir) == "logs"
    
    def test_create_formatter(self):
        """测试创建格式化器"""
        # 默认格式
        config = {}
        formatter = _create_formatter(config)
        assert formatter._fmt == "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
        
        # 自定义格式
        config = {
            "format": "%(asctime)s | %(name)s | %(message)s",
            "date_format": "%Y/%m/%d"
        }
        formatter = _create_formatter(config)
        assert formatter._fmt == "%(asctime)s | %(name)s | %(message)s"
        assert formatter.datefmt == "%Y/%m/%d"
        
        # 测试修复.%f格式
        config = {"date_format": "%Y-%m-%d %H:%M:%S.%f"}
        formatter = _create_formatter(config)
        assert formatter.datefmt == "%Y-%m-%d %H:%M:%S"
    
    def test_setup_logger_default_config(self):
        """测试使用默认配置设置日志记录器"""
        logger = setup_logger("test_logger", self.log_dir)
        
        # 验证日志记录器是否创建成功
        assert logger is not None
        assert logger.name == "test_logger"
        
        # 验证处理器数量
        # 默认配置下应该有两个处理器：控制台处理器和文件处理器
        assert len(logger.handlers) == 2
        
        # 验证第一个处理器是控制台处理器
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        
        # 验证第二个处理器是文件处理器
        assert isinstance(logger.handlers[1], logging.handlers.RotatingFileHandler)
        
        # 验证日志目录中是否有日志文件
        log_files = list(Path(self.log_dir).glob("*.log"))
        assert len(log_files) == 1
    
    def test_setup_logger_custom_config(self):
        """测试使用自定义配置设置日志记录器"""
        # 自定义配置
        custom_config = {
            "level": "debug",
            "format": "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S",
            "filename_format": "test_{timestamp}.log",
            "console_output": True,
            "file_output": True
        }
        
        logger = setup_logger("test_logger_custom", self.log_dir, custom_config)
        
        # 验证日志记录器是否创建成功
        assert logger is not None
        assert logger.name == "test_logger_custom"
        assert logger.level == logging.DEBUG
        
        # 验证处理器数量
        assert len(logger.handlers) == 2
        
        # 验证日志目录中是否有日志文件
        log_files = list(Path(self.log_dir).glob("test_*.log"))
        assert len(log_files) == 1
    
    def test_setup_logger_console_only(self):
        """测试只有控制台输出的日志记录器"""
        # 只有控制台输出的配置
        console_only_config = {
            "level": "info",
            "console_output": True,
            "file_output": False
        }
        
        logger = setup_logger("test_logger_console", self.log_dir, console_only_config)
        
        # 验证日志记录器是否创建成功
        assert logger is not None
        
        # 验证处理器数量，只应该有一个控制台处理器
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        
        # 验证日志目录中没有日志文件
        log_files = list(Path(self.log_dir).glob("*.log"))
        assert len(log_files) == 0
    
    def test_setup_logger_file_only(self):
        """测试只有文件输出的日志记录器"""
        # 只有文件输出的配置
        file_only_config = {
            "level": "info",
            "console_output": False,
            "file_output": True
        }
        
        logger = setup_logger("test_logger_file", self.log_dir, file_only_config)
        
        # 验证日志记录器是否创建成功
        assert logger is not None
        
        # 验证处理器数量，只应该有一个文件处理器
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.handlers.RotatingFileHandler)
        
        # 验证日志目录中是否有日志文件
        log_files = list(Path(self.log_dir).glob("*.log"))
        assert len(log_files) == 1
    
    def test_get_logger_creates_global_logger(self):
        """测试获取全局日志记录器会创建一个新的全局记录器"""
        # 确保全局记录器被重置
        import src.log.logger
        src.log.logger._GLOBAL_LOGGER = None
        
        logger = get_logger()
        
        # 验证日志记录器是否创建成功
        assert logger is not None
        assert logger.name == "cheeseburger"
    
    def test_get_logger_returns_existing_logger(self):
        """测试获取全局日志记录器会返回已存在的全局记录器"""
        # 首先创建一个全局记录器
        first_logger = get_logger()
        
        # 再次获取全局记录器
        second_logger = get_logger()
        
        # 验证两次获取的是同一个记录器
        assert first_logger is second_logger
    
    def test_load_log_config(self):
        """测试从配置文件加载日志配置"""
        # 创建测试配置文件
        test_config = {
            "level": "debug",
            "format": "%(asctime)s | %(levelname)s | %(message)s",
            "console_output": False
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        # 加载配置
        config = load_log_config(self.config_path)
        
        # 验证配置是否正确合并
        assert config["level"] == "debug"
        assert config["format"] == "%(asctime)s | %(levelname)s | %(message)s"
        assert config["console_output"] == False
        # 其他配置应使用默认值
        assert "file_output" in config
        assert "max_bytes" in config


class TestLoggerConfig:
    """测试日志配置"""
    
    def test_get_log_level_from_string(self):
        """测试从字符串获取日志级别"""
        assert get_log_level("debug") == logging.DEBUG
        assert get_log_level("info") == logging.INFO
        assert get_log_level("warning") == logging.WARNING
        assert get_log_level("error") == logging.ERROR
        assert get_log_level("critical") == logging.CRITICAL
        
        # 测试大小写不敏感
        assert get_log_level("DEBUG") == logging.DEBUG
        assert get_log_level("Info") == logging.INFO
        
        # 测试无效的字符串，应该返回默认的INFO级别
        assert get_log_level("invalid") == logging.INFO
    
    def test_get_log_level_from_int(self):
        """测试从整数获取日志级别"""
        assert get_log_level(logging.DEBUG) == logging.DEBUG
        assert get_log_level(logging.INFO) == logging.INFO
        assert get_log_level(logging.WARNING) == logging.WARNING
        assert get_log_level(logging.ERROR) == logging.ERROR
        assert get_log_level(logging.CRITICAL) == logging.CRITICAL


def test_logger_functionality():
    """测试日志记录器的基本功能"""
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 设置日志记录器
        config = {"level": "debug"}
        logger = setup_logger("test_func", temp_dir, config)
        
        # 记录不同级别的日志
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        logger.critical("This is a critical message")
        
        # 验证日志文件是否存在
        log_files = list(Path(temp_dir).glob("*.log"))
        assert len(log_files) > 0
        
        # 关闭处理器
        import src.log.logger
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

