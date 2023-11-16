from backtesting import Strategy
from backtesting import Backtest
import pandas as pd

#load data
df = pd.read_csv('../data/ACHUSDT_5m.csv')
#get front 36 rows
df = df.head(36)
#init Signal and Quant
df['Signal'] = 0
df['Quant'] = 0
#set second row to 1
df.loc[1, 'Signal'] = 1
df.loc[1, 'Quant'] = 0.5
#set third row to 1
df.loc[2, 'Signal'] = 1
df.loc[2, 'Quant'] = 0.5
#set last row to 2
df.loc[29, 'Signal'] = 2
df.loc[29, 'Quant'] = 0.5

#look for nan values
print(df['time'].isnull())

#set time to index
df['time'] = pd.to_datetime(df['time'])
df = df.set_index('time')
df.head()

#rename columns
df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)

def SIGNAL(df):
    return df['Signal']

def QUANT(df):
    return df['Quant']

class Scalping_Strategy(Strategy):

    def init(self):
        super().init()
        self.quant = self.I(QUANT, self.data)
        self.signal = self.I(SIGNAL, self.data)

    def next(self):
        super().next()
        base = float(self.data.Close[-1])
        size_pre = round((float(self.quant[-1])*self.equity)/base)
        # print(self.position)
        # print(size_pre)
        if self.signal == 2:
            self.buy(size=300)
        if self.signal == 1:
            self.sell(size=100)
            

bt = Backtest(df, Scalping_Strategy, cash=1000000)
stat = bt.run()
trade = stat['_trades']
s = stat['_equity_curve']
print(stat.keys())
print(s)