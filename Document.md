# Tflask
## Tflask简介

Tflask是一款专为金融交易（主要针对数字货币）而设计的功能强大的Python库，旨在提供全面的回测和实盘支持。其主要功能包括但不限于：

- **数据获取与处理**：Tflask提供了与币安API的集成，使用户能够方便地获取现货和永续合约等多种金融产品的历史和实时数据。这些数据可以通过Tflask内置的数据处理功能进行预处理和清洗，以满足用户的需求。

- **交易信号生成**：基于用户定义的交易策略和因子，Tflask能够生成买卖信号，用于指导交易决策。用户可以根据自己的需求和市场情况定义各种复杂的交易规则和信号算法。

- **K线图绘制**：Tflask支持绘制K线图，并能够在图表上标注多空头的开仓和平仓信号，以帮助用户直观地分析交易行为和结果。

- **风险管理**：Tflask提供了灵活的风险管理功能，包括设定止盈止损价格、控制最大持仓时长等，帮助用户合理控制风险，最大限度地保护资金。

- **机器学习支持**：对于使用机器学习建立交易策略的用户，Tflask提供了滚动训练的方法，使用户能够动态地根据市场变化不断调整和优化模型，提高交易效果。

- **策略模板**：Tflask提供了一套投机策略的父类模板，方便用户根据自己的需求和偏好快速构建自己的交易策略，并且支持用户自定义扩展。

在使用Tflask之前，用户需要准备好相关的数据、因子计算方法和信号生成算法。其中，数据应以DataFrame的格式传入，而其他参数则以字典的形式传入。通过Tflask提供的丰富功能和灵活性，用户能够更加方便地进行金融交易的回测和实盘操作，并且更好地理解和掌握市场走势。


## Tflask安装
你可以通过 pip 安装 Tflask：

```bash
pip install Tflask
```
## 导入库
几乎库的所有方法集都以如下形式导入
```python
from Tflask.PSL import psl
from Tflask.Roll import roll
from Tflask.Kline import kline_with_signal as ks
```
## Tflask.GetData
getData分为两个部分，每个部分都有两个函数：**get_hist_data** 和 **get_high_and_low** 。


- getF.get_hist_data
- getS.get_hist_data

**传入参数**
| 参数名 | params | 格式| 备注|
| --- | --- | ---| ---|
| 交易对 | symbol| 字符串 |
| 时间粒度 | interval | 字符串 |1m, 15m, 30m, 1h, 2h, 4h, 1d|
| 开始时间 | start_time | 字符串 |UTC时间，格式如："2024-03-15T00:00:00.000Z"|
| 结束时间 | end_time | 字符串 |UTC时间，格式如："2024-03-15T00:00:00.000Z"|

**返回参数**
返回值为一个包含时间、开高低收、成交量等数据的DataFrame（列名的英文很好的解释了数据）

**代码示例**
```python
from Tflask.GetData import getS as gs
df = gs.get_hist_data(symbol='BTCUSDT', interval='1d', start_time="2024-01-01T00:00:00.000Z", end_time="2024-02-01T00:00:00.000Z")
print(df.head())
```
get_high_and_low具有同样的输入参数，但返回的是最高价和最低价的两个ndarray。

## Tflask.PSL
PSL主要是针对已经给出最大持仓时长、止盈价格和止损价格的订单作出分析，判断每一笔仓位订单会在何时结束，结束状态是止盈止损还是到期等。

PSL有两个函数：long和short，分别表示在多头和空头时的判断，由于其具有同样的参数传入和返回值，因此只介绍long。


**传入参数**
|    参数名   | params    |     参数类型   |  二级参数 | params2 | 默认值 |参数类型 | 参数说明 | 是否必须 |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| pandas数据  |    ohlc   |  DataFrame   |          |         |            | 是 |
| 数据列名字典 | name_dict |     字典      |          |         | ||字典中的数据均为字符串，代表ohlc中的列名，具体数据请存放与ohlc中 | 是 |
|            |           |               |   开仓价  | open| open | 字符串 |     |否|
|            |           |               |   最高价  | high| high |  字符串 |     |否|
|            |           |               |   最低价  | low| low |  字符串 |     |否|
|            |           |               |   平仓价  | close| clsoe |  字符串 |     |否|
|            |           |               |   止盈价  | ps | |  字符串 |     |否|
|            |           |               |   止损价  | ls | |  字符串 |     |否，但ps与ls至少传入一个|
|            |           |               |最高持续时长| remain | | 字符串 | 0代表该时间段内购买，在该时段收盘前必须卖出；1代表在该时间段内购买，下一时间段的首盘前必须卖出；以此类推  | 是 |


