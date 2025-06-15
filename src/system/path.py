"""
路径管理模块

负责获取各种系统路径
"""
import os
from pathlib import Path


def get_runtime_root_path():
    """
    获取项目运行根目录路径，默认是项目根目录
    
    返回:
        Path: 项目运行根目录的绝对路径
    """
    # 获取当前文件所在目录的上上级目录
    return Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))).resolve()


def get_config_path(runtime_root=None):
    """
    获取配置目录路径
    
    参数:
        runtime_root: 运行根目录，如果为None则自动获取
    
    返回:
        Path: 配置目录的绝对路径
    """
    if runtime_root is None:
        runtime_root = get_runtime_root_path()
        
    config_path = Path(runtime_root) / 'config'
    os.makedirs(config_path, exist_ok=True)
    return config_path


def get_output_path(runtime_root=None):
    """
    获取输出目录路径
    
    参数:
        runtime_root: 运行根目录，如果为None则自动获取
    
    返回:
        Path: 输出目录的绝对路径
    """
    if runtime_root is None:
        runtime_root = get_runtime_root_path()
        
    output_path = Path(runtime_root) / 'output'
    os.makedirs(output_path, exist_ok=True)
    return output_path

def get_data_path(output_path=None):
    """
    获取数据目录路径
    
    参数:
        output_path: 输出目录路径，如果为None则自动获取
    
    返回:
        Path: 数据目录的绝对路径
    """
    # 获取输出目录
    output_path = get_output_path(output_path)
    
    # 在输出目录下创建data目录
    data_path = output_path / 'data'
    os.makedirs(data_path, exist_ok=True)
    return data_path


def get_log_path(output_path=None):
    """
    获取日志目录路径
    
    参数:
        output_path: 输出目录路径，如果为None则自动获取
    
    返回:
        Path: 日志目录的绝对路径
    """
    if output_path is None:
        output_path = get_output_path()
        
    log_path = Path(output_path) / 'logs'
    os.makedirs(log_path, exist_ok=True)
    return log_path
