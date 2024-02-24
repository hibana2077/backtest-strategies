'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-02-23 23:58:23
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-02-24 00:17:54
FilePath: \backtest-strategies-1\strategy\auto_grad.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import torch
from tqdm import trange

# 重新定義參數和變量
a, b, c = 2.0, 3.0, 1.0
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 初始化x值，需要requires_grad=True來使用自動梯度計算，並移至GPU
x_gpu = torch.tensor([0.0], requires_grad=True, device=device)

# 選擇優化器，這裡使用SGD，並將其應用於GPU上的變量
optimizer_gpu = torch.optim.SGD([x_gpu], lr=0.01)

# 設定迭代次數
num_iterations = 10

for _ in range(num_iterations):
    optimizer_gpu.zero_grad()
    f_x_gpu = a * x_gpu**2 + b * x_gpu + c
    # f_x_gpu = -f_x_gpu # 取負號，使其成為最大化問題
    print("=====")
    print(f_x_gpu , x_gpu)
    f_x_gpu.backward()
    print(f_x_gpu , x_gpu)
    optimizer_gpu.step()
    print(f_x_gpu , x_gpu)

# 將結果從GPU移回CPU，並轉換為numpy格式輸出
x_out = x_gpu.cpu().detach().numpy()
fn_out = (a * x_gpu**2 + b * x_gpu + c).cpu().detach().numpy()
print(f'x: {x_out[0]:.4f}, f(x): {fn_out[0]:.4f}')