返回值为一个DataFrame，除了包含输入ohlc的列，还增添了新的列。
**注：** long会返回L开头或包含L的列名，而short会返回S开头或包含S的列名

**返回参数**
| 列名 | 参数说明 | 参数类型 |备注 |
|-----|-----|-----|-----|
| LpsNum |  多头止盈平仓时间  | int | 与传入参数中的remain类似，0代表该时间段平仓，1代表下个时间段平仓，以此类推，后面的Num类似 （如果ps未传入参数则不返回该参数）  |
| LIsPS |   多头仓位是否止盈  |   bool  |（如果ps未传入参数则不返回该参数）  |
| psLCP |   多头止盈仓位平仓价格  |  float   |如果止盈，则平仓价为止盈价格，如果不止盈，则平仓价为到期收盘价 （如果ps未传入参数则不返回该参数）  |
| LlsNum |   多头止损平仓时间  |  int   |（如果ls未传入参数则不返回该参数）  |
| LIsLS |  多头仓位是否止损   |  bool   |（如果ls未传入参数则不返回该参数）  |
| lsLCP |   多头止损仓位平仓价格  | float    |（如果ls未传入参数则不返回该参数）  |
| Lcond |   多头仓位平仓状态  |  字符串   | 'ps'代表止盈，'ls'代表止损， 'expire'代表到期平仓 |
| LNum |   多头仓位平仓时间  |  int   |
| LCP |   多头仓位平仓价格  |   float  |

**代码示例**
```python
from Tflask.PSL import psl
name_dict = {
    'datetime': '时间',
    'open': '开盘价',
    'high': '最高价',
    'low': '最低价',
    'close': '收盘价',
    'ps': '止盈价',
    'ls': '止损价',
    'remain':'持续时长'
}
psl.long(ohlc = df, name_dict = name_dict)
```

## Tflask.Roll

Roll是针对滚动训练设置的函数，传入参数时，除了基本的DataFrame、因子列名、标签列名，还需要传入一个参数函数（参数函数的传入参数：X_train, y_train, X_test;参数函数的返回参数：y_predict）。当然，如果你的需求并不复杂，你需要使用的机器学习算法只是KNN、支持向量机、决策树或者逻辑回归中的一种，你是不需要传入参数函数的（注意：这些情况下需要你已经安装了sklearn库）。

库中有以下函数
- KNN
- SVM
- LogisticRegression
- Tree
- DIYalgorithm

对于DIYalgorithm，我们需要多传入一个参数函数。而其他函数的参数与之完全相同，因此，我们只介绍DIYalgorithm的情况。

**传入参数**
| 参数名 | params | 参数类型 | 默认值 | 参数说明 |
| --- | --- | --- | --- | --- |
| 表格 |  df   |  pd.DataFrame   |     |     |
| 因子名 |  factors   |  list   |     |     |
| 标签名 |  labels   |  list   |     |     |
| 学习算法 |  algorithm   |   Callable  |     |  该函数需传入三个ndarray：训练集数据，训练集标签，测试集数据，返回一个ndarray，为预测数据   |
| 进度条名称 |  bar   |  str   |  '我的算法'   |  该进度条的名称，如果你的测试数据是多个，最好传入该参数，并在每个参数前进行编号，如：f'{num}--{name}'   |
| 未到期数据行 |  expire   |  int   |  5   |  在滚动训练时，可能每一次训练都要舍弃数据的最后几行，以避免未来函数   |
| 滚动训练回望 |  roll_length  |  int  |  2000   |  每次滚动训练需要的过去数据行数   |

**代码示例**
```python
from Tflask.Roll import roll
data = pd.read_csv('....')
roll.KNN(data, ['RSI','Sigma','SM1'], ['isProfit'], 'KNN')
```

## Tflask.AllSignal

这是一个根据初始信号计算最终持仓状态的函数
在这里，因为normal signal较为简单，因此只介绍pslSignal。

**传入参数**
传入参数为ohlc：DataFrame和name_dict：ohlc中的列名（str），其中每列的参数如下表
| 参数名             | params | 默认值 | 列类型 | 列内容说明 |
|-------|-------|-------|-------|-------|
|原始信号            | signal | signal | int         | 0表示空仓，1表示多头，-1表示空头   |
|开仓时长            | LNum   | LNum   | usigned int | 0表示在df一行时间内开仓并平仓， 1表示在df当行时间开仓，下一行平仓；以此类推   |
|开仓价格            | open   | open   | float       |    |
|收盘价           | close  | close  | float       |    |
|跟随开仓时间的平仓价铬 | stop   | stop  | float       |  原始信号不为1时该数值有效  |

**注：**传入DataFrame中，以上表格中所有列均不可以有空值

**返回参数**

