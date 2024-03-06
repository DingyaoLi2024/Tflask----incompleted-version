import pandas as pd
import numpy as np

import os
import sys
# 设置路径
script_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_directory)

class analysis:

    def __init__(self) -> None:
        pass

    def drawdown(ohlc:pd.DataFrame, datetime='datetime', netValue='net_value'):

        data = ohlc.copy()
        data['max2here'] = data[netValue].expanding().max()
        data['dd2here'] = data[netValue] / data['max2here']
        end_date, remains = tuple(data.sort_values(by=['dd2here'], inplace=False).iloc[0][[datetime, netValue]])
        data.set_index(datetime, inplace=True)
        data_sub = data[:end_date]
        start_date = data_sub[netValue].idxmax()
        max_retracement = f'{round(((data.loc[start_date, netValue] - remains) * 100 / data.loc[start_date, netValue]), 2)}%'

        return {
            "最大回撤": max_retracement,
            "最大回撤开始时间": start_date,
            "最大回撤结束时间": end_date
        }
    
    def sketch_netValue(ohlc:pd.DataFrame, title='策略净值走势', store_to='', datetime='datetime', netValue='net_value'):

        from pyecharts import options as opts
        from pyecharts.charts import Line

        data = ohlc.copy()
        data[datetime] = pd.to_datetime(data[datetime])
        net = (
            Line()
            .add_xaxis(xaxis_data=data['datetime'].tolist())
            .add_yaxis(
                series_name='策略净值', 
                y_axis=list(data[netValue].tolist()),
            ).set_global_opts(title_opts=opts.TitleOpts(title=title), datazoom_opts=[opts.DataZoomOpts(type_='slider', xaxis_index=[0])],)
        )
        net.render(store_to + title + '.html')

    def sketch_netValue_in_notebook(ohlc:pd.DataFrame, title='策略净值走势', datetime='datetime', netValue='net_value'):

        from pyecharts import options as opts
        from pyecharts.charts import Line

        data = ohlc.copy()
        data[datetime] = pd.to_datetime(data[datetime])
        net = (
            Line()
            .add_xaxis(xaxis_data=data['datetime'].tolist())
            .add_yaxis(
                series_name='策略净值', 
                y_axis=list(data[netValue].tolist()),
            ).set_global_opts(title_opts=opts.TitleOpts(title=title), datazoom_opts=[opts.DataZoomOpts(type_='slider', xaxis_index=[0])],)
        )
        net.render_notebook()

    def IC(factors:np.ndarray, returns:np.ndarray, T:int):
        import IC
        return IC.IC(factors.astype(np.float64).tolist(), returns.astype(np.float64).tolist(), T)

    def TotalAnalysis(ohlc:pd.DataFrame, strategy_name='我的策略', name_dict:dict={}, isPrint=True):

        '''
        name_dict需传入的参数如下：
                datetime： str，有默认值datetime
                symbols：list[str]，有默认值[]（单个净值对应的列名）
                conditions：list[str]，有默认值[]（单个持仓状态对应的列名），condtions和symbols中的元素请一一对应，按照相同的顺序排列
                total：str，有默认值total（整体净值对应的列名）
                base：基准收益率，float，默认值0
        '''

        import WinRate

        # 填充name_dict
        if 'datetime' not in name_dict:
            name_dict['datetime'] = 'datetime'
        if 'total' not in name_dict:
            name_dict['total'] = 'total'
        if 'conditions' not in name_dict:
            name_dict['conditions'] = []
        if 'symbols' not in name_dict:
            name_dict['symbols'] = []
        if 'primary' not in name_dict:
            name_dict['primary'] = []
        if 'base' not in name_dict:
            name_dict['base'] = 0

        # 错误
        if len(name_dict['conditions'])!=len(name_dict['symbols']) or len(name_dict['conditions'])!=len(name_dict['total']) or len(name_dict['conditions'])==0:
            raise ValueError("输入参数名不一致")
        for ele in name_dict['primary']:
            if ele not in name_dict['symbols']:
                raise ValueError("输入参数名不一致")
        if not len(ohlc):
            raise ValueError("输入空DataFrame")

        # 记录初始时间和结束时间
        initial_time = ohlc[name_dict['datetime']].tolist()[0]
        end_time = ohlc[name_dict['datetime']].tolist()[-1]
        import ccxt
        binance_exchange = ccxt.binance()
        initial_stamp = binance_exchange(initial_time)
        end_stamp = binance_exchange(end_time)
        interval = (end_stamp - initial_stamp) / (365*3600*24*1000)
        if interval <= 0:
            raise ValueError("时间传入错误，初始时间大于结束时间")
        
        # 获取需要的数据碎片
        condition_df = ohlc[name_dict['conditions']]
        condition_df_copy = condition_df.copy()
        condition_df_copy.replace(-1, 1, inplace=True)
        condition_df_copy['postion_amount'] = condition_df_copy.sum(axis=1)

        # 根据total净值计算整体指标
        net_value = ohlc[name_dict['total']].values
        rates = np.diff(net_value) / net_value[:-1]

        total_profit = round(net_value[-1] / net_value[0] - 1, 4)
        CAGR = round((net_value[-1] / net_value[0]) ** (1 / interval), 4)
        Sortino = round((np.mean(rates) - name_dict['base']) / (np.std(rates[rates<name_dict['base']])), 2)
        Sharp = round((np.mean(rates) - name_dict['base']) / (np.std(rates)), 2)
        drawdown_info = analysis.drawdown(ohlc, datetime=name_dict['datetime'], netValue=name_dict['total'])
        Calmar = round(CAGR * 100 / float(drawdown_info["最大回撤"][:-1]), 2)

        Best_day = round(np.max(rates), 4)
        worst_day = round(np.min(rates, 4))
        Days_data = (np.sum(rates>0.01), np.sum((rates<=0.01) & (rates>0)), np.sum(rates<=0))

        creatings_times = 0
        profits_times = 0
        for symbol_num in range(len(name_dict['conditions'])):
            conds = ohlc[name_dict['conditions'][symbol_num]].astype(np.int64).tolist()
            nets = ohlc[name_dict['symbols'][symbol_num]].astype(np.float64).tolist()
            win_rate_info = WinRate.static_of_position(conds, nets)
            creatings_times += win_rate_info["position_creating_times"]
            profits_times += win_rate_info["position_profit_times"]
        win_rate = round(profits_times / creatings_times, 4)

        min_balance = np.min(net_value)
        max_balance = np.max(net_value)
        account_underwater = np.sum(net_value<net_value[0]) / len(net_value)
        max_drawdown = drawdown_info["最大回撤"]
        drawdown_start = drawdown_info["最大回撤开始时间"]
        drawdown_end = drawdown_info["最大回撤结束时间"]

        total_indicators = {
            '整体利润率':               f'{total_profit*100}%',
            '复合年增长率':             f'{CAGR*100}%',
            'Sortino':                Sortino,
            '夏普比率':                 Sharp,
            'Calmar':                 Calmar,
            '单位时间最大利润率':        f'{Best_day*100}%',
            '单位时间最大损失率':        f'{worst_day*100}%',
            '天数：盈利/保持/亏损':      Days_data,
            '胜率':                    f'{win_rate*100}%',
            '账户最低净值':             round(min_balance, 2),
            '账户最高净值':             round(max_balance, 2),
            '低于初始净值的时间占比':     f'{round(account_underwater, 4)*100}%',
            '最大回撤':                 max_drawdown,
            '最大回撤开始时间':          drawdown_start,
            '最大回撤结束时间':          drawdown_end,
        }

        strategy_info = {
            'title':['Strategy Name', 'Entries', 'Profit', 'Max Drawdown', 'Win Rate'],
            'value':[strategy_name, len(name_dict['conditions']), total_indicators['整体利润率'], total_indicators['最大回撤'], total_indicators['胜率']]
        }
        primary = []
        if name_dict['primary']:
            primary = [['资产名', '利润率', '最大回撤', '夏普比率', '开仓次数', '盈利次数']]
            for symbol in name_dict['primary']:
                rates = (ohlc[symbol] / ohlc[symbol].shift() - 1).values
                rates[0] = 0.0
                rate = ohlc[symbol].tolist()[-1] / ohlc[symbol].tolist()[0] - 1
                drawdown = analysis.drawdown(ohlc, name_dict['datetime'], symbol)
                sharp_ratio = (rate - name_dict['base']) / np.std(rates)
                p_nets = ohlc[symbol].astype(np.float64).tolist()
                p_conds = ohlc[name_dict['conditions'][name_dict['symbols'].index(symbol)]].astype(np.float64).tolist()
                position_info = WinRate.static_of_position(p_conds, p_nets)
                primary += [symbol, rate, drawdown, sharp_ratio, position_info['position_creating_times'], position_info['position_profit_times']]

        result = {'策略速看':strategy_info, '整体指标':total_indicators, '主流资产':primary}


        if isPrint:
            from prettytable import PrettyTable

            # total
            table1 = PrettyTable(['指标', '值'])
            for indicator, value in total_indicators.items():
                table1.add_row([indicator, value])
            
            # strategy info
            table2 = PrettyTable(strategy_info['title'])
            table2.add_row(strategy_info['value'])

            # primary
            if name_dict['primary']:
                table3 = PrettyTable(primary[0])
                for data in enumerate(primary[1:]):
                    table3.add_row(data)
            
            print(table1)
            print(table2)
            print(table3)

        return result
