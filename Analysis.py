import pandas as pd
import numpy as np

class analysis:

    def __init__(self) -> None:
        pass

    def retrace(ohlc:pd.DataFrame, datetime='datetime', netValue='net_value'):

        data = ohlc.copy()
        data['max2here'] = data[netValue].expanding().max()
        data['dd2here'] = data[netValue] / data['max2here']
        end_date, remains = tuple(data.sort_values(by=['dd2here'], inplace=False).iloc[0][[datetime, netValue]])
        data.set_index(datetime, inplace=True)
        data_sub = data[:end_date]
        start_date = data_sub[netValue].idxmax()
        max_retracement = f'{round(((1 - remains) * 100), 2)}%'

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