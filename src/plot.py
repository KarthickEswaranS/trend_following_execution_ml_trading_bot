from src.execution import Execution
import mplfinance as mplf
import pandas as pd
import numpy as np

class Plot(Execution):

    def __init__(self):
        super().__init__()
        self.plot_data()

    def plot_data(self):
        df = self.buy_sell()
        
        price_data = [
            mplf.make_addplot(df["jaw"], color='red'),
            mplf.make_addplot(df["teeth"], color='yellow'),
            mplf.make_addplot(df["lip"], color='blue'),
            mplf.make_addplot(df['long_buy_price'], type='scatter', markersize=50, marker='^', color='blue'),
            mplf.make_addplot(df['long_sell_price'], type='scatter', markersize=50, marker='_', color='blue'),
            mplf.make_addplot(df['short_buy_price'], type='scatter', markersize=50, marker='v', color='black'),
            mplf.make_addplot(df['short_sell_price'], type='scatter', markersize=50, marker='_', color='black'),
            mplf.make_addplot(df['long_sl'], type='scatter', markersize=21, marker='_', color='red'),
            mplf.make_addplot(df['short_sl'], type='scatter', markersize=21, marker='_', color='black'),
        ]

        mplf.plot(
            df,
            type='candle',
            style='yahoo',
            volume=False,
            addplot = price_data,
            figratio = (18,10),
            figscale = 1,

        )

p = Plot()
           