
from AlgorithmImports import *

# lean backtest single_option_trade.py --debug ptvsd 


class SingleOptionTrade(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2013, 1, 1)
        self.SetEndDate(2015, 6, 1)
        self.SetCash(10000)
        
        # self.AddSecurity()
        # self.AddEquity('SPY', Resolution.Daily)
        self.spy = self.AddEquity('SPX', Resolution.Minute, Market.USA)

        #3. Indicator of a different property (default is close of bar/data):
        # self.emaDailyHigh = self.EMA("SPY", 14, Resolution.Daily, Field.High)

        #4. Using the indicators:
        #4.1  Setup in initialize: make sure you've asked for the data for the asset.
        # self.emaFast = self.EMA("SPY", 14)
        # self.emaSlow = self.EMA("SPY", 28)
        
        self.sma = self.SMA('SPX', 50, Resolution.Minute)
        
    def OnData(self, data):
        #4.2 Consume the indicators in OnData.
        # if self.emaSlow.IsReady and self.emaFast.IsReady:
            # if self.emaFast.Current.Value > self.emaSlow.Current.Value:
                # print("Long")
            # elif self.emaFast.Current.Value < self.emaSlow.Current.Value:
                # print("Short")   
                
        if self.IsWarmingUp:
            print(f"Warmup: {self.Time}")
            return
            
                
        print(f"Current Time: {self.Time}")
                
        if self.sma.IsReady:
            if self.sma.Current.Value > self.spy.Close:
                print("long!")
            elif self.sma.Current.Value < self.spy.Close:
                print("short!")
