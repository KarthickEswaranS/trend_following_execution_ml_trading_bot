import keyring
from binance import Client
import pandas as pd

class Data:
    def __init__(self):
        self.api_key = keyring.get_password('binance', 'api_key' )
        self.api_sercet = keyring.get_password('binance', 'api_secret')
        self.client = Client(self.api_key, self.api_sercet)
        self.hist_data = self.client.get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_1DAY, '1-1-2022', '30-12-2024')

    def data_process(self):
        df = pd.DataFrame(self.hist_data)
        df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                          'quote_asset_volume', 'no_of_trades', 'taker_buy_base_volume',
                          'taker_buy_quote_volume', 'ignore']
        df[['open_time','close_time']] = df[['open_time','close_time']].apply(pd.to_datetime, unit = 'ms')

        numeric_data = ['open','high', 'low', 'close', 'volume', 'quote_asset_volume', 'taker_buy_base_volume',
                          'taker_buy_quote_volume']
        df[numeric_data] = df[numeric_data].apply(pd.to_numeric, axis=1)

        return df

d= Data()