- allSignal：每日的持仓状态，1.0多头持仓，-1.0空头持仓，0.0空仓
- return：每日收益率
- op：仓位情况，0.001开仓，0.111持续持仓，0空仓，0.101平仓，0.011当日开仓当日平仓


**代码示例**
```python
from Tflask.AllSignal import Signal

# 传统信号
data = pd.read_csv('....')
Signal.normalSignals(data, {'signal':'我的信号', 'open':'开仓价', 'close':'平仓价'})

# 带止盈止损的信号
name_dict = {
            'signal':'原始信号',
            'LNum':'持续时长',
            'open':'开仓价',
            'close':'收盘价',
            'stop':'当日开仓的平仓价'
        }
Signal.pslSignals(data, name_dict)
```

## Tflask.Kline
kline的绘制分为传入参数和绘制两步：
**代码示例**
```python
from Tflask.Kline import kline_with_signal as ks
data = pd.read_csv('...')
name_dict = {
    'datetime':'时间',
    'open':'开盘价',
    'high':'最高价',
    'low':'最低价',
    'close':'收盘价',
    'long_price':'多头开仓价',
    'close_long_price':'多头平仓价',
    'short_price':'空头开仓价',
    'close_short_price':'空头平仓价'
}
Sketcher = ks(name='ETH', strategy='RSI', store_to = './')
Sketcher.generate(ohlc=data, name_dict=name_dict)
```


## Tflask.Analysis


- 计算最大回撤
    函数名：**drawdown**

    |传入参数 | 参数类型 | 参数注释 |
    |-----|-----|-----|
    |ohlc | dataframe |原始数据 |
    |datetime | str |时间列的列名 |
    |netValue | str | 净值列的列名 |

    返回参数：字典
    ```Json
    {
        "最大回撤": "15%",
        "最大回撤开始时间": "2023-01-01",
        "最大回撤结束时间": "2023-03-02"
    }
    ```
**代码示例**
```python
from Tflask.Analysis import analysis as ans
data = pd.read_csv('...')
ans.drawdown(data, 'datetime', 'net_value')
```


- 绘制净值走势图（可生成文件或在notebook中直接绘制）
    函数名：**sketch_netValue**和**sketch_netValue_in_notebook**

    |传入参数 | 参数类型 | 参数注释 |
    |-----|-----|-----|
    |ohlc | dataframe |原始数据 |
    |title | str |时间列的列名 |
    |netValue | str | 净值列的列名 |

**代码示例**
```python
from Tflask.Analysis import analysis as ans
data = pd.read_csv('...')
ans.sketch_netValue(ohlc=data, title='策略净值走势', store_to='D:/MyFile/', datetime='datetime', netValue='net_value')
# jupyter notebook 中的写法
ans.sketch_netValue_in_notebook(ohlc=data, title='策略净值走势', datetime='datetime', netValue='net_value')
```

- 计算因子的IC值
    函数名：**IC**
    |传入参数 | 参数类型 | 参数注释 |
    |-----|-----|-----|
    |factors | ndarray | 因子值 |
    |returns | ndarray | 收益率 |

**代码示例**
```python
from Tflask.Analysis import analysis as ans
factors = np.array(data_factor)
returns = np.array(data_return)
ICs = ans.IC(factors, returns, 10)
'ICs为一个ndarray，内部存储着每个时刻的IC值'
```
- 根据多个资产的持仓状态和净值变化，计算策略的整体评价指标并打印

    函数名：**TotalAnalysis**
    |传入参数 | 参数类型 | 默认值 |参数注释 | 二级参数 | 参数类型 | 参数说明 |
    |-----|-----|-----|---|---|---|---|
    |ohlc | dataframe |  | 原始数据 |
    |strategy_name | str | 我的策略 | 策略名称 |
    |name_dict| dict || 列名 |
    ||||| datetime |str||
    ||||| total |str||
    ||||| conditions |list[str]| 所有资产状态的列名称 |
    ||||| symbols |list[str]| 所有资产的列名称（需要与资产状态的顺序一致） |
    ||||| primary |list[str]| 主要资产的列名称 |
    ||||| base |int| 基准收益率，默认为0 |

**代码示例**
```python
from Tflask.Analysis import analysis as ans
data = pd.read_csv('...')
symbols = ['BTC', 'ETH', .....]
name_dict = {
    'datetime':'datetime',
    'total':'total_value',
    'conditions':[f'{symbol}_cond' for symbol in symbols],
    'symbols':[f'{symbol}_value' for symbol in symbols],
    'primary':[f'{symbol}_cond' for symbol in symbols[100:]]
}
result_data = ans.TotalAnalysis(ohlc=data, strategy_name='我的策略', name_dict=name_dict, isPrint=True)
```
