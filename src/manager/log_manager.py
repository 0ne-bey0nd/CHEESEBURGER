"""
日志管理器模块

负责日志的初始化和管理
"""
from src.log import setup_logger, get_logger
from src.log.config import load_log_config


class LogManager:
    """
    日志管理器
    
    负责日志的初始化和管理
    """
    
    def __init__(self, system_manager=None):
        """
        初始化日志管理器
        
        参数:
            system_manager: 系统管理器实例
        """
        from src.manager import SystemManager
        self.system_manager = system_manager if system_manager else SystemManager()
        
        # 日志记录器
        self._logger = None
    
    def initialize(self):
        """
        初始化日志系统
        
        返回:
            logger: 日志记录器对象
        """
        # 加载日志配置文件路径
        log_config_path = self.system_manager.CONFIG_PATH / 'log_config.json'
        
        # 配置日志
        if log_config_path.exists():
            # 如果配置文件存在，从中加载配置
            log_config = load_log_config(str(log_config_path))
        else:
            # 否则使用默认配置
            log_config = None
        
        # 创建日志记录器，并将日志文件保存在日志目录中
        self._logger = setup_logger(log_dir=str(self.system_manager.LOG_PATH), config=log_config)
        
        # 记录初始化信息
        self._logger.info(f"系统初始化完成，版本: {self.system_manager.VERSION}")
        self._logger.info(f"运行路径: {self.system_manager.RUNTIME_ROOT_PATH}")
        self._logger.info(f"配置目录: {self.system_manager.CONFIG_PATH}")
        self._logger.info(f"输出目录: {self.system_manager.OUTPUT_PATH}")
        self._logger.info(f"数据目录: {self.system_manager.DATA_PATH}")
        self._logger.info(f"日志目录: {self.system_manager.LOG_PATH}")
        
        return self._logger
    
    def get_logger(self):
        """
        获取日志管理器
        
        返回:
            Logger: 日志记录器对象
        """
        if not self._logger:
            self._logger = self.initialize()
        return self._logger 