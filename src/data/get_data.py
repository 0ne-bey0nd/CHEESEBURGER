"""数据获取模块，从交易所API获取历史K线数据并保存为CSV格式"""

import os
import pandas as pd
import ccxt
import time
from datetime import datetime, timedelta
from src.log import get_logger
from src.manager import SystemManager, ConfigManager

# 获取系统管理器
system_manager = SystemManager()

# 获取配置管理器
config_manager = ConfigManager(system_manager)

# 读取数据配置
data_config = config_manager.read_config('data_config.json')

# 获取配置好的logger
logger = get_logger()

# 默认保存数据的目录
DEFAULT_DATA_DIR = system_manager.DATA_PATH


def ensure_data_dir(data_dir=None):
    """确保数据目录存在
    
    Args:
        data_dir (str, optional): 数据目录路径，默认为系统数据目录
        
    Returns:
        str: 数据目录的完整路径
    """
    if data_dir is None:
        data_dir = DEFAULT_DATA_DIR

    if not os.path.exists(data_dir):
        logger.info(f"创建数据目录: {data_dir}")
        os.makedirs(data_dir)

    return data_dir


def get_exchange(exchange_id='okx', config=None):
    """获取交易所实例
    
    Args:
        exchange_id (str): 交易所ID，默认为'okx'
        config (dict, optional): 额外的配置参数
        
    Returns:
        ccxt.Exchange: 交易所API实例
    """
    # 默认配置
    default_config = {
        'enableRateLimit': True,  # 启用请求频率限制
    }

    # 如果全局配置中有交易所配置，则使用它
    if 'exchange_config' in data_config:
        default_config.update(data_config['exchange_config'])

    # 合并传入的配置
    if config:
        default_config.update(config)

    try:
        # 创建交易所实例
        logger.info(f"初始化交易所API: {exchange_id}")
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class(default_config)
        return exchange
    except Exception as e:
        logger.error(f"初始化交易所API失败: {str(e)}")
        raise


def fetch_ohlcv(exchange, symbol, timeframe='1h', since=None, limit=1000):
    """获取K线数据
    
    Args:
        exchange (ccxt.Exchange): 交易所API实例
        symbol (str): 交易对，如 'ETH/USDT'
        timeframe (str): K线周期，如 '1h', '1d'
        since (int, optional): 起始时间戳(毫秒)
        limit (int): 单次请求的K线数量
        
    Returns:
        list: K线数据列表
    """
    try:
        logger.info(
            f"获取 {symbol} {timeframe} K线数据，起始时间: {datetime.fromtimestamp(since / 1000) if since else 'None'}")
        # 获取K线数据
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
        logger.info(f"获取到 {len(ohlcv)} 条K线数据")
        return ohlcv
    except Exception as e:
        logger.error(f"获取K线数据失败: {str(e)}")
        raise


def fetch_full_history(exchange, symbol, timeframe='1h', start_date=None, end_date=None):
    """获取完整的历史K线数据
    
    Args:
        exchange (ccxt.Exchange): 交易所API实例
        symbol (str): 交易对，如 'ETH/USDT'
        timeframe (str): K线周期，如 '1h', '1d'
        start_date (str): 起始日期，格式 'YYYY-MM-DD'
        end_date (str): 结束日期，格式 'YYYY-MM-DD'，默认为当前日期
        
    Returns:
        list: 完整的K线数据列表
    """
    # 处理日期参数
    if start_date:
        start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
    else:
        # 默认获取30天的数据
        start_timestamp = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)

    if end_date:
        end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
    else:
        end_timestamp = int(datetime.now().timestamp() * 1000)

    # 确保时间范围有效
    if end_timestamp <= start_timestamp:
        raise ValueError("结束日期必须晚于起始日期")

    # 获取交易所的K线周期毫秒数
    timeframes = exchange.timeframes
    if timeframe not in timeframes:
        raise ValueError(f"不支持的K线周期: {timeframe}")

    # 获取完整历史数据
    all_ohlcv = []
    since = start_timestamp

    while since < end_timestamp:
        try:
            logger.info(f"获取从 {datetime.fromtimestamp(since / 1000)} 开始的数据")
            ohlcv = fetch_ohlcv(exchange, symbol, timeframe, since)

            if not ohlcv or len(ohlcv) == 0:
                logger.warning("没有获取到更多数据，可能已到达数据末尾")
                break

            all_ohlcv.extend(ohlcv)

            # 更新since为最后一条记录的时间+1
            since = ohlcv[-1][0] + 1

            # 防止请求过于频繁
            time.sleep(exchange.rateLimit / 1000)

        except Exception as e:
            logger.error(f"获取数据出错: {str(e)}")
            time.sleep(10)  # 出错后等待一段时间再重试

    # 去重并按时间排序
    unique_ohlcv = []
    timestamps = set()

    for candle in all_ohlcv:
        if candle[0] not in timestamps:
            timestamps.add(candle[0])
            unique_ohlcv.append(candle)

    unique_ohlcv.sort(key=lambda x: x[0])

    # 过滤结束日期之后的数据
    filtered_ohlcv = [candle for candle in unique_ohlcv if candle[0] <= end_timestamp]

    logger.info(f"共获取 {len(filtered_ohlcv)} 条有效K线数据")
    return filtered_ohlcv


