from scipy.signal import find_peaks,argrelextrema
from sklearn.neighbors import KernelDensity
import numpy as np
import pandas as pd
#strategy functions

def group_levels(levels, tolerance=100):
    sorted_levels = sorted(levels)
    grouped_levels = []
    
    current_group = [sorted_levels[0]]
    for level in sorted_levels[1:]:
        if level - current_group[-1] <= tolerance:
            current_group.append(level)
        else:
            grouped_levels.append(np.mean(current_group))
            current_group = [level]
            
    grouped_levels.append(np.mean(current_group))
    return np.round(grouped_levels, 2)

def add_support_resistance(df:pd.DataFrame, window_size:int=100):
    # Limit the data to the last 'window_size' rows
    limited_df = df.iloc[-window_size:]

    # Extract the 'close' prices
    close_prices = limited_df['close'].values

    # Find local maxima and minima
    local_maxima_indices, _ = find_peaks(close_prices)
    local_maxima_values = close_prices[local_maxima_indices]
    local_minima_indices = argrelextrema(close_prices, np.less)[0]
    local_minima_values = close_prices[local_minima_indices]

    # Perform Kernel Density Estimation
    close_prices_reshaped = close_prices.reshape(-1, 1)
    kde = KernelDensity(kernel='gaussian', bandwidth=200).fit(close_prices_reshaped)
    price_range = np.linspace(min(close_prices), max(close_prices), 1000)[:, np.newaxis]
    log_density = kde.score_samples(price_range)
    density_peaks, _ = find_peaks(np.exp(log_density))
    density_peaks_values = price_range[density_peaks].flatten()

    # Combine and make them unique to avoid duplicate lines
    all_levels = np.unique(np.concatenate([local_maxima_values, local_minima_values, density_peaks_values]))

    # Group the levels using 7.5% of the standard deviation as the tolerance
    std_deviation = np.std(close_prices)
    tolerance = int(round(std_deviation * 0.075))
    grouped_levels = group_levels(all_levels, tolerance=tolerance)

    # Create two new columns for the closest support and resistance levels in the original DataFrame
    closest_support = [None] * len(df)
    closest_resistance = [None] * len(df)

    for i in range(len(df)):
        if i < len(df) - window_size:
            continue
        
        price = df['close'].iloc[i]
        support_levels = [level for level in grouped_levels if level < price]
        resistance_levels = [level for level in grouped_levels if level > price]

        closest_support[i] = min(support_levels, default=np.nan, key=lambda x: abs(x - price))
        closest_resistance[i] = min(resistance_levels, default=np.nan, key=lambda x: abs(x - price))

    df['closest_support'] = closest_support
    df['closest_resistance'] = closest_resistance

    return df

# 標記策略買賣點
def mark_strategies(df):
    # 初始化信號欄位
    df['breakout_signal'] = 0
    df['pullback_signal'] = 0
    df['consolidation_signal'] = 0
    df['bottom_fishing_signal'] = 0
    
    # 突破/跌破策略
    df.loc[df['close'] > df['resistance'], 'breakout_signal'] = 1
    df.loc[df['close'] < df['support'], 'breakout_signal'] = -1
    
    # 回踩策略
    df.loc[(df['close'] > df['ema_22']) & (df['close'].shift(1) < df['ema_22']), 'pullback_signal'] = 1
    df.loc[(df['close'] < df['ema_22']) & (df['close'].shift(1) > df['ema_22']), 'pullback_signal'] = -1
    
    # 盤整策略
    df.loc[df['close'] == df['upper'], 'consolidation_signal'] = -1
    df.loc[df['close'] == df['lower'], 'consolidation_signal'] = 1
    
    # 抄底策略
    df.loc[(df['close'] < df['ema_22']) & (df['close'] > df['support']), 'bottom_fishing_signal'] = 1
    
    return df