
from datetime import timedelta
from AlgorithmImports import *
# from pprint import pprint
# from datetime import timedelta

# lean backtest single_option_trade.py --debug ptvsd 



class SingleOptionTrade(QCAlgorithm):
    def Initialize(self):
        
        RESOLUTION = Resolution.Minute
        SMA_VALUE = 19500 # Taking only open market hours into consideration (9:30am-4:00pm), 19,500 is how many minutes are in 50 days.
        
        self.SetStartDate(2013, 4, 1)
        self.SetEndDate(2014, 12, 1)
        self.SetCash(100000)
        
        self.AddEquity(ticker='SPY', resolution=RESOLUTION, market=Market.USA)
        self.AddEquity(ticker='AAPL', resolution=RESOLUTION, market=Market.USA)
        self.AddOption('AAPL', Resolution.Minute, Market.USA)
        
        self.spy:     Equity              = self.AddEquity(ticker='SPY', resolution=Resolution.Minute, market=Market.USA)
        # self.spy_sma: SimpleMovingAverage = self.SMA(symbol=self.spy.Symbol, period=50, resolution=Resolution.Daily) 

        self.symbol = 'AAPL'
        equity: Equity = self.AddEquity(ticker=self.symbol, resolution=RESOLUTION, market=Market.USA)
        option: Option = self.AddOption(self.symbol, RESOLUTION, market=Market.USA)
        
        consolidator = TradeBarConsolidator(timedelta(days=1))
        self.SubscriptionManager.AddConsolidator('SPY', consolidator)
        self.spy_sma = SimpleMovingAverage('spy_sma', 50)
        self.RegisterIndicator('SPY', self.spy_sma, consolidator)
        
        # set our strike/expiry filter for this option chain
        option.SetFilter(lambda u: (u.Strikes(-2, +2).Expiration(30, 90)))

        self.option_symbol = option.Symbol
        
        # Most common request; requesting raw prices for universe securities.
        # self.SetSecurityInitializer(lambda x: x.SetDataNormalizationMode(DataNormalizationMode.Raw))
        # self.SetBenchmark(equity.Symbol)
        return
        
    def get_contracts(self, option_chain: OptionChain, call=False, put=False, itm=False, atm=False, otm=False):
        contract_list = [contract for contract in option_chain]
        
        if call:
            call_list = [contract for contract in contract_list if contract.Right == OptionRight.Call]
            contract_list = call_list
        elif put:
            put_list  = [contract for contract in contract_list if contract.Right == OptionRight.Put]
            contract_list = put_list
        if itm:
            # choose ITM contracts
            itm_contract_list = [contract for contract in contract_list if contract.UnderlyingLastPrice - contract.Strike > 0]
            contract_list = itm_contract_list
        elif atm:
            # or choose ATM contracts
            atm_contract_list = sorted(contract_list, key=lambda contract: abs(option_chain.Underlying.Price - contract.Strike))
            contract_list = atm_contract_list
        elif otm:
            # or choose OTM contracts
            otm_contract_list = [contract for contract in contract_list if contract.UnderlyingLastPrice - contract.Strike < 0]
            contract_list = otm_contract_list
                    
        # sort the contracts by their expiration dates
        return sorted(contract_list, key=lambda contract: contract.Expiry, reverse=True)
        
    def is_long(self):
        return self.spy_sma.Current.Value > self.spy.Close

    def is_short(self):
        return self.spy_sma.Current.Value < self.spy.Close
        
    def OnData(self, data):
        print(f"Current Time: {self.Time}, Portfolio Cash: {self.Portfolio.Cash}, Unrealized Profit: {self.Portfolio.TotalUnrealisedProfit}")
        
        if not self.spy_sma.IsReady:
            return
        
        if self.spy_sma.Current.Value != 0:
            print(f"SMA current: {self.spy_sma.Current.Value}")
            print(f"SPY Close Price: {self.spy.Close}")
        
        filter_results = [self.option_symbol]

        for filtered_symbol in filter_results:
            for kvp in data.OptionChains:
                if kvp.Key != self.option_symbol:          continue
                if kvp.Value is None:                      continue
                if not self.IsMarketOpen(filtered_symbol): continue
                
                option_chain: OptionChain = kvp.Value
                contract_list = []
                
                print(f"SPY Close Price: {self.spy.Close}")
                print(f"SPY SMA:   {self.spy_sma.Current.Value}")                        
                
                if self.is_long():
                    contract_list = self.get_contracts(option_chain, call=True, atm=True)
                elif self.is_short():
                    contract_list = self.get_contracts(option_chain, put=True, atm=True)
                    
                if len(contract_list) > 0:  
                    symbol = contract_list[0].Symbol # AAPL  141018C00645000
                    self.MarketOrder(symbol, 1)

        expiries = [x.Key.ID.Date for x in self.Portfolio if x.Value.Invested and x.Value.Type==SecurityType.Option]
        if len(expiries) > 0:
            print(expiries)
        return
    
    def OnOrderEvent(self, orderEvent):
        order = self.Transactions.GetOrderById(orderEvent.OrderId)
        print("{0}: {1}: {2}".format(self.Time, order.Type, orderEvent))        
        return

    def OnSecuritiesChanged(self, changes):
        for security in changes.RemovedSecurities:
            if security.Invested:
                self.Liquidate(security.Symbol)
        # for security in changes.AddedSecurities: # do I need this?
            # self.SetHoldings(security.Symbol, self.targetPercent)