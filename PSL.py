from typing import Callable
import pandas as pd
import numpy as np


class psl:

    def __init__(self):
        pass

    def long(ohlc: pd.DataFrame, name_dict: dict = {}, singleData: Callable = lambda since, end: False):
        
        # 传入参数
        params = {
            'datetime': 'datetime',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'ps': '',
            'ls': '',
            'remain':''
        }
        for key in params.keys():
            if key in name_dict.keys():
                params[key] = name_dict[key]

        # 判断参数是否合法
        if np.any(ohlc[params['remain']] < 0):
            raise ValueError("df错误：最长时间列有负数")
        if len(ohlc) <= 4:
            raise ValueError("参数错误：传入的df长度不够")
        if not params['ps'] and not params['ls']:
            raise ValueError("参数不够：请传入止盈或止损，ps or ls")
        if not params['remain']:
            raise ValueError("参数不够：请传入持续时长，remain")
        if params['ps'] and params['ls'] and not singleData(ohlc[params['datetime']].tolist()[0], ohlc[params['datetime']].tolist()[1]):
            raise ValueError("参数不够：请输入数据获取函数")
        
        maximum_remain = np.max(ohlc[params['remain']])
        maximum = max(2, maximum_remain)

        # 计算止盈部分
        if params['ps']:
            
            # 进行必要的数据准备
            data = ohlc.copy()
            for i in range(1,maximum+1):
                data[f'high{i}'] = data[params['high']].shift(-i)
                data[f'close{i}'] = data[params['close']].shift(-i)
            highMatrix = data[[params['high']] + [f'high{i}' for i in range(1,maximum+1)]].values
            closeMatrix = data[[params['close']] + [f'close{i}' for i in range(1,maximum+1)]].values

            # 利用矩阵算法得出订单存活时长
            profit_stop_expanded = np.tile(data[params['ps']], (highMatrix.shape[1], 1)).T
            indices = np.argmax(highMatrix > profit_stop_expanded, axis=1)
            data['LpsNum'] = np.where(indices < highMatrix.shape[1], indices, highMatrix.shape[1])

            # 判断订单是止盈还是到期
            MaxClose1 = ((data['LpsNum'] == 0) & (data[params['ps']] > data[params['high']]))
            MaxClose2 = data['LpsNum'] > data[params['remain']]
            data.loc[MaxClose1 | MaxClose2, 'LpsNum'] = data[params['remain']]
            data['LIsPS'] = np.where(MaxClose1 | MaxClose2, False, True)

            # 计算平仓价格
            ps_close_price = np.choose(np.array(data['LpsNum']), closeMatrix.T)
            data['LCP'] = np.where(data['LIsPS'], data[params['ps']], ps_close_price)  #LCP: long close price

            ohlc['LpsNum'] = data['LpsNum']  # 多头仓位的持续时间
            ohlc['LIsPS'] = data['LIsPS']    # 多头是否止盈
            ohlc['psLCP'] = data['LCP']      # 多头平仓价格
            if not params['ls']:
                ohlc['Lcond'] = np.where(ohlc['LIsPS'], 'ps', 'expire')
                ohlc['LNum'] = ohlc['LpsNum']
                ohlc['LCP'] = ohlc['psLCP']
                return ohlc
            
        if params['ls']:

            # 进行必要的数据准备
            data = ohlc.copy()
            for i in range(1,maximum+1):
                data[f'low{i}'] = data[params['low']].shift(-i)
                data[f'close{i}'] = data[params['close']].shift(-i)
            lowMatrix = data[[params['low']] + [f'low{i}' for i in range(1,maximum+1)]].values
            closeMatrix = data[[params['close']] + [f'close{i}' for i in range(1,maximum+1)]].values

            # 利用矩阵算法得出订单存活时长
            loss_stop_expanded = np.tile(data[params['ls']], (lowMatrix.shape[1], 1)).T
            indices = np.argmax(lowMatrix < loss_stop_expanded, axis=1)
            data['LlsNum'] = np.where(indices < lowMatrix.shape[1], indices, lowMatrix.shape[1])

            # 判断订单是止损还是到期
            MaxClose1 = ((data['LlsNum'] == 0) & (data[params['ls']] < data[params['low']]))
            MaxClose2 = data['LlsNum'] > data[params['remain']]
            data.loc[MaxClose1 | MaxClose2, 'LlsNum'] = data[params['remain']]
            data['LIsLS'] = np.where(MaxClose1 | MaxClose2, False, True)

            # 计算平仓价格
            ls_close_price = np.choose(np.array(data['LlsNum']), closeMatrix.T)
            data['LCP'] = np.where(data['LIsLS'], data[params['ls']], ls_close_price)  #SCP: short close price

            ohlc['LlsNum'] = data['LlsNum']  # 多头仓位的持续时间
            ohlc['LIsLS'] = data['LIsLS']    # 多头是否止损
            ohlc['lsLCP'] = data['LCP']      # 多头平仓价格
            if not params['ps']:
                ohlc['Lcond'] = np.where(ohlc['LIsLS'], 'ls', 'expire')
                ohlc['LNum'] = ohlc['LlsNum']
                ohlc['LCP'] = ohlc['lsLCP']
                return ohlc
            
        if params['ps'] and params['ls']:

            # 计算多头平仓价格、平仓状态和平仓时间
            ohlc.loc[~ohlc['LIsPS'], 'Lcond'] = 'ls'
            ohlc.loc[~ohlc['LIsPS'], 'LNum'] = ohlc['LlsNum']
            ohlc.loc[~ohlc['LIsPS'], 'LCP'] = ohlc['lsLCP']

            ohlc.loc[~ohlc['LIsLS'], 'Lcond'] = 'ps'
            ohlc.loc[~ohlc['LIsLS'], 'LNum'] = ohlc['LpsNum']
            ohlc.loc[~ohlc['LIsLS'], 'LCP'] = ohlc['psLCP']

            ohlc.loc[ohlc['LIsLS'] & ohlc['LIsPS'] & (ohlc['LpsNum'] < ohlc['LlsNum']), 'Lcond'] = 'ps'
            ohlc.loc[ohlc['LIsLS'] & ohlc['LIsPS'] & (ohlc['LpsNum'] < ohlc['LlsNum']), 'LNum'] = ohlc['LpsNum']
            ohlc.loc[ohlc['LIsLS'] & ohlc['LIsPS'] & (ohlc['LpsNum'] < ohlc['LlsNum']), 'LCP'] = ohlc['psLCP']

            ohlc.loc[ohlc['LIsLS'] & ohlc['LIsPS'] & (ohlc['LpsNum'] > ohlc['LlsNum']), 'Lcond'] = 'ls'
            ohlc.loc[ohlc['LIsLS'] & ohlc['LIsPS'] & (ohlc['LpsNum'] > ohlc['LlsNum']), 'LNum'] = ohlc['LlsNum']
            ohlc.loc[ohlc['LIsLS'] & ohlc['LIsPS'] & (ohlc['LpsNum'] > ohlc['LlsNum']), 'LCP'] = ohlc['lsLCP']

            ohlc.loc[(~ohlc['LIsLS']) & (~ohlc['LIsPS']), 'Lcond'] = 'expire'
            
            # 通过再次获得时间粒度更小的数据，计算未知量
            excess_data = ohlc[ohlc['LIsLS'] & ohlc['LIsPS'] & (ohlc['LpsNum'] == ohlc['LlsNum'])].dropna(subset=[params['ls'],params['ps']])
            for index in excess_data.index:
                
                shift = excess_data.loc[index, 'LlsNum']
                since = ohlc.loc[index+shift, params['datetime']]
                end = ohlc.loc[index+shift+1, params['datetime']]
                try:
                    for _ in range(5):
                        high_column, low_column = singleData(since, end)
                        break
                except:
                    pass
                psIndex = np.where(high_column > excess_data.loc[index, params['ps']])[0][0]
                lsIndex = np.where(low_column < excess_data.loc[index, params['ls']])[0][0]
                if psIndex < lsIndex:
                    ohlc.loc[index, 'Lcond'] = 'ps'
                    ohlc.loc[index, 'LNum'] = ohlc.loc[index, 'LpsNum']
                    ohlc.loc[index, 'LCP'] = ohlc.loc[index, params['ps']]
                elif lsIndex < psIndex:
                    ohlc.loc[index, 'Lcond'] = 'ls'
                    ohlc.loc[index, 'LNum'] = ohlc.loc[index, 'LlsNum']
                    ohlc.loc[index, 'LCP'] = ohlc.loc[index, params['ls']]
                else:
                    ohlc.loc[index, 'Lcond'] = np.nan
                    ohlc.loc[index, 'LNum'] = np.nan
                    ohlc.loc[index, 'LCP'] = np.nan

        return ohlc
    

    def short(ohlc: pd.DataFrame, name_dict: dict = {}, singleData: Callable = lambda since, end: False):
        
        # 传入参数
        params = {
            'datetime': 'datetime',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'ps': '',
            'ls': '',
            'remain':''
        }
        for key in params.keys():
            if key in name_dict.keys():
                params[key] = name_dict[key]

        # 判断参数是否合法
        if np.any(ohlc[params['remain']] < 0):
            raise ValueError("df错误：最长时间列有负数")
        if len(ohlc) <= 4:
            raise ValueError("参数错误：传入的df长度不够")
        if not params['ps'] and not params['ls']:
            raise ValueError("参数不够：请传入止盈或止损，ps or ls")
        if not params['remain']:
            raise ValueError("参数不够：请传入持续时长，remain")
        if params['ps'] and params['ls'] and not singleData(ohlc[params['datetime']].tolist()[0], ohlc[params['datetime']].tolist()[1]):
            raise ValueError("参数不够：请输入数据获取函数")
        
        maximum_remain = np.max(ohlc[params['remain']])
        maximum = max(2, maximum_remain)
        
        # 计算止盈部分
        if params['ps']:

            # 进行必要的数据准备
            data = ohlc.copy()
            for i in range(1,maximum+1):
                data[f'low{i}'] = data[params['low']].shift(-i)
                data[f'close{i}'] = data[params['close']].shift(-i)
            lowMatrix = data[[params['low']] + [f'low{i}' for i in range(1,maximum+1)]].values
            closeMatrix = data[[params['close']] + [f'close{i}' for i in range(1,maximum+1)]].values

            # 利用矩阵算法得出订单存活时长
            loss_stop_expanded = np.tile(data[params['ps']], (lowMatrix.shape[1], 1)).T
            indices = np.argmax(lowMatrix < loss_stop_expanded, axis=1)
            data['SpsNum'] = np.where(indices < lowMatrix.shape[1], indices, lowMatrix.shape[1])

            # 判断订单是止损还是到期
            MaxClose1 = ((data['SpsNum'] == 0) & (data[params['ps']] < data[params['low']]))
            MaxClose2 = data['SpsNum'] > data[params['remain']]
            data.loc[MaxClose1 | MaxClose2, 'SpsNum'] = data[params['remain']]
            data['SIsPS'] = np.where(MaxClose1 | MaxClose2, False, True)

            # 计算平仓价格
            ps_close_price = np.choose(np.array(data['SpsNum']), closeMatrix.T)
            data['SCP'] = np.where(data['SIsPS'], data[params['ps']], ps_close_price)  #SCP: short close price

            ohlc['SpsNum'] = data['SpsNum']  # 多头仓位的持续时间
            ohlc['SIsPS'] = data['SIsPS']    # 多头是否止损
            ohlc['psSCP'] = data['SCP']      # 多头平仓价格
            if not params['ls']:
                ohlc['Scond'] = np.where(ohlc['SIsPS'], 'ps', 'expire')
                ohlc['SNum'] = ohlc['SpsNum']
                ohlc['SCP'] = ohlc['psSCP']
                return ohlc

        # 计算止损部分
        if params['ls']:
            
            # 进行必要的数据准备
            data = ohlc.copy()
            for i in range(1,maximum+1):
                data[f'high{i}'] = data[params['high']].shift(-i)
                data[f'close{i}'] = data[params['close']].shift(-i)
            highMatrix = data[[params['high']] + [f'high{i}' for i in range(1,maximum+1)]].values
            closeMatrix = data[[params['close']] + [f'close{i}' for i in range(1,maximum+1)]].values

            # 利用矩阵算法得出订单存活时长
            profit_stop_expanded = np.tile(data[params['ls']], (highMatrix.shape[1], 1)).T
            indices = np.argmax(highMatrix > profit_stop_expanded, axis=1)
            data['SlsNum'] = np.where(indices < highMatrix.shape[1], indices, highMatrix.shape[1])

            # 判断订单是止盈还是到期
            MaxClose1 = ((data['SlsNum'] == 0) & (data[params['ls']] > data[params['high']]))
            MaxClose2 = data['SlsNum'] > data[params['remain']]
            data.loc[MaxClose1 | MaxClose2, 'SlsNum'] = data[params['remain']]
            data['SIsLS'] = np.where(MaxClose1 | MaxClose2, False, True)

            # 计算平仓价格
            ls_close_price = np.choose(np.array(data['SlsNum']), closeMatrix.T)
            data['SCP'] = np.where(data['SIsLS'], data[params['ls']], ls_close_price)  #SCP: long close price

            ohlc['SlsNum'] = data['SlsNum']  # 多头仓位的持续时间
            ohlc['SIsLS'] = data['SIsLS']    # 多头是否止盈
            ohlc['lsSCP'] = data['SCP']      # 多头平仓价格
            if not params['ps']:
                ohlc['Scond'] = np.where(ohlc['SIsLS'], 'ls', 'expire')
                ohlc['SNum'] = ohlc['SlsNum']
                ohlc['SCP'] = ohlc['lsSCP']
                return ohlc
            
        if params['ps'] and params['ls']:

            # 计算多头平仓价格、平仓状态和平仓时间
            ohlc.loc[~ohlc['SIsPS'], 'Scond'] = 'ls'
            ohlc.loc[~ohlc['SIsPS'], 'SNum'] = ohlc['SlsNum']
            ohlc.loc[~ohlc['SIsPS'], 'SCP'] = ohlc['lsSCP']

            ohlc.loc[~ohlc['SIsLS'], 'Scond'] = 'ps'
            ohlc.loc[~ohlc['SIsLS'], 'SNum'] = ohlc['SpsNum']
            ohlc.loc[~ohlc['SIsLS'], 'SCP'] = ohlc['psSCP']

            ohlc.loc[ohlc['SIsLS'] & ohlc['SIsPS'] & (ohlc['SpsNum'] < ohlc['SlsNum']), 'Scond'] = 'ps'
            ohlc.loc[ohlc['SIsLS'] & ohlc['SIsPS'] & (ohlc['SpsNum'] < ohlc['SlsNum']), 'SNum'] = ohlc['SpsNum']
            ohlc.loc[ohlc['SIsLS'] & ohlc['SIsPS'] & (ohlc['SpsNum'] < ohlc['SlsNum']), 'SCP'] = ohlc['psSCP']

            ohlc.loc[ohlc['SIsLS'] & ohlc['SIsPS'] & (ohlc['SpsNum'] > ohlc['SlsNum']), 'Scond'] = 'ls'
            ohlc.loc[ohlc['SIsLS'] & ohlc['SIsPS'] & (ohlc['SpsNum'] > ohlc['SlsNum']), 'SNum'] = ohlc['SlsNum']
            ohlc.loc[ohlc['SIsLS'] & ohlc['SIsPS'] & (ohlc['SpsNum'] > ohlc['SlsNum']), 'SCP'] = ohlc['lsSCP']

            ohlc.loc[(~ohlc['SIsLS']) & (~ohlc['SIsPS']), 'Scond'] = 'expire'
            
            # 通过再次获得时间粒度更小的数据，计算未知量
            excess_data = ohlc[ohlc['SIsLS'] & ohlc['SIsPS'] & (ohlc['SpsNum'] == ohlc['SlsNum'])].dropna(subset=[params['ls'],params['ps']])
            for index in excess_data.index:

                shift = excess_data.loc[index, 'SlsNum']
                since = ohlc.loc[index+shift, params['datetime']]
                end = ohlc.loc[index+shift+1, params['datetime']]
                try:
                    for _ in range(5):
                        high_column, low_column = singleData(since, end)
                        break
                except:
                    pass
                lsIndex = np.where(high_column > excess_data.loc[index, params['ls']])[0][0]
                psIndex = np.where(low_column < excess_data.loc[index, params['ps']])[0][0]
                if psIndex < lsIndex:
                    ohlc.loc[index, 'Scond'] = 'ps'
                    ohlc.loc[index, 'SNum'] = ohlc.loc[index, 'SpsNum']
                    ohlc.loc[index, 'SCP'] = ohlc.loc[index, params['ps']]
                elif lsIndex < psIndex:
                    ohlc.loc[index, 'Scond'] = 'ls'
                    ohlc.loc[index, 'SNum'] = ohlc.loc[index, 'SlsNum']
                    ohlc.loc[index, 'SCP'] = ohlc.loc[index, params['ls']]
                else:
                    ohlc.loc[index, 'Scond'] = np.nan
                    ohlc.loc[index, 'SNum'] = np.nan
                    ohlc.loc[index, 'SCP'] = np.nan

        return ohlc