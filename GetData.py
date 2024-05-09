import ccxt
import pandas as pd
import numpy as np
import requests
import sys
import threading

class getS:

    def __init__(self) -> None:
        pass
    
    def get_hist_data(symbol:str, interval:str, start_time:str, end_time:str):
        
        # 初始化请求url和时间粒度的毫秒数
        binance_exchange = ccxt.binance()  #初始化交易所-binance
        baseurl = 'https://api.binance.com'  #初始化baseurl
        kline_path = '/api/v3/klines' #获取k线数据
        interval_dict = {
            '1m':60000, 
            '15m':900000, 
            '30m':1800000, 
            '1h':3600000, 
            '2h':7200000, 
            '4h':14400000, 
            '1d':86400000
        }
        
        # 给定请求数据
        start_stamp = binance_exchange.parse8601(start_time)
        end_stamp = binance_exchange.parse8601(end_time)
        query_dict = {
            'symbol':symbol,
            'interval':interval,
            'limit':500,
            'startTime':start_stamp
        }

        # 发送请求获取数据
        data_list = []
        while start_stamp < end_stamp:

            query_dict = {
            'symbol':symbol,
            'interval':interval,
            'limit':500,
            'startTime':start_stamp
            }
            for _ in range(5):
                try:
                    response = requests.get(url=baseurl+kline_path, params=query_dict)
                    break
                except:
                    if _ < 4:
                        continue
                    else:
                        print('响应失败')
                        sys.exit()
            single_kline = response.json()
            if single_kline[0][0] == start_stamp:
                if single_kline[-1][0] > end_stamp:
                    numbers_of_delete_row = int((single_kline[-1][0] - end_stamp)/(interval_dict[interval]))
                    single_kline = single_kline[:-numbers_of_delete_row]
                data_list += single_kline
            start_stamp += interval_dict[interval] * 500
        
        # 将获取的数据存入dataframe中
        data = pd.DataFrame(data_list, columns=[
            'datetime',
            'open',
            'high',
            'low',
            'close',
            'vol',
            'closeTime',
            'volAmount',
            'transaction',
            'activeBuyVol',
            'activeBuyTransaction',
            'delete'
        ])
        data.drop(columns=['delete'], inplace=True)
        data['datetime'] = data['datetime'].apply(binance_exchange.iso8601)
        data['closeTime'] = data['closeTime'].apply(binance_exchange.iso8601)
        return data

    def get_high_and_low(symbol:str, interval:str, start_time:str, end_time:str):
        hist_data = getS.get_hist_data(symbol, interval, start_time, end_time)
        high_column = np.array(hist_data['high'])
        low_column = np.array(hist_data['low'])
        return high_column.astype(np.float64), low_column.astype(np.float64)




class getF:

    def __init__(self) -> None:
        pass
    
    def get_hist_data(symbol:str, interval:str, start_time:str, end_time:str):
        
        # 初始化请求url和时间粒度的毫秒数
        binance_exchange = ccxt.binance()  #初始化交易所-binance
        baseurl = 'https://fapi.binance.com'  #初始化baseurl
        kline_path = '/fapi/v1/klines' #获取k线数据
        interval_dict = {
            '1m':60000, 
            '15m':900000, 
            '30m':1800000, 
            '1h':3600000, 
            '2h':7200000, 
            '4h':14400000, 
            '1d':86400000
        }
        
        # 给定请求数据
        start_stamp = binance_exchange.parse8601(start_time)
        end_stamp = binance_exchange.parse8601(end_time)
        query_dict = {
            'symbol':symbol,
            'interval':interval,
            'limit':500,
            'startTime':start_stamp
        }

        # 发送请求获取数据
        data_list = []
        while start_stamp < end_stamp:

            query_dict = {
            'symbol':symbol,
            'interval':interval,
            'limit':500,
            'startTime':start_stamp
            }
            for _ in range(5):
                try:
                    response = requests.get(url=baseurl+kline_path, params=query_dict)
                    break
                except:
                    if _ < 4:
                        continue
                    else:
                        print('响应失败')
                        sys.exit()
            single_kline = response.json()
            if single_kline[0][0] == start_stamp:
                if single_kline[-1][0] > end_stamp:
                    numbers_of_delete_row = int((single_kline[-1][0] - end_stamp)/(interval_dict[interval]))
                    single_kline = single_kline[:-numbers_of_delete_row]
                data_list += single_kline
            start_stamp += interval_dict[interval] * 500
        
        # 将获取的数据存入dataframe中
        data = pd.DataFrame(data_list, columns=[
            'datetime',
            'open',
            'high',
            'low',
            'close',
            'vol',
            'closeTime',
            'volAmount',
            'transaction',
            'activeBuyVol',
            'activeBuyTransaction',
            'delete'
        ])
        data.drop(columns=['delete'], inplace=True)
        data['datetime'] = data['datetime'].apply(binance_exchange.iso8601)
        data['closeTime'] = data['closeTime'].apply(binance_exchange.iso8601)
        return data

    def get_high_and_low(symbol:str, interval:str, start_time:str, end_time:str):
        hist_data = getF.get_hist_data(symbol, interval, start_time, end_time)
        high_column = np.array(hist_data['high'])
        low_column = np.array(hist_data['low'])
        return high_column.astype(np.float64), low_column.astype(np.float64)

if __name__ == '__main__':
    
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 
               'XRPUSDT', 'DOGEUSDT', 'TONUSDT', 'ADAUSDT', 
               '1000SHIBUSDT', 'AVAXUSDT', 'TRXUSDT', 'DOTUSDT', 
               'BCHUSDT', 'LINKUSDT', 'MATICUSDT', 'LTCUSDT', 
               'PEOPLEUSDT', 'ICPUSDT', 'UNIUSDT', 'FILUSDT']

    def process_symbols(start, end):
        for symbol in symbols[start:end]:
            print(f"{symbol}开始")
            data = getF.get_hist_data(symbol, '15m', '2021-01-01T00:00:00.000Z', '2024-05-05T00:00:00.000Z')
            data = data[['datetime', 'open', 'high', 'low', 'close', 'vol']]
            data.to_csv(f'D:/crypto/data/15m/{symbol}.csv', index=False)
            print(f"{symbol}结束")
    
    threads = []
    for i in range(5):
        start = i * 4
        end = (i + 1) * 4 if i < 4 else len(symbols)  # 最后一个线程处理剩余的元素
        thread = threading.Thread(target=process_symbols, args=(start, end))
        threads.append(thread)
    
    # 启动线程
    for thread in threads:
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
