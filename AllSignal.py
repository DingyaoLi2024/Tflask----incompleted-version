import numpy as np
import pandas as pd
import os
import sys

# 设置路径
script_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_directory)
import netValue

class Signal:

    def __init__(self) -> None:
        pass

    def normalSignals(ohlc, name_dict:dict={}, current:bool=True):
        
        # 初始化
        nameDict = {
            'signal':'signal',
            'open':'open',
            'close':'close',
        }
        if name_dict:
            for key in name_dict:
                nameDict[key] = name_dict[key]

        data = ohlc.copy()
        if current:
            data['fsSignal'] = data[nameDict['signal']]
        else:
            data['fsSignal'] = data[nameDict['signal']].shift(-1)
        data['fsSignal'].fillna(method='ffill', inplace=True)
        data['fsSignal'].fillna(0, inplace=True)
        data['return'] = np.where(
            pd.isna(data['signal']), 
            data[nameDict['close']] / data[nameDict['open']] - 1, 
            data[nameDict['close']] / data[nameDict['close']].shift() - 1
        )

        return data
    
    def pslSignals(ohlc, name_dict:dict={}):
        
        # 初始化
        nameDict = {
            'signal':'signal',
            'LNum':'LNum',
            'Lcond':'Lcond',
            'open':'open',
            'close':'close',
            'stop':'LCP'
        }
        if name_dict:
            for key in name_dict:
                nameDict[key] = name_dict[key]

        # 构造C++中的输入
        df = ohlc.copy()
        df.loc[df[nameDict['stop']].isna(), nameDict['stop']] = df['open']
        signals = df[nameDict['signal']].fillna(0).astype(np.int64).tolist()
        LNums = df[nameDict['LNum']].fillna(0).astype(np.int64).tolist()
        opens = df[nameDict['open']].fillna(method='ffill').fillna(method='bfill').astype(np.float64).tolist()
        closes = df[nameDict['close']].fillna(method='ffill').fillna(method='bfill').astype(np.float64).tolist()
        stops = df[nameDict['stop']].fillna(method='ffill').fillna(method='bfill').astype(np.float64).tolist()

        # 调用C++函数
        result = netValue.pslSignal(signals, LNums, opens, closes, stops)

        # 提取返回的结果
        data = ohlc.copy()
        data['fsSignal'] = np.array(result['allSignal'])
        data['fsSignal'] = data['fsSignal'].astype(np.int64)
        data['fsReturn'] = np.array(result['return'])
        data['fsOpCond'] = np.array(result['opCond'])

        return data
