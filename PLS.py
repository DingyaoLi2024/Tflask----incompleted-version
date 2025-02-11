import numpy as np

'''
principal：本金
MakerFee：开仓手续费
TakerFee：平仓手续费
leverage：杠杆
signal：信号，正负代表开多或开空，数值代表仓位的比例
open_prices：开仓价
close_prices：收仓价
close：收盘价
high：最高价
low：最低价
ps：止盈（目前仅支持开仓时设置且不可调）
ls：止损（目前仅支持开仓时设置且不可调）
'''


class PLSInput:
    def __init__(self, principal:float, MakerFee:float, TakerFee:float, leverage:float,
                 signal:np.ndarray, open_prices:np.ndarray, close_prices:np.ndarray, close:np.ndarray, high:np.ndarray, 
                 low:np.ndarray, ps:np.ndarray, ls:np.ndarray):
        self.principal = principal
        self.MakerFee = MakerFee
        self.TakerFee = TakerFee
        self.leverage = leverage
        
        self.signal = signal       # 开仓信号（0，1，-1）
        self.open = open_prices    # 开仓价
        self.closes = close        # 收盘价
        self.close = close_prices  # 收仓价
        self.high = high
        self.low = low
        self.ps = ps               # 止盈点
        self.ls = ls               # 止损点

    def useable(self):
        # Check if all vectors are of the same length
        size = len(self.signal)
        return (len(self.open) == size and
                len(self.close) == size and
                len(self.closes) == size and
                len(self.high) == size and
                len(self.low) == size and
                len(self.ps) == size and
                len(self.ls) == size and
                size > 10)


def pls_value(pls_input:PLSInput):

    n = len(pls_input.close)
    net_value = np.full(n, pls_input.principal)
    conds = np.zeros(n)

    if not pls_input.useable():
        return net_value, conds
    
    i = 1
    pls_input.signal[-1] = 0
    pls_input.signal[-2] = 0
    PosCondition = False
    while i < n:

        if np.isnan(pls_input.signal[i]) or pls_input.signal[i] == 0:
            conds[i] = 0
            net_value[i] = net_value[i - 1]
            i += 1

        # 多头
        elif pls_input.signal[i] > 0:
            
            net = net_value[i - 1]
            open_price = pls_input.open[i]
            position = np.abs(net * pls_input.signal[i] * pls_input.leverage / pls_input.open[i] )                # 头寸大小
            open_fee = position * pls_input.open[i] * pls_input.MakerFee                                          # 开仓手续费
            close_fee = position * pls_input.open[i] * pls_input.TakerFee                                         # 平仓手续费
            PosCondition = True
            net = net - open_fee

            ps = pls_input.ps[i]
            ls = pls_input.ls[i]
            while PosCondition:
                conds[i] = 1
                if pls_input.high[i] >= ps and pls_input.low[i] > ls:
                    net_value[i] = net + position * (ps - open_price) - close_fee
                    PosCondition = False
                elif pls_input.low[i] <= ls and pls_input.high[i] < ps:
                    net_value[i] = net + position * (ls - open_price) - close_fee
                    PosCondition = False
                else:
                    net_value[i] = net + position * (pls_input.close[i] - open_price)
                    if pls_input.signal[i] == 0:
                        net_value[i] = net_value[i] - close_fee
                        PosCondition = False
                if net_value[i] < 0:
                    while i < n:
                        net_value[i] = 0
                        i += 1
                    return conds, net_value
                i += 1


        # 空头
        elif pls_input.signal[i] < 0:

            net = net_value[i - 1]
            open_price = pls_input.open[i]
            position = np.abs(net * pls_input.signal[i] * pls_input.leverage / pls_input.open[i] )                # 头寸大小
            open_fee = position * pls_input.open[i] * pls_input.MakerFee                                          # 开仓手续费
            close_fee = position * pls_input.open[i] * pls_input.TakerFee                                         # 平仓手续费
            PosCondition = True
            net = net - open_fee

            ps = pls_input.ps[i]
            ls = pls_input.ls[i]
            while PosCondition:
                conds[i] = 1
                if pls_input.high[i] >= ls and pls_input.low[i] > ps:
                    net_value[i] = net - position * (ls - open_price) - close_fee
                    PosCondition = False
                elif pls_input.low[i] <= ps and pls_input.high[i] < ls:
                    net_value[i] = net - position * (ps - open_price) - close_fee
                    PosCondition = False
                else:
                    net_value[i] = net - position * (pls_input.close[i] - open_price)
                    if pls_input.signal[i] == 0:
                        net_value[i] = net_value[i] - close_fee
                        PosCondition = False
                if net_value[i] < 0:
                    while i < n:
                        net_value[i] = 0
                        i += 1
                    return conds, net_value
                i += 1
        
        else:
            raise ValueError(f'数据为{pls_input.signal[i]}')

    return conds, net_value
