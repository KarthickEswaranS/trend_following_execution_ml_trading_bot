from src.data import Data
import pandas as pd
import numpy as np

class Strategy(Data):


    def __init__(self):
        super().__init__()


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
    

s = Strategy()
