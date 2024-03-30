#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <fstream>
#include <sstream>

/*
conds的表示
+0.000：空仓
+0.010：多头持仓
-0.010：空头持仓
+0.100：多头开仓
-0.100：空头开仓
+0.001：多头平仓
-0.001：空头平仓
+0.101：多头开仓平仓（本次不考虑）
-0.101：空头开仓平仓（本次不考虑）

小数点后一位：是否有开仓动作
小数点后两位：是否全程持仓
小数点后三位：是否有平仓动作
*/

struct PLSInput{

    double principal;
    double proportion;
    double MakerFee;
    double TakerFee;
    unsigned int leverage;

    std::vector<int> signal;    //开仓信号（0，1，-1）
    std::vector<double> open;   //开仓价
    std::vector<double> close;  //收盘价
    std::vector<double> high;
    std::vector<double> low;
    std::vector<double> ps;     //止盈点
    std::vector<double> ls;     //止损点
    std::vector<size_t> remain; //最大持续时长

    bool useable(){
        if (signal.size() != open.size()) return false;
        if (signal.size() != close.size()) return false;
        if (signal.size() != ps.size()) return false;
        if (signal.size() != ls.size()) return false;
        if (signal.size() != remain.size()) return false;
        return true;
    }
};

struct result{
    std::vector<double> net_value;
    std::vector<double> conds;
    std::vector<double> closes;
};

PLSInput read_csv(std::string file){
    PLSInput pls_input;

    // 打开CSV文件
    std::ifstream fin(file);
    if (!fin) {
        std::cerr << "无法打开文件 " << file << std::endl;
        return pls_input; // 返回空的pls_input
    }

    // 逐行读取CSV文件，并将数据存储到PLSInput结构体中的向量中
    std::string line;
    while (std::getline(fin, line)) {
        std::istringstream iss(line);
        int sig;
        double o, c, h, l, p, s;
        size_t r;
        if (!(iss >> sig >> o >> c >> h >> l >> p >> s >> r)) {
            std::cerr << "无法解析CSV文件的行：" << line << std::endl;
            continue;
        }
        pls_input.signal.push_back(sig);
        pls_input.open.push_back(o);
        pls_input.close.push_back(c);
        pls_input.high.push_back(h);
        pls_input.low.push_back(l);
        pls_input.ps.push_back(p);
        pls_input.ls.push_back(s);
        pls_input.remain.push_back(r);
    }

    // 关闭文件
    fin.close();

    // 设置默认值
    pls_input.principal = 10000.0;
    pls_input.proportion = 0.9;
    pls_input.MakerFee = 0.00018;
    pls_input.TakerFee = 0.00045;
    pls_input.leverage = 2;

    return pls_input;
}


void write_csv(const std::string& file, const result& orders) {
    std::ofstream fout(file);
    if (!fout) {
        std::cerr << "无法打开文件 " << file << " 进行写入" << std::endl;
        return;
    }

    size_t n = orders.net_value.size();
    if (n != orders.conds.size() || n != orders.closes.size()) {
        std::cerr << "数据不完整，无法写入CSV文件" << std::endl;
        return;
    }

    fout << "net_value,conds,close_price" << std::endl;
    for (size_t i = 0; i < n; ++i) {
        fout << orders.net_value[i] << "," 
             << orders.conds[i] << "," 
             << orders.closes[i];
        fout << std::endl;
    }

    fout.close();
    std::cout << "CSV文件写入成功！" << std::endl;
}



