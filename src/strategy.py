from src.data import Data
import pandas as pd
import numpy as np

class Strategy(Data):
    def __init__(self):
        super().__init__()
        self.initial_balance = 100000
        self.balance = self.initial_balance
        self.lot_size = 1
        self.leverage = 0.01
        self.risk = 0.03
        self.reward = 0.09

        # self.signal()
        # self.execution()
        # self.find_high_low()
        self.features()
    def smma_logic(self, data, length):
        smma_values = []

        for i in range(len(data)):
            if i < length:
                smma_values.append(np.nan)
            elif i==length:
                smma_values.append(data.iloc[:length].mean())
            else:
                smma_values.append((smma_values[-1]* (length-1)+ data.iloc[i])/length)

        return pd.Series(smma_values, index=data.index)
    
    def features(self):
        df = self.data_process()
        df.set_index('open_time', inplace=True)
        df['hl_avg'] =  df[['high', 'low']].mean(axis=1) 
        df['jaw'] = self.smma_logic(df['hl_avg'], 28)
        df['teeth'] = self.smma_logic(df['hl_avg'], 14)
        df['lip'] = self.smma_logic(df['hl_avg'], 7)
        df['daily_return'] = df['close'].pct_change(1)

        return df
    
    def signal(self):
        df = self.features()

        df['enter_long'] = (
            (df['close'].shift(1) > df['teeth'].shift(1)) &
            (df['close'].shift(1) > df['lip'].shift(1)) &
            (df['close'].shift(1) > df['jaw'].shift(1)) 
           
        )

        df['enter_short'] = (
            (df['close'].shift(1) < df['teeth'].shift(1)) &
            (df['close'].shift(1) < df['lip'].shift(1)) &
            (df['close'].shift(1) < df['jaw'].shift(1)) 
            
        )

        df['exit_long'] = (
            ((df['close'] < df['lip']) & (df['close'] < df['teeth'])) 
           
        )
        
        df['exit_short'] = (
            ((df['close'] > df['lip']) & (df['close'] > df['teeth'])) 
           
        )
        return df
    
    def execution(self):
        df = self.signal()
        cols = ['long_buy_price','long_sell_price','short_buy_price','short_sell_price',
                'long_sl','short_sl','position']
        
        for col in cols:
            df[col] = np.nan
            df['position'] = 0

        position = 0
        entry_price = None
        exit_price = None
        long_tp = None
        long_sl = None
        short_tp = None
        short_sl = None

        for i in range(len(df)):

            close = df.iloc[i]['close']
            enter_long_trade = df.iloc[i]['enter_long']
            exit_long_trade = df.iloc[i]['exit_long']
            enter_short_trade = df.iloc[i]['enter_short']
            exit_short_trade = df.iloc[i]['exit_short']

            #long Entry
            if position == 0 and enter_long_trade:
                
                margin_required = round(self.leverage * entry_price * self.lot_size, 2)
                
                if self.balance < margin_required:
                   print("Insufficient margin")

                elif position == 0 and enter_long_trade:
                    entry_price = close

                    df.at[df.index[i] ,'long_buy_price'] = entry_price
                    df.at[df.index[i], 'position'] = 1

                    long_sl =  round(entry_price * (1 - self.risk), 2)
                    # long_tp =  round(entry_price *(1 + self.reward), 2)

                    df.at[df.index[i], 'long_sl'] = long_sl
                    # df.at[df.index[i], 'long_tp'] = long_tp
                   
                    position = 1
                    
                continue

            #Long Exit
            if position == 1 and (close <= long_sl):
                exit_price = long_sl
                df.at[df.index[i], 'long_sell_price'] = round(exit_price, 2)
                df.at[df.index[i], 'long_sl'] = round(exit_price, 2)

                df.at[df.index[i], 'position'] = 0
                position = 0
                continue

            elif position == 1 and  exit_long_trade:
                exit_price = close
                df.at[df.index[i], 'long_sell_price'] = round(exit_price, 2)

                df.at[df.index[i], 'position'] = 0
                position = 0
                continue

            #Short Entry
            if position == 0 and enter_short_trade:

                entry_price = close
                
                margin_required = round(self.leverage * entry_price * self.lot_size, 2)
                
                if self.balance < margin_required:
                    print("Insufficient margin")

                elif position == 0 and enter_short_trade:

                    df.at[df.index[i] ,'short_buy_price'] = entry_price
                    df.at[df.index[i], 'position'] = -1

                    short_sl =  round(entry_price * (1 + self.risk), 2)
                    # short_tp =  round(entry_price *(1 - self.reward), 2)
                    
                    df.at[df.index[i], 'short_sl'] = short_sl
                    # df.at[df.index[i], 'short_tp'] = short_tp

                    position = -1
                    
                continue

            #Short Exit
            if position == -1 and (close >= short_sl):
                exit_price = short_sl
                df.at[df.index[i], 'short_sell_price'] = round(exit_price, 2)
                df.at[df.index[i], 'short_sl'] = round(exit_price, 2)
                
                df.at[df.index[i], 'position'] = 0
                position = 0
                continue

            elif position == -1 and exit_short_trade:
                exit_price = close
                df.at[df.index[i], 'short_sell_price'] = round(exit_price, 2)

                df.at[df.index[i], 'position'] = 0
                position = 0
                continue

        return df       
    

s = Strategy()
