import ccxt
import pandas as pd
import numpy as np
import httpx

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
            response = httpx.get(url=baseurl+kline_path, params=query_dict)
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

    # # 多线程准备工作—编写函数
    # def get_part(symbols, interval:str, start_time:str, end_time:str, first, last, store_to='./'):
        
    #     for symbol in symbols[first: last]:
    #         try:
    #             df = getS.get_hist_data(symbol=symbol, interval=interval, start_time=start_time, end_time=end_time)
    #             df.to_csv(store_to + f'S{symbol}.csv', index=False)
    #         except:
    #             pass
    
    # # 多线程获取多个数据
    # def ThreadGetAllData(interval:str, start_time:str, end_time:str, store_to='./', thread_num=15, timing=True):

    #     #设置币种
    #     baseurl = 'https://api.binance.com'  #初始化baseurl
    #     info_path = '/api/v3/exchangeInfo'
    #     response = requests.get(baseurl+info_path)
    #     exchange_info = response.json()
    #     symbols_values_list = exchange_info['symbols']
    #     symbols = []
    #     for symbol_dict in symbols_values_list:
    #         single_symbol = symbol_dict.get('symbol')
    #         symbols.append(single_symbol)

    #     start_time = time.time()
    #     examples = int(len(symbols) / thread_num)
    #     processes = []

    #     for i in range(thread_num):
            
    #         if i!=thread_num-1:
    #             part = threading.Thread(target=getS.get_part, args=(symbols, interval, start_time, end_time, store_to, i*examples, (i+1)*examples))
    #         else:
    #             part = threading.Thread(target=getS.get_part, args=(symbols, interval, start_time, end_time, store_to, i*examples, None))
    #         processes.append(part)
        
    #     for process in processes:
    #         process.start()
    #     for process in processes:
    #         process.join()
        
    #     end_time = time.time()
    #     elapsed_time = end_time - start_time
    #     formatted_time = str(timedelta(seconds=elapsed_time))
    #     if timing:
    #         print(f"获取数据所用时间：{formatted_time}")


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
            response = httpx.get(url=baseurl+kline_path, params=query_dict)
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

    # # 多线程准备工作—编写函数
    # def get_part(symbols, interval:str, start_time:str, end_time:str, first, last, store_to='./'):

    #     for symbol in symbols[first: last]:
    #         try:
    #             df = getF.get_hist_data(symbol=symbol, interval=interval, start_time=start_time, end_time=end_time)
    #             df.to_csv(store_to + f'F{symbol}.csv', index=False)
    #         except:
    #             pass
    
    # # 多线程获取多个数据
    # def ThreadGetAllData(interval:str, start_time:str, end_time:str, store_to='./', thread_num=15, timing=True):

    #     #设置币种
    #     baseurl = 'https://fapi.binance.com'  #初始化baseurl
    #     info_path = '/fapi/v1/exchangeInfo'
    #     response = requests.get(baseurl+info_path)
    #     exchange_info = response.json()
    #     symbols_values_list = exchange_info['symbols']
    #     symbols = []
    #     for symbol_dict in symbols_values_list:
    #         single_symbol = symbol_dict.get('symbol')
    #         symbols.append(single_symbol)

    #     start_time = time.time()
    #     examples = int(len(symbols) / thread_num)
    #     processes = []

    #     for i in range(thread_num):
            
    #         if i!=thread_num-1:
    #             part = threading.Thread(target=getF.get_part, args=(symbols, interval, start_time, end_time, store_to, i*examples, (i+1)*examples))
    #         else:
    #             part = threading.Thread(target=getF.get_part, args=(symbols, interval, start_time, end_time, store_to, i*examples, None))
    #         processes.append(part)
        
    #     for process in processes:
    #         process.start()
    #     for process in processes:
    #         process.join()
        
    #     end_time = time.time()
    #     elapsed_time = end_time - start_time
    #     formatted_time = str(timedelta(seconds=elapsed_time))
    #     if timing:
    #         print(f"获取数据所用时间：{formatted_time}")