"""
日志记录器模块

提供日志记录器的创建和获取功能
"""
import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
import sys
import atexit

# 导入日志配置
from src.log.config import get_log_level, load_log_config

# 全局日志对象
_GLOBAL_LOGGER = None
# 全局文件处理器
_FILE_HANDLERS = []


def _close_handlers():
    """关闭所有文件处理器"""
    for handler in _FILE_HANDLERS:
        handler.close()


# 注册退出函数，确保文件句柄被正确关闭
atexit.register(_close_handlers)


def _get_log_directory(log_dir=None):
    """
    获取日志目录路径
    
    参数:
        log_dir: 指定的日志目录，如果为None则使用默认目录
        
    返回:
        str: 日志目录的绝对路径
    """
    # 如果指定了日志目录，直接使用
    if log_dir is not None:
        directory = log_dir
    else:
        try:
            # 首先尝试从系统管理器获取日志目录
            from src.manager import SystemManager
            directory = str(SystemManager().LOG_PATH)
        except ImportError:
            # 如果系统管理器不可用，尝试使用路径模块获取
            try:
                from src.system.path import get_log_path
                directory = str(get_log_path())
            except ImportError:
                # 如果路径模块不可用，直接报错
                raise ImportError("无法获取日志目录，请确保src.manager或src.system.path模块已正确加载")
    
    # 确保日志目录存在
    os.makedirs(directory, exist_ok=True)
    return directory


def _create_formatter(config):
    """
    创建日志格式化器
    
    参数:
        config: 日志配置
        
    返回:
        logging.Formatter: 格式化器对象
    """
    # 获取格式化字符串和日期格式
    format_string = config.get("format", "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
    date_format = config.get("date_format", "%Y-%m-%d %H:%M:%S")
    
    # 修复日期格式，确保格式正确
    if date_format == "%Y-%m-%d %H:%M:%S.%f":
        date_format = "%Y-%m-%d %H:%M:%S"
    
    # 创建并返回格式化器
    return logging.Formatter(format_string, datefmt=date_format)


def _add_console_handler(logger, config, formatter):
    """
    为日志记录器添加控制台处理器
    
    参数:
        logger: 日志记录器对象
        config: 日志配置
        formatter: 格式化器对象
    """
    if config.get("console_output", True):
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)


def _add_file_handler(logger, config, formatter, log_dir):
    """
    为日志记录器添加文件处理器
    
    参数:
        logger: 日志记录器对象
        config: 日志配置
        formatter: 格式化器对象
        log_dir: 日志目录路径
    
    返回:
        logging.FileHandler: 文件处理器对象，如果没有创建则返回None
    """
    global _FILE_HANDLERS
    
    if config.get("file_output", True):
        # 生成时间戳和文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_format = config.get("filename_format", "cheeseburger_{timestamp}.log")
        log_file = os.path.join(log_dir, filename_format.format(timestamp=timestamp))
        
        # 创建RotatingFileHandler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=config.get("max_bytes", 10 * 1024 * 1024),  # 默认10MB
            backupCount=config.get("backup_count", 5)
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 保存文件处理器以便稍后关闭
        _FILE_HANDLERS.append(file_handler)
        
        return file_handler
    
    return None


def setup_logger(logger_name="cheeseburger", log_dir=None, config=None):
    """
    设置日志记录器
    
    参数:
        logger_name: 日志记录器名称，默认为"cheeseburger"
        log_dir: 日志目录路径，如果为None，则使用系统管理器中的日志目录
        config: 日志配置，如果为None，则从系统管理器中加载配置
    
    返回:
        Logger: 日志记录器对象
    """
    global _GLOBAL_LOGGER
    
    # 如果已经设置过全局日志记录器，直接返回
    if _GLOBAL_LOGGER is not None and logger_name == "cheeseburger":
        return _GLOBAL_LOGGER
    
    # 加载配置
    if config is None:
        # 尝试从文件加载配置
        try:
            from src.manager import SystemManager
            config_path = SystemManager().CONFIG_PATH / 'log_config.json'
            if config_path.exists():
                config = load_log_config(str(config_path))
            else:
                config = load_log_config()
        except ImportError:
            config = load_log_config()
    
    # 获取日志目录
    log_directory = _get_log_directory(log_dir)
    
    # 创建或获取日志记录器
    logger = logging.getLogger(logger_name)
    
    # 设置日志级别
    logger_level = get_log_level(config.get("level", "info"))
    logger.setLevel(logger_level)
    
    # 清除已有的处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 创建格式化器
    formatter = _create_formatter(config)
    
    # 添加控制台处理器
    _add_console_handler(logger, config, formatter)
    
    # 添加文件处理器
    _add_file_handler(logger, config, formatter, log_directory)
    
    # 设置全局日志记录器
    if logger_name == "cheeseburger":
        _GLOBAL_LOGGER = logger
    
    # 记录初始化完成消息
    logger.debug("日志系统初始化完成")
    
    return logger


def get_logger():
    """
    获取全局日志记录器
    
    如果全局日志记录器不存在，则创建一个新的
    
    返回:
        Logger: 日志记录器对象
    """
    global _GLOBAL_LOGGER
    
    if _GLOBAL_LOGGER is None:
        _GLOBAL_LOGGER = setup_logger()
    
    return _GLOBAL_LOGGER 