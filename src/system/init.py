"""
系统初始化模块

提供系统初始化功能
"""

def initialize_system():
    """
    系统初始化
    
    初始化系统各个组件
    
    返回:
        tuple: (system_manager, config_manager, log_manager) 系统各管理器实例
    """
    from src.manager import SystemManager, ConfigManager, LogManager
    
    # 初始化系统管理器
    system_manager = SystemManager()
    system_manager.initialize_system()
    
    # 初始化配置管理器
    config_manager = ConfigManager(system_manager)
    
    # 初始化日志管理器
    log_manager = LogManager(system_manager)
    logger = log_manager.initialize()
    
    logger.info("系统初始化完成")
    
    return system_manager, config_manager, log_manager 