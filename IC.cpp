#include <vector>
#include <string>
#include <cmath>
#include <numeric>
#include <algorithm>
#include <stdexcept>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>


/*
该程序接受以下参数：
    向量1：因子
    向量2：收益率
    整数：回测时间
该程序返回以下参数：
    向量：IC值（未测区间均为0）
*/

// 冒泡排序
void order(std::vector<double>& Vec){
    size_t length = Vec.size();
    for (size_t n=length-1; n>0; n--){
        for (size_t m=0; m<n; m++){
            if (Vec[m] > Vec[m+1]){
                double temp = Vec[m];
                Vec[m] = Vec[m+1];
                Vec[m+1] = temp;
            }
        }
    }
    return;
}

std::vector<double> sortedRanks(const std::vector<double>& vec) {
    std::vector<double> sortedVec = vec;
    std::sort(sortedVec.begin(), sortedVec.end());
    std::unordered_map<double, double> rankSumMap;
    for (size_t i = 0; i < sortedVec.size(); ++i) {
        double rank = i + 1;
        size_t j = i + 1;
        while (j < sortedVec.size() && sortedVec[j] == sortedVec[i]) {
            rank += j + 1;
            ++j;
        }
        rank /= (j - i);
        rankSumMap[sortedVec[i]] += rank;
        i = j - 1;
    }
    std::vector<double> result;
    for (const auto& val : vec) {
        result.push_back(rankSumMap[val]);
    }
    return result;
}

double spearmanr(const std::vector<double>& x, const std::vector<double>& y){
    std::vector<double> x_sorted = sortedRanks(x);
    std::vector<double> y_sorted = sortedRanks(y);
    int n = static_cast<int>(x.size());
    double d = 0.0;
    for (int i=0; i<n; i++){
        d += 6 * std::pow(x_sorted[i] - y_sorted[i], 2);
    }
    double result = 1.0 - d / (n * (n*n - 1));
    return result;
}



std::vector<double> IC(std::vector<double> factors, std::vector<double> returns, int T){

    // 判断向量长度是否相等且大于T
    if (factors.size()!=returns.size() || static_cast<int>(factors.size())<=T || T<10){
        throw std::invalid_argument("输入有误，请调整参数");
    }

    // 创建需返回的向量
    std::vector<double> ICValues(returns.size());

    // 引入算法并填充结果
    for (int i=0; i<static_cast<int>(factors.size()); i++){
        if (i < T-1){
            ICValues[i] = 0.0;
        }
        else{
            std::vector<double> Xs(T);
            std::vector<double> Ys(T);
            for (int j=0; j<T; j++){
                Xs[j] = factors[i-(T-1)+j];
                Ys[j] = returns[i-(T-1)+j];
            }
            ICValues[i] = spearmanr(Xs, Ys);
        }
    }

    return ICValues;
}


namespace py = pybind11;

PYBIND11_MODULE(IC, m) {
    m.def("IC", &IC, "IC");
}