def save_to_csv(ohlcv_data, symbol, timeframe, data_dir=None):
    """将K线数据保存为CSV文件
    
    Args:
        ohlcv_data (list): K线数据列表
        symbol (str): 交易对，如 'ETH/USDT'
        timeframe (str): K线周期，如 '1h', '1d'
        data_dir (str, optional): 保存数据的目录
        
    Returns:
        str: CSV文件的路径
    """
    # 确保数据目录存在
    data_dir = ensure_data_dir(data_dir)

    # 处理符号名称，替换/为-
    symbol_filename = symbol.replace('/', '-')
    symbol_filename = symbol_filename.replace(':', '-')

    # 构建文件名
    filename = f"{symbol_filename}_{timeframe}.csv"
    file_path = os.path.join(data_dir, filename)

    # 将数据转换为DataFrame
    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # 添加日期时间列
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

    # 保存为CSV
    logger.info(f"保存数据到文件: {file_path}")
    df.to_csv(file_path, index=False)

    return file_path


def fetch_and_save_data(symbol=None, timeframe=None, start_date=None, end_date=None,
                        exchange_id=None, data_dir=None, config=None):
    """获取并保存历史K线数据
    
    Args:
        symbol (str): 交易对，如 'ETH/USDT'
        timeframe (str): K线周期，如 '1h', '1d'
        start_date (str): 起始日期，格式 'YYYY-MM-DD'
        end_date (str): 结束日期，格式 'YYYY-MM-DD'
        exchange_id (str): 交易所ID
        data_dir (str, optional): 保存数据的目录
        config (dict, optional): 交易所API配置
        
    Returns:
        str: 保存的CSV文件路径
    """
    try:
        # 使用配置文件中的默认值
        if symbol is None:
            symbol = data_config.get('symbol', 'ETH/USDT')
        
        if timeframe is None:
            timeframe = data_config.get('timeframe', '1h')
            
        if exchange_id is None:
            exchange_id = data_config.get('exchange_id', 'okx')
            
        # 获取交易所实例
        exchange = get_exchange(exchange_id, config)

        # 加载市场
        exchange.load_markets()

        # 检查交易对是否存在
        if symbol not in exchange.symbols:
            logger.error(f"交易对 {symbol} 在交易所 {exchange_id} 中不存在")
            available_symbols = exchange.symbols[:10]  # 获取前10个可用交易对
            logger.info(f"可用交易对示例: {available_symbols}")
            raise ValueError(f"交易对 {symbol} 在交易所 {exchange_id} 中不存在")

        # 获取完整历史数据
        ohlcv_data = fetch_full_history(exchange, symbol, timeframe, start_date, end_date)

        # 保存为CSV
        file_path = save_to_csv(ohlcv_data, symbol, timeframe, data_dir)

        return file_path

    except Exception as e:
        logger.error(f"获取并保存数据失败: {str(e)}")
        raise


if __name__ == "__main__":
    # 从配置中获取参数
    symbol = data_config.get("symbol", "ETH/USDT")
    timeframe = data_config.get("timeframe", "1h")
    exchange_id = data_config.get("exchange_id", "okx")
    
    # 可以在命令行中覆盖这些参数
    start_date = '2023-05-01'  # 起始日期
    end_date = None  # 结束日期，默认为当前日期
    
    # 从配置中获取交易所配置
    config = data_config.get("exchange_config", {})
    
    try:
        # 获取并保存数据
        file_path = fetch_and_save_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            exchange_id=exchange_id,
            config=config
        )

        logger.info(f"数据已保存至: {file_path}")

    except Exception as e:
        logger.error(f"数据获取失败: {str(e)}")
