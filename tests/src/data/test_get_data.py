"""
测试数据获取模块
"""
import os
import json
import pytest
import pandas as pd
import tempfile
from unittest import mock
from datetime import datetime, timedelta
import sys

# 添加项目根目录到路径，以便导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# 导入被测试模块
from src.data.get_data import (
    ensure_data_dir, get_exchange, fetch_ohlcv, fetch_full_history,
    save_to_csv, fetch_and_save_data
)

from src.manager.config_manager import ConfigManager

class TestGetData:
    """测试数据获取模块"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时目录
        self.temp_dir = tempfile.TemporaryDirectory()

        # 创建测试配置
        self.test_config = {
            'enableRateLimit': True,
            'proxies': {
                'http': 'http://127.0.0.1:10808/',
                'https': 'http://127.0.0.1:10808/'
            },
            'options': {'defaultType': 'swap'}
        }
        ConfigManager().

        # 模拟K线数据
        self.mock_ohlcv_data = [
            [1625097600000, 35000.0, 35500.0, 34800.0, 35200.0, 100.0],  # 2021-07-01 00:00:00
            [1625101200000, 35200.0, 35800.0, 35100.0, 35700.0, 120.0],  # 2021-07-01 01:00:00
            [1625104800000, 35700.0, 36000.0, 35500.0, 35900.0, 150.0],  # 2021-07-01 02:00:00
        ]

    def teardown_method(self):
        """每个测试方法后的清理"""
        # 清理临时目录
        self.temp_dir.cleanup()

    def test_ensure_data_dir(self):
        """测试确保数据目录存在"""
        # 测试使用指定目录
        test_dir = os.path.join(self.temp_dir.name, "test_data")
        result = ensure_data_dir(test_dir)

        # 验证目录是否创建
        assert os.path.exists(test_dir)
        assert os.path.isdir(test_dir)
        assert result == test_dir

    @mock.patch('ccxt.okx')
    def test_get_exchange(self, mock_okx):
        """测试获取交易所实例"""
        # 设置模拟交易所
        mock_exchange = mock.MagicMock()
        mock_okx.return_value = mock_exchange
        
        # 测试默认参数
        exchange = get_exchange()
        assert exchange == mock_exchange
        mock_okx.assert_called_once()
        
        # 测试自定义配置
        mock_okx.reset_mock()
        exchange = get_exchange('okx', self.test_config)
        assert exchange == mock_exchange
        mock_okx.assert_called_once_with(self.test_config)
    
    @mock.patch('ccxt.okx')
    def test_fetch_ohlcv(self, mock_okx):
        """测试获取K线数据"""
        # 设置模拟交易所
        mock_exchange = mock.MagicMock()
        mock_exchange.fetch_ohlcv.return_value = self.mock_ohlcv_data
        mock_okx.return_value = mock_exchange
        
        # 获取交易所实例
        exchange = get_exchange()
        
        # 测试获取K线数据
        symbol = "BTC/USDT"
        timeframe = "1h"
        since = int(datetime.now().timestamp() * 1000)
        limit = 100
        
        result = fetch_ohlcv(exchange, symbol, timeframe, since, limit)
        
        # 验证结果
        assert result == self.mock_ohlcv_data
        mock_exchange.fetch_ohlcv.assert_called_once_with(symbol, timeframe, since, limit)
    
    @mock.patch('src.data.get_data.fetch_ohlcv')
    @mock.patch('ccxt.okx')
    def test_fetch_full_history(self, mock_okx, mock_fetch_ohlcv):
        """测试获取完整的历史K线数据"""
        # 设置模拟交易所
        mock_exchange = mock.MagicMock()
        mock_exchange.timeframes = {'1h': 3600000}
        mock_exchange.rateLimit = 1000
        mock_okx.return_value = mock_exchange
        
        # 模拟fetch_ohlcv的返回值
        mock_fetch_ohlcv.side_effect = [
            self.mock_ohlcv_data[:1],  # 第一次调用返回第一条数据
            self.mock_ohlcv_data[1:2],  # 第二次调用返回第二条数据
            self.mock_ohlcv_data[2:],   # 第三次调用返回第三条数据
            []  # 第四次调用返回空列表，表示没有更多数据
        ]
        
        # 获取交易所实例
        exchange = get_exchange()
        
        # 测试获取完整历史数据
        symbol = "BTC/USDT"
        timeframe = "1h"
        start_date = "2021-07-01"
        end_date = "2021-07-02"
        
        result = fetch_full_history(exchange, symbol, timeframe, start_date, end_date)
        
        # 验证结果
        assert len(result) == 3
        assert result == self.mock_ohlcv_data
        assert mock_fetch_ohlcv.call_count == 4
    
    def test_save_to_csv(self):
        """测试将K线数据保存为CSV文件"""
        # 测试保存数据
        symbol = "BTC/USDT"
        timeframe = "1h"
        data_dir = self.temp_dir.name
        
        file_path = save_to_csv(self.mock_ohlcv_data, symbol, timeframe, data_dir)
        
        # 验证文件是否创建
        assert os.path.exists(file_path)
        
        # 验证文件内容
        df = pd.read_csv(file_path)
        assert len(df) == 3
        assert list(df.columns) == ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'datetime']
        assert df['timestamp'].iloc[0] == self.mock_ohlcv_data[0][0]
    
    @mock.patch('src.data.get_data.fetch_full_history')
    @mock.patch('src.data.get_data.save_to_csv')
    @mock.patch('ccxt.okx')
    def test_fetch_and_save_data(self, mock_okx, mock_save_to_csv, mock_fetch_full_history):
        """测试获取并保存历史K线数据"""
        # 设置模拟交易所
        mock_exchange = mock.MagicMock()
        mock_exchange.symbols = ["BTC/USDT", "ETH/USDT"]
        mock_exchange.load_markets = mock.MagicMock()
        mock_okx.return_value = mock_exchange
        
        # 模拟fetch_full_history的返回值
        mock_fetch_full_history.return_value = self.mock_ohlcv_data
        
        # 模拟save_to_csv的返回值
        expected_file_path = os.path.join(self.temp_dir.name, "BTC-USDT_1h.csv")
        mock_save_to_csv.return_value = expected_file_path
        
        # 测试获取并保存数据
        symbol = "BTC/USDT"
        timeframe = "1h"
        start_date = "2021-07-01"
        end_date = "2021-07-02"
        exchange_id = "okx"
        config = self.test_config
        
        result = fetch_and_save_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            exchange_id=exchange_id,
            data_dir=self.temp_dir.name,
            config=config
        )
        
        # 验证结果
        assert result == expected_file_path
        mock_exchange.load_markets.assert_called_once()
        mock_fetch_full_history.assert_called_once_with(mock_exchange, symbol, timeframe, start_date, end_date)
        mock_save_to_csv.assert_called_once_with(self.mock_ohlcv_data, symbol, timeframe, self.temp_dir.name)
    
    @mock.patch('ccxt.okx')
    def test_fetch_and_save_data_symbol_not_found(self, mock_okx):
        """测试获取并保存数据时交易对不存在的情况"""
        # 设置模拟交易所
        mock_exchange = mock.MagicMock()
        mock_exchange.symbols = ["ETH/USDT"]  # 不包含BTC/USDT
        mock_exchange.load_markets = mock.MagicMock()
        mock_okx.return_value = mock_exchange
        
        # 测试获取并保存数据
        symbol = "BTC/USDT"
        
        # 验证是否抛出预期的异常
        with pytest.raises(ValueError) as excinfo:
            fetch_and_save_data(symbol=symbol)
        
        assert "交易对 BTC/USDT 在交易所" in str(excinfo.value)
        mock_exchange.load_markets.assert_called_once()


@pytest.fixture
def mock_config_manager():
    """创建模拟的配置管理器"""
    with mock.patch('src.manager.ConfigManager') as mock_cm:
        # 创建模拟的配置管理器实例
        mock_cm_instance = mock.MagicMock()
        mock_cm.return_value = mock_cm_instance
        
        # 设置read_config方法的返回值
        mock_cm_instance.read_config.return_value = {
            "exchange_id": "okx",
            "symbol": "BTC/USDT",
            "timeframe": "1h",
            "start_time": datetime.now().strftime("%Y-%m-%d 00:00:00"),
            "end_time": (datetime.now().replace(hour=23, minute=59, second=59)).strftime("%Y-%m-%d %H:%M:%S"),
            "output_dir": "output",
            "exchange_config": {
                "proxies": {
                    "http": "http://127.0.0.1:10808/",
                    "https": "http://127.0.0.1:10808/"
                },
                "options": {"defaultType": "swap"}
            }
        }
        
        yield mock_cm_instance


def test_config_integration(mock_config_manager):
    """测试配置集成"""
    # 重新导入模块，以使用模拟的配置管理器
    with mock.patch.dict('sys.modules'):
        import importlib
        importlib.reload(sys.modules['src.data.get_data'])
        from src.data.get_data import data_config
    
    # 验证配置是否正确加载
    assert 'exchange_id' in data_config
    assert 'symbol' in data_config
    assert 'timeframe' in data_config
    assert 'exchange_config' in data_config
    
    # 验证exchange_config是否包含预期的值
    assert 'proxies' in data_config['exchange_config']
    assert 'options' in data_config['exchange_config']
    assert data_config['exchange_config']['options']['defaultType'] == 'swap' 