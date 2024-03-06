#include <vector>
#include <string>
#include <map>
#include <cmath>
#include <stdexcept>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>


/*
该程序接受以下参数：
    向量1：持仓状态（第一个元素必须是0）
    向量2：净值
该程序返回以下参数：
    字典：{开仓次数：int，盈利次数：int}
*/


std::map<std::string, int> static_of_position(const std::vector<int>& conditions, const std::vector<double>& net_values){

    if (conditions.size() != net_values.size() || conditions.size() <5){
        throw std::invalid_argument("输入列表长度不够，或长度不一致");
    }

    int creating_times = 0;
    int profit_times = 0;
    double init_value;

    if (conditions[0]!=0){
        creating_times++;
    }

    for (size_t i=1; i<conditions.size()-1; i++){
        if (conditions[i] == 0){
            continue;
        }
        else if (conditions[i]!=conditions[i-1] && conditions[i]!=conditions[i+1]){
            creating_times++;
            profit_times += net_values[i] > net_values[i-1] ? 1 : 0;
        }
        else if (conditions[i]!=conditions[i-1]){
            creating_times++;
            init_value = net_values[i-1];
        }
        else if (conditions[i]!=conditions[i+1]){
            profit_times += net_values[i] > init_value ? 1 : 0;
        }
        else{
            continue;
        }
    }

    size_t length = conditions.size();
    if (conditions[length-1] == conditions[length-2] && conditions.back()!=0){
        profit_times += net_values.back() > init_value ? 1 : 0;
    }
    else if (conditions.back() != conditions[length-2] && conditions.back()!=0){
        creating_times++;
        profit_times += net_values.back() > net_values[length-2] ? 1 : 0;
    }

    std::map<std::string, int> result;
    result["position_creating_times"] = creating_times;
    result["position_profit_times"] = profit_times;

    return result;
}



namespace py = pybind11;

PYBIND11_MODULE(WinRate, m) {
    m.def("static_of_position", &static_of_position, "static_of_position");
}