#include <vector>
#include <map>
#include <string>
#include <stdexcept>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>


/*
该程序接受以下参数：
    int类型向量：原始信号（signal：-1开空仓，0不开仓，1开仓）
    int类型向量：开仓持续时长（LNum：0当日开仓当日平仓，1当日开仓下一日平仓....）
    double类型向量：开仓价（open）
    double类型向量：收盘价（close）
    double类型向量：跟随开仓时间的平仓价格（stop）

该程序返回以下参数：
    一个字典，键为列表对应的列名，值为double类型的vector
    allSignal：每日的持仓状态，1.0多头持仓，-1.0空头持仓，0.0空仓
    return：每日收益率
    op：仓位情况，0.001开仓，0.111持续持仓，0空仓，0.101平仓，0.011当日开仓当日平仓
*/



// 开仓价可以和开盘价不同，但收盘价与到期平仓价必须相同
std::map<std::string, std::vector<double>>  pslSignal(const std::vector<int> signal, const std::vector<int> LNum, const std::vector<double> open, const std::vector<double> close, const std::vector<double> stop){
    
    // 异常情况处理
    if (signal.size() != LNum.size() || LNum.size() != open.size() || open.size() != close.size() || close.size() != stop.size()){
        throw std::invalid_argument("输入有误，请调整参数");
    }

    // 循环遍历列表，充实pslSignal
    std::vector<double> finalSignal;
    std::vector<double> rate;
    std::vector<double> op;
    int start = 0;
    int i = 0;
    int j;
    while (i<signal.size()){
        
        try{
            if (signal[i] == 0){                // 不开仓的情况
                finalSignal.push_back(0.0);
                rate.push_back(0.0);
                op.push_back(0.0);
                i++;
            }
            else if (LNum[i] == 0){             // 当日开仓当日平仓的情况
                finalSignal.push_back(static_cast<double>(signal[i]));
                rate.push_back(stop[i] / open[i] - 1);
                op.push_back(0.011);
                i++;
            }
            else{                               // 当日开仓并继续持有的情况
                start = i;
                if (i+LNum[start] < static_cast<int>(signal.size())){
                    i += LNum[start];
                }
                else{
                    i = static_cast<int>(signal.size()) - 1;
                }
                finalSignal.push_back(static_cast<double>(signal[start]));
                rate.push_back(close[start] / open[start] - 1);
                op.push_back(0.001);

                for (j=start+1; j<i; j++){
                    finalSignal.push_back(static_cast<double>(signal[start]));
                    rate.push_back(close[j] / close[j-1] - 1);
                    op.push_back(0.111);
                }

                finalSignal.push_back(finalSignal.back());
                rate.push_back(stop[start] / close[i-1] - 1);
                op.push_back(0.101);
                i++;

            }
        }
        catch (const std::exception& e) {
            finalSignal.push_back(0.0);
            rate.push_back(0.0);
            op.push_back(0.0);
            i++;
        }
    }

    std::map<std::string, std::vector<double>> result;
    result["allSignal"] = finalSignal;
    result["return"] = rate;
    result["opCond"] = op;

    return result;
}


namespace py = pybind11;

PYBIND11_MODULE(netValue, m) {
    m.def("pslSignal", &pslSignal, "psl signal");
}