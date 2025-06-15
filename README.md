# CHEESEBURGER

这是一个专注于加密货币市场交易的量化策略回测系统。

---

## 系统架构

### 目录结构

```
CHEESEBURGER/
├── config/               # 配置文件目录
│   └── data_config.json  # 数据获取配置
├── data/                 # 数据目录
├── docs/                 # 文档目录
├── logs/                 # 日志目录（运行时自动创建）
├── output/               # 输出目录（运行时自动创建）
├── scripts/              # 脚本目录
│   └── data_main.py      # 数据获取脚本
├── src/                  # 源代码目录
│   ├── __init__.py       
│   └── config.py         # 全局配置管理模块
└── tests/                # 测试目录
    ├── __init__.py
    └── test_data_main.py # 数据获取测试
```

### 全局配置模块

系统使用 `src/config.py` 作为全局配置管理模块，提供以下功能：

- 管理项目路径（运行根目录、配置目录、输出目录、数据目录等）
- 日志系统配置
- 配置文件读写
- 系统初始化
- 全局常量定义

## 环境设置

1. 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法

### 数据获取

数据获取通过配置文件控制参数，默认配置文件位于 `config/data_config.json`。

首次运行时，如果配置文件不存在，系统会自动创建示例配置文件。您可以根据需要修改配置文件中的参数：

```json
{
    "exchange_id": "okx",        // 交易所ID
    "symbol": "BTC/USDT",        // 交易对
    "timeframe": "1h",           // 时间周期（1m, 5m, 15m, 1h, 4h, 1d等）
    "start_time": "2023-01-01 00:00:00",  // 开始时间
    "end_time": "2023-01-07 00:00:00",    // 结束时间
    "output_dir": "output"       // 输出目录
}
```

运行数据获取脚本：

```bash
python scripts/data_main.py
```

脚本会根据配置文件获取数据，并保存到指定的输出目录。日志文件将保存在 `logs/` 目录下。

### 运行测试

本项目采用测试驱动开发(TDD)方法，使用pytest作为测试框架。运行测试：

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_data_main.py

# 生成测试覆盖率报告
pytest --cov=scripts --cov=src tests/
```

## 数据规范

数据格式遵循TOHLCV标准，包含以下字段：
- timestamp: 时间戳
- open: 开盘价
- high: 最高价
- low: 最低价
- close: 收盘价
- volume: 成交量

详细规范请参考 [数据规范文档](docs/data_regulation.md)。
