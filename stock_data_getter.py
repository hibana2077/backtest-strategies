'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-02-22 10:02:54
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-02-22 10:11:22
FilePath: \backtest-strategies-1\stock_data_getter.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# Purpose: get data from ccxt and save it to csv file
import pandas as pd
import argparse
import logging
import yfinance as yf

#set up logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('data_getter')

#set up argument parser
# input : symbol, timeframe, start_time, end_time

parser = argparse.ArgumentParser(description='data getter')
parser.add_argument('--symbol', type=str, default='AAPL')
parser.add_argument('--period', type=str, default='1y')

args = parser.parse_args()

def get_data(symbol:str, period:str) -> pd.DataFrame:

    #get data from yfinance
    period = period
    symbol = symbol
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=period)
    return data

#set up data saver

def save_data(df:pd.DataFrame, symbol:str, period:str):
    df.to_csv(f'./data/{symbol}_{period}.csv')

#Basic data check

def data_checker(df:pd.DataFrame):
    #check if there is any nan value
    if df.isnull().values.any():
        logger.warning('there is nan value in the data')
    #check if ther has any duplicated index
    if df.index.duplicated().any():
        logger.warning('there is duplicated index in the data')
    #check if the index is in order
    if not df.index.is_monotonic_increasing and not df.index.is_monotonic_decreasing:
        logger.warning('the index is not in order')

#run

if __name__ == '__main__':
    logger.info('start getting data')
    df = get_data(args.symbol, args.period)
    logger.info('data get')
    data_checker(df)
    logger.info('start saving data')
    save_data(df, args.symbol, args.period)
    logger.info('data saved')
