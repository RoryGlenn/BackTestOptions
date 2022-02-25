from AlgorithmImports import *


# Debug with LeanCLI
# lean backtest ".\StevenCawiezellStrategy1\" --debug ptvsd

class SelectionData(object):
    def __init__(self, symbol):
        self.symbol       = symbol
        self.volume       = 0

        self.volume_sma_period = 50

        self.price_min   = 10
        self.pop_percent = 3
        self.volume_min  = 1_000_000
        self.volume_mult = 2

        self.pop_percent_daily = 0
        # self.price_min         = False
        self.pop               = False
        self.volume_min        = False
        self.double_volume     = False
        # self.volume_sma_50 = SimpleMovingAverage(self.volume_sma_period)
        return

    def update(self, time, price, volume, history) -> None:
        # self.volume = volume
        # self.volume_sma_50.Update(time, volume)
        
        print("time", time)
        print("price", price)
        print("volume", volume)
        print("history", history)
        

        if not history.empty:
            self.pop           = self.is_pop(history)
            # self.volume_min    = self.is_volume_min()
            # self.double_volume = self.is_double_volume()
            self.price_min     = self.is_price_min(history)
        return

    # 1. Maximum price is $10 per share
    def is_price_min(self, history) -> bool:
        # return (0 < history.close[0] < self.price_max)
        return history.close[0] >= 10

    # 2. Min 1 million shares traded per day (Dow Jones and S&P 500 stocks)        
    def is_volume_min(self) -> bool:
        return self.volume >= self.volume_min
        
    # 3. Stocks that pop 3% in a day
    def is_pop(self, history) -> bool:
        # if ((history.high[0] / history.open[0]) - 1) * 100 >= self.pop_percent:
            # print(f"{self.symbol} pop percent: {((history.high[0] / history.open[0]) - 1) * 100}")
        return (history.high[0] / history.open[0] - 1) * 100 >= self.pop_percent

    # 4. Stocks whos current daily volume is double their average daily volume (use the 50 day moving average volume)
    def is_double_volume(self):
        return self.volume*self.volume_mult > self.volume_sma_50.Current.Value
