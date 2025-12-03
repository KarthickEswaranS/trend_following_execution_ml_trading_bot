from src.strategy import Strategy
import numpy as np

class Execution(Strategy):
    
    def __init__(self):
        super().__init__()
        self.initial_balance = 100000
        self.balance = self.initial_balance
        self.lot_size = 1
        self.risk = 0.03
        self.reward = 0.9

        self.long_profit_trades = []
        self.long_loss_trades = []
        self.short_profit_trades = []
        self.short_loss_trades = []

        # self.buy_sell()


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

    def buy_sell(self):
        df = self.signal()

        cols = ['long_buy_price','long_sell_price','short_buy_price','short_sell_price',
                'long_sl','short_sl','position']
        
        for col in cols:
            df[col] = np.nan
            df['position'] = 0

        position = 0
        entry_price = None
        exit_price = None
        long_sl = None
        short_sl = None
        pnl = None

        for i in range(len(df)):

            close = df.iloc[i]['close']
            enter_long_trade = df.iloc[i]['enter_long']
            exit_long_trade = df.iloc[i]['exit_long']
            enter_short_trade = df.iloc[i]['enter_short']
            exit_short_trade = df.iloc[i]['exit_short']

            #long Entry
            if position == 0 and enter_long_trade:
                
                entry_price = close

                df.at[df.index[i] ,'long_buy_price'] = entry_price
                df.at[df.index[i], 'position'] = 1

                long_sl =  round(entry_price * (1 - self.risk), 2)

                df.at[df.index[i], 'long_sl'] = long_sl
                
                position = 1
                    
                continue
            #short Entry
            elif position == 0 and enter_short_trade:

                entry_price = close
                
                df.at[df.index[i] ,'short_buy_price'] = entry_price
                df.at[df.index[i], 'position'] = -1

                short_sl =  round(entry_price * (1 + self.risk), 2)
    
                df.at[df.index[i], 'short_sl'] = short_sl

                position = -1
                    
                continue

            #Long Exit
            if position == 1 and (close <= long_sl):
                exit_price = long_sl
                df.at[df.index[i], 'long_sell_price'] = round(exit_price, 2)
                df.at[df.index[i], 'long_sl'] = round(exit_price, 2)

                df.at[df.index[i], 'position'] = 0
                position = 0

                pnl = (exit_price - entry_price) * self.lot_size
                self.long_loss_trades.append(abs(pnl))
                self.balance += pnl

                continue

            elif position == 1 and  exit_long_trade:
                exit_price = close
                df.at[df.index[i], 'long_sell_price'] = round(exit_price, 2)

                df.at[df.index[i], 'position'] = 0
                position = 0

                pnl = (exit_price - entry_price) * self.lot_size
                self.long_profit_trades.append(pnl)
                self.balance += pnl
                continue


            #Short Exit
            if position == -1 and (close >= short_sl):
                exit_price = short_sl
                df.at[df.index[i], 'short_sell_price'] = round(exit_price, 2)
                df.at[df.index[i], 'short_sl'] = round(exit_price, 2)
                
                df.at[df.index[i], 'position'] = 0
                position = 0

                pnl = (exit_price - entry_price) * self.lot_size
                self.short_loss_trades.append(abs(pnl))
                self.balance += pnl
                continue

            elif position == -1 and exit_short_trade:
                exit_price = close
                df.at[df.index[i], 'short_sell_price'] = round(exit_price, 2)

                df.at[df.index[i], 'position'] = 0
                position = 0

                pnl = (exit_price - entry_price) * self.lot_size
                self.short_profit_trades.append(pnl)
                self.balance += pnl
                continue
        # self.results()
        return df       
    
    def results(self):
        print("================ FINAL RESULTS ================")
        print(f"Balance: {round(self.balance, 2)}")

        total_profit = round(sum(self.long_profit_trades) + sum(self.short_profit_trades), 2)
        print(f"Total Profit: + {total_profit}")

        total_loss = round(sum(self.long_loss_trades)  + sum(self.short_loss_trades), 2)
        print(f"Total Loss: - {round(total_loss,2)}")

        npl =   round(total_profit - total_loss , 2)
        print(f"Net Profit/Loss: {npl}")

        trades = [len(self.long_profit_trades), len(self.long_loss_trades), len(self.short_profit_trades), len(self.short_loss_trades)]
        total_no_of_trades = sum(trades)

        profit_trades = [len(self.long_profit_trades), len(self.short_profit_trades)]
        win = ( sum(profit_trades) / total_no_of_trades) * 100
        print(f"Win Rate %: {win:.2f}%")

        print("-------------------------------------------------")
        print(f"Total No Of Long Profit Trades: {len(self.long_profit_trades)}")
        print(f"Total No Of Long Loss Trades: {len(self.long_loss_trades)}")
        print(f"Total No Of Short Profit Trades: {len(self.short_profit_trades)}")
        print(f"Total No Of Short Loss Trades: {len(self.short_loss_trades)}")

Execution()