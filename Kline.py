from pyecharts import options as opts
from pyecharts.charts import Kline, Scatter, Line

#判断技术指标线条的位置

class kline_with_signal:

    def __init__(self, name='K线图--开平仓信号', strategy='我的策略', store_to='./'):
        self.__name = name
        self.__strategy = strategy
        if store_to[-1] != '/' and store_to[-1] != '\\':
            store_to += '/'
        self.__store_to = store_to

    def dict_data(self, data, name_dict):

        # 判断参数合法性
        cond1 = 'long_price' in name_dict
        cond2 = 'close_long_price' in name_dict
        cond3 = 'short_price' in name_dict
        cond4 = 'close_short_price' in name_dict
        
        if 'datetime' not in name_dict:
            raise ValueError("传入参数不够：缺少时间轴")
        datas_list = ['datetime', 'open', 'high', 'low', 'close']
        if not all(name in name_dict for name in datas_list):
            raise ValueError(f"传入参数不够：请确认{datas_list}中的所有参数均传入")
        if (cond1 and not cond2) or (cond3 and not cond4):
            raise ValueError("传入参数不匹配：传入开仓但没有传入平仓")
        if (not cond1 and cond2) or (not cond3 and cond4):
            raise ValueError("传入参数不匹配：传入平仓但没有传入开仓")
        
        for name in name_dict.keys():
            if name_dict[name] not in data.columns:
                raise ValueError("传入参数不匹配：请检查data中的列名与name_dict中的值是否一一对应")

        # 初始化参数
        df = data.copy()
        dict_data = {}
        
        # 将所有参数以列表的形式传入字典
        datas = df[[name_dict['open'], name_dict['close'], name_dict['low'], name_dict['high']]].values.tolist()
        times = df[name_dict['datetime']].tolist()
        dict_data['datas'] = datas
        dict_data['times'] = times
        if cond1:
            dict_data['long_price'] = df[name_dict['long_price']].tolist()
            dict_data['close_long_price'] = df[name_dict['close_long_price']].tolist()
        if cond3:
            dict_data['short_price'] = df[name_dict['short_price']].tolist()
            dict_data['close_short_price'] = df[name_dict['close_short_price']].tolist()
        
        return dict_data
    
    def chart_generate(self, dict_data, bullin=False, MA=False, EMA=False):
        #绘制K线图
        kline = (
            Kline()
            .add_xaxis(xaxis_data=dict_data['times'])
            .add_yaxis(
                series_name='', 
                y_axis=dict_data['datas'],
                itemstyle_opts=opts.ItemStyleOpts(
                    color='#00da3c',
                    color0='#ec0000',
                    border_color='#00da3c',
                    border_color0='#ec0000',
                ),
            )
        )

        #绘制买卖点
        if 'long_price' not in dict_data and 'short_price' not in dict_data:
            overlap_kline_and_signal = kline
            
        else:
            scatter = Scatter()
            scatter.add_xaxis(xaxis_data=dict_data['times'])

            if 'long_price' in dict_data:
                scatter.add_yaxis(
                    series_name='多头开仓',
                    y_axis=dict_data['long_price'],
                    label_opts=opts.LabelOpts(is_show=False),
                    itemstyle_opts=opts.ItemStyleOpts(color='blue', opacity=0.8),  # 设置颜色为蓝色
                    symbol='arrow',  # 设置为箭头
                    symbol_size=10
                )
                scatter.add_yaxis(
                    series_name='多头平仓',
                    y_axis=dict_data['close_long_price'],
                    label_opts=opts.LabelOpts(is_show=False),
                    itemstyle_opts=opts.ItemStyleOpts(color='blue', opacity=0.8),  # 设置颜色为蓝色
                    symbol='circle',  # 设置为圆圈
                    symbol_size=10
                )

            if 'short_price' in dict_data:
                scatter.add_yaxis(
                    series_name='空头开仓',
                    y_axis=dict_data['short_price'],
                    label_opts=opts.LabelOpts(is_show=False),
                    itemstyle_opts=opts.ItemStyleOpts(color='yellow', opacity=0.8),  # 设置颜色为黄色
                    symbol='arrow',  # 设置为箭头
                    symbol_size=10
                )
                scatter.add_yaxis(
                    series_name='空头平仓',
                    y_axis=dict_data['close_short_price'],
                    label_opts=opts.LabelOpts(is_show=False),
                    itemstyle_opts=opts.ItemStyleOpts(color='yellow', opacity=0.8),  # 设置颜色为黄色
                    symbol='circle',  # 设置为圆圈
                    symbol_size=10
                )
            
            #将k线图和买卖点联合
            overlap_kline_and_signal = kline.overlap(scatter)

        if bullin or MA or EMA:
            
            import numpy as np
            close = np.array(dict_data['datas'])[:, 1]
            line = Line()
            line.add_xaxis(xaxis_data=dict_data['times'])

            if bullin:
                middle = np.convolve(close, np.ones(20)/20, mode='valid')

                # 计算标准差
                std_dev = np.std(close)
                upper = middle + 2 * std_dev
                lower = middle - 2 * std_dev
                line.add_yaxis(
                    series_name='布林线高',
                    y_axis=upper.tolist(),
                    label_opts=opts.LabelOpts(is_show=False),
                    itemstyle_opts=opts.ItemStyleOpts(color='lightblue')
                )
                line.add_yaxis(
                    series_name='布林线中',
                    y_axis=middle.tolist(),
                    label_opts=opts.LabelOpts(is_show=False),
                    itemstyle_opts=opts.ItemStyleOpts(color='pink')
                )
                line.add_yaxis(
                    series_name='布林线低',
                    y_axis=lower.tolist(),
                    label_opts=opts.LabelOpts(is_show=False),
                    itemstyle_opts=opts.ItemStyleOpts(color='lightblue')
                )
                overlap_kline_and_signal = overlap_kline_and_signal.overlap(line)
                
            
        
        overlap_kline_and_signal.set_global_opts(
            xaxis_opts=opts.AxisOpts(is_scale=True),
            yaxis_opts=opts.AxisOpts(is_scale=True),
            title_opts=opts.TitleOpts(title=f'{self.__name}{self.__strategy}下的买卖点图线'),
            datazoom_opts=[opts.DataZoomOpts(type_='inside', xaxis_index=[0])],
            toolbox_opts=opts.ToolboxOpts(),
        )

        self.total_chart = overlap_kline_and_signal

    def generate(self, ohlc, name_dict, bullin=False, MA=False, EMA=False):
        data_dict = kline_with_signal.dict_data(
            self, 
            data=ohlc, 
            name_dict=name_dict
        )
        kline_with_signal.chart_generate(self, data_dict, bullin, MA, EMA)
        self.total_chart.render(self.__store_to + f'{self.__name}-{self.__strategy}.html')