result plsValue(PLSInput plsinput){
    
    // 初始化变量
    const size_t n = plsinput.signal.size();
    result orders;
    std::vector<double> net_value(n, plsinput.principal);
    std::vector<double> conds(n, 0.0);
    std::vector<double> closes(n, 0.0);

    // 判断输入是否正确
    if (!plsinput.useable()){
        orders.conds = conds;
        orders.net_value = net_value;
        return orders;
    }

    // 输入正确后，处理程序
    for (size_t i=1; i<n; i++){

        double net = net_value[i - 1];

        // 无信号
        if (plsinput.signal[i] == 0){
            conds[i] = 0.000;
            net_value[i] = net;
        }

        // 多头信号
        else if (plsinput.signal[i] == 1){
            
            // 计算开仓数额，浮动与固定
            const double open_price = plsinput.open[i];
            const int quants = static_cast<int>(net * plsinput.leverage * plsinput.proportion / open_price);
            const double fixed = net - quants * open_price * plsinput.MakerFee;
            const double ps = plsinput.ps[i];
            const double ls = plsinput.ls[i];
            double floated = quants * (open_price - plsinput.close[i]);

    

            conds[i] = 0.100;
            net_value[i] = floated + fixed;
            size_t j = 1;

            while (j <= plsinput.remain[i]){
                if (plsinput.low[i + j] >= ls){
                    floated = quants * (ls - open_price);
                    conds[i + j] = 0.001;
                    net_value[i + j] = floated + fixed - quants * ls * plsinput.TakerFee;
                    closes[i] = ls;
                    j++;
                    break;
                }
                else if (plsinput.high[i + j] <= ps){
                    floated = quants * (ps - open_price);
                    conds[i + j] = 0.001;
                    net_value[i + j] = floated + fixed - quants * ps * plsinput.TakerFee;
                    closes[i] = ps;
                    j++;
                    break;
                }
                else{
                    floated = quants * (plsinput.close[i + j] - open_price);
                    conds[i + j] = 0.010;
                    net_value[i + j] = j < plsinput.remain[i] ? floated + fixed : floated + fixed - quants * plsinput.close[i + j] * plsinput.TakerFee;
                    closes[i] = j < plsinput.remain[i] ? 0.0 : plsinput.close[i + j];
                    j++;
                    if (i + j >= n) break;
                }
            }

            i = i + j;
        }

        // 空头信号
        else{
            
            // 计算开仓数额，浮动与固定
            const double open_price = plsinput.open[i];
            const int quants = static_cast<int>(net * plsinput.leverage * plsinput.proportion / open_price);
            const double fixed = net - quants * open_price * plsinput.MakerFee;
            const double ps = plsinput.ps[i];
            const double ls = plsinput.ls[i];
            double floated = quants * (open_price - plsinput.close[i]) * (-1.0);

            conds[i] = -0.100;
            net_value[i] = floated + fixed;
            size_t j = 1;

            while (j <= plsinput.remain[i]){
                if (plsinput.low[i + j] >= ls){
                    floated = quants * (ls - open_price) * (-1.0);
                    conds[i + j] = -0.001;
                    net_value[i + j] = floated + fixed - quants * ls * plsinput.TakerFee;
                    j++;
                    break;
                }
                else if (plsinput.high[i + j] <= ps){
                    floated = quants * (ps - open_price) * (-1.0);
                    conds[i + j] = -0.001;
                    net_value[i + j] = floated + fixed - quants * ps * plsinput.TakerFee;
                    closes[i] = ps;
                    j++;
                    break;
                }
                else{
                    floated = quants * (plsinput.close[i + j] - open_price) * (-1.0);
                    conds[i + j] = -0.010;
                    net_value[i + j] = j < plsinput.remain[i] ? floated + fixed : floated + fixed - quants * plsinput.close[i + j] * plsinput.TakerFee;
                    closes[i] = j < plsinput.remain[i] ? 0.0 : plsinput.close[i + j];
                    j++;
                    if (i + j >= n) break;
                }
            }

            i = i + j;
        }
    }

    orders.conds = conds;
    orders.net_value = net_value;
    orders.closes = closes;
    return orders;
}

int main(){

    PLSInput pls_input = read_csv("signal_with_pls.csv");
    result result_data = plsValue(pls_input);
    write_csv("result.csv", result_data);

    return 0;
}