from typing import Callable
from tqdm import tqdm
import numpy as np


class roll:

    def __init__(self) -> None:
        pass

    def __standardise(X_train:np.ndarray, X_test:np.ndarray):
        row_of_means = np.mean(X_train, axis=0)
        row_of_stds = np.std(X_train, axis=0)
        standardise_data = (X_train - row_of_means) / row_of_stds
        standardise_test = (X_test - row_of_means) / row_of_stds
        return standardise_data, standardise_test

    def KNN(df, factors, labels, bar='我的算法', k:int=5, expire=5, roll_length=2000):

        from sklearn.neighbors import KNeighborsClassifier
        # # # 训练 KNN 模型
        # # 创建并训练 KNN 模型
        # # KNN（K近邻）模型根据输入样本的最近的K个邻居的类别进行分类或者回归，参数如下：
        # # n_neighbors: int, 默认=5
        # #   指定用于分类的邻居数量。较小的值意味着更具噪声鲁棒性，但可能会忽略有用的信息。较大的值使模型更稳定，但也可能过拟合。
        # # weights: {'uniform', 'distance'} or callable, 默认='uniform'
        # #   指定用于预测的权重函数。 'uniform'表示所有邻居的权重相等，'distance'表示权重与距离成反比。您还可以传递一个自定义的权重函数。
        # knn_model = KNeighborsClassifier(n_neighbors=5, weights='uniform')
        # knn_model.fit(X_train, y_train)
        if k:
            knn = KNeighborsClassifier(n_neighbors=k)
        else:
            knn = KNeighborsClassifier()
        
        data = df.copy()
        data.dropna(subset=factors+labels, inplace=True)
        factors_matrix = data[factors].values
        labels_matrix = data[labels].values
        examples = len(factors_matrix)
        signals = np.full((roll_length,), np.nan)
        for train in tqdm(range(examples - roll_length), desc='KNN-'+bar):
            X_train = factors_matrix[train: train+roll_length-expire, :]
            y_train = labels_matrix[train: train+roll_length-expire]
            X_test = factors_matrix[train+roll_length, :]
            X_train, X_test = roll.__standardise(X_train, X_test)              #之前没加标准化，效果很不错
            knn.fit(X_train, y_train.ravel())
            prediction = knn.predict(X_test.reshape(1,-1))
            signals = np.concatenate((signals, prediction))
        signals[signals==0] = np.nan
        data['signalL'] = signals
        df.loc[data.index, 'signalL'] = data['signalL']

        return data

    def SVM(df, factors, labels, bar='我的算法', C:float=1.0, kernel:str='rbf', gamma='scale', expire=5, roll_length:int=2000):
        
        from sklearn.svm import SVC
        # # 创建并训练 SVM 模型
        # # SVM（支持向量机）模型用于分类和回归分析，参数如下：
        # # kernel: {'linear', 'poly', 'rbf', 'sigmoid', 'precomputed'}, 默认='rbf'
        # #   指定核函数的类型。常用的有'linear'线性核、'rbf'高斯核等。'linear'适用于线性可分数据，'rbf'适用于非线性可分数据。
        # # C: float, 默认=1.0
        # #   正则化参数，控制分类器的惩罚项。较小的值表示较强的正则化，适用于更简单的决策边界；较大的值表示较弱的正则化，适用于更复杂的决策边界。
        # # gamma: {'scale', 'auto'} or float, 默认='scale'
        # #   'scale'表示使用1 / (n_features * X.var())作为gamma值，'auto'表示使用1 / n_features。
        # #   gamma参数控制了核函数的宽度，它影响了模型的复杂性。较小的gamma值表示较大的核，适用于简单的决策边界；较大的gamma值表示较小的核，适用于复杂的决策边界。
        # svm_model = SVC(kernel='rbf', C=1.0, gamma='scale')
        # svm_model.fit(X_train, y_train)
        svm = SVC(kernel=kernel, C=C, gamma=gamma)
        
        data = df.copy()
        data.dropna(subset=factors+labels, inplace=True)
        factors_matrix = data[factors].values
        labels_matrix = data[labels].values
        examples = len(factors_matrix)
        signals = np.full((roll_length,), np.nan)
        for train in tqdm(range(examples - roll_length), desc='SVM'+bar):
            X_train = factors_matrix[train: train+roll_length-expire, :]
            y_train = labels_matrix[train: train+roll_length-expire]
            X_test = factors_matrix[train+roll_length, :]
            X_train, X_test = roll.__standardise(X_train, X_test) 
            svm.fit(X_train, y_train.ravel())
            prediction = svm.predict(X_test.reshape(1,-1))
            signals = np.concatenate((signals, prediction))
        signals[signals==0] = np.nan
        data['signalL'] = signals
        df.loc[data.index, 'signalL'] = data['signalL']

        return data

    def Tree(df, factors, labels, bar='我的算法', criterion='gini', max_depth=None, expire=5, roll_length:int=2000):

        from sklearn.tree import DecisionTreeClassifier
        # # 创建并训练决策树模型
        # # 决策树模型通过学习数据特征和标签之间的关系来进行预测，参数如下：
        # # criterion: {'gini', 'entropy'}, 默认='gini'
        # #   指定用于衡量节点纯度的判定标准。'gini'表示使用基尼不纯度，'entropy'表示使用信息熵。两者效果差异不大，可以根据具体情况选择。
        # # max_depth: int, 默认=None
        # #   树的最大深度。较小的值将导致树的简单模型，容易欠拟合；较大的值将导致树的复杂模型，容易过拟合。通常使用交叉验证来选择合适的值。
        # dt_model = DecisionTreeClassifier(criterion='gini', max_depth=None)
        # dt_model.fit(X_train, y_train)
        tree = DecisionTreeClassifier(criterion=criterion, max_depth=max_depth)
        
        data = df.copy()
        data.dropna(subset=factors+labels, inplace=True)
        factors_matrix = data[factors].values
        labels_matrix = data[labels].values
        examples = len(factors_matrix)
        signals = np.full((roll_length,), np.nan)
        for train in tqdm(range(examples - roll_length), desc='Tree'+bar):
            X_train = factors_matrix[train: train+roll_length-expire, :]
            y_train = labels_matrix[train: train+roll_length-expire]
            X_test = factors_matrix[train+roll_length, :]
            X_train, X_test = roll.__standardise(X_train, X_test) 
            tree.fit(X_train, y_train.ravel())
            prediction = tree.predict(X_test.reshape(1,-1))
            signals = np.concatenate((signals, prediction))
        signals[signals==0] = np.nan
        data['signalL'] = signals
        df.loc[data.index, 'signalL'] = data['signalL']

        return data
        

    def LogisticRegression(df, factors, labels, bar='我的算法', penalty='l2', C=1.0, solver='lbfgs', expire=5, roll_length:int=2000):
        
        from sklearn.linear_model import LogisticRegression
        # # 创建并训练逻辑回归模型
        # # 逻辑回归模型用于解决二分类问题，参数如下：
        # # penalty: {'l1', 'l2', 'elasticnet', 'none'}, 默认='l2'
        # #   指定正则化方式。'l1'表示L1正则化，可以使得模型稀疏；'l2'表示L2正则化，可以防止过拟合；'elasticnet'表示L1和L2正则化的组合。
        # # C: float, 默认=1.0
        # #   正则化强度的倒数，即正则化参数的倒数。较小的值表示较强的正则化，适用于稀疏权重；较大的值表示较弱的正则化，适用于更复杂的模型。
        # # solver: {'newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'}, 默认='lbfgs'
        # #   指定求解器。不同的求解器适用于不同的优化问题。'lbfgs'通常适用于小数据集，'liblinear'适用于大数据集，'sag'和'saga'适用于大型数据集。
        # lr_model = LogisticRegression(penalty='l2', C=1.0, solver='lbfgs')
        # lr_model.fit(X_train, y_train)
        lr = LogisticRegression(penalty=penalty, C=C, solver=solver)
        
        data = df.copy()
        data.dropna(subset=factors+labels, inplace=True)
        factors_matrix = data[factors].values
        labels_matrix = data[labels].values
        examples = len(factors_matrix)
        signals = np.full((roll_length,), np.nan)
        for train in tqdm(range(examples - roll_length), desc='LR'+bar):
            X_train = factors_matrix[train: train+roll_length-expire, :]
            y_train = labels_matrix[train: train+roll_length-expire]
            X_test = factors_matrix[train+roll_length, :]
            X_train, X_test = roll.__standardise(X_train, X_test) 
            lr.fit(X_train, y_train.ravel())
            prediction = lr.predict(X_test.reshape(1,-1))
            signals = np.concatenate((signals, prediction))
        signals[signals==0] = np.nan
        data['signalL'] = signals
        df.loc[data.index, 'signalL'] = data['signalL']

        return data
    
    
    def DIYalgorithm(df, factors, labels, algorithm:Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray], bar:str='我的算法', expire=5, roll_length=2000):
        
        data = df.copy()
        data.dropna(subset=factors+labels, inplace=True)
        factors_matrix = data[factors].values
        labels_matrix = data[labels].values
        examples = len(factors_matrix)
        signals = np.full((roll_length,), np.nan)
        for train in tqdm(range(examples - roll_length), desc=bar):
            X_train = factors_matrix[train: train+roll_length-expire, :]
            y_train = labels_matrix[train: train+roll_length-expire]
            X_test = factors_matrix[train+roll_length, :]
            X_train, X_test = roll.__standardise(X_train, X_test) 
            y_train = y_train.ravel()
            X_test = X_test.reshape(1,-1)
            prediction = algorithm(X_train, y_train, X_test)
            signals = np.concatenate((signals, prediction))
        signals[signals==0] = np.nan
        data['signalL'] = signals
        df.loc[data.index, 'signalL'] = data['signalL']

        return data