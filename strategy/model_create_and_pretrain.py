import pandas as pd
import numpy as np
import argparse
import pandas_ta as ta
from pycaret.regression import *
from scipy.signal import find_peaks
print("Libraries imported")

argparser = argparse.ArgumentParser()
argparser.add_argument('--data_path', type=str, default='data/')
argparser.add_argument('--model_name', type=str, default='model')
argparser.add_argument('--exp_name', type=str, default='exp')
argparser.add_argument('--shift', type=int, default=5)

args = argparser.parse_args()

#load data
data_path = args.data_path
model_name = args.model_name
exp_name = args.exp_name
shift = args.shift

data = pd.read_csv(data_path)
print("Data loaded")

# data preprocessing
# 在特定列中找到局部極大值 (local maxima)
peaks, _ = find_peaks(data['high'])
data['is_local_max'] = 0  # 初始化列
data.loc[peaks, 'is_local_max'] = 1  # 標記局部極大值

# 尋找每個點到下一個局部極大值的價格變化百分比
data['target'] = np.nan  # 初始化列
for i in range(len(data) - 1):
    if data['is_local_max'].iloc[i] == 1:
        continue  # 如果當前點是局部極大值，則跳過
    
    # 找到下一個局部極大值
    next_peak_idx = data.index[data['is_local_max'] & (data.index > i)].min()
    
    if pd.isna(next_peak_idx):
        continue  # 如果沒有找到下一個局部極大值，則跳過

    # 計算價格變化百分比
    price_now = data['high'].iloc[i]
    price_next_peak = data['high'].iloc[next_peak_idx]
    percent_change = ((price_next_peak - price_now) / price_now) * 100
    data['target'].iloc[i] = percent_change

data['SMA5'] = ta.sma(data['close'], length = 5)
data['SMA10'] = ta.sma(data['close'], length = 10)
data['SMA20'] = ta.sma(data['close'], length = 20)
data['SMA60'] = ta.sma(data['close'], length = 60)
data['SMA120'] = ta.sma(data['close'], length = 120)
data['SMA240'] = ta.sma(data['close'], length = 240)

#make shift columns
for idx in range(1, shift + 1):
    name = 'shift_' + str(idx)
    data[name] = data['close'].shift(idx)

#fill nan with 0
data['target'] = data['target'].fillna(0)
data = data.dropna()
print("Data preprocessed")

#check data
print(data.describe())
print(data.shape)

#setup
reg = setup(data = data, target = 'target', session_id = 123,normalize=True,
            ignore_features = ['is_local_max', 'time'],html=False)
print("Setup finished")

#compare models
best2 = compare_models(sort = 'MAE', n_select = 4, exclude=['lightgbm'])
print(best2)
print("Models compared")

#tune model
tuned_best2 = [tune_model(i) for i in best2]
print("Models tuned")

#blend models
blender = blend_models(estimator_list = tuned_best2, fold = 5, optimize = 'MAPE')

#save model
save_model(blender, model_name)
print("Model saved")

print("Experiment finished")