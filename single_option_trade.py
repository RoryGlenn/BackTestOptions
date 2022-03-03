# To run program
# lean backtest single_option_trade.py --debug ptvsd 


from AlgorithmImports import *
from datetime         import timedelta


RESOLUTION       = Resolution.Minute
BENCHMARK_SYMBOL = 'SPY'

# lean data generate -> generate random market data: try this before submitting to steven

# Your organization needs to have an active Security Master subscription to download data from the 'US Equity Options' dataset
# You can add the subscription at https://www.quantconnect.com/datasets/quantconnect-security-master/pricing

class SingleOptionTrade(QCAlgorithm):
    def Initialize(self) -> None:
        self.SetStartDate(2013, 12, 16)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)
        self.SetSecurityInitializer(lambda x: x.SetDataNormalizationMode(DataNormalizationMode.Raw))
        # self.SetBenchmark(self.AddEquity(BENCHMARK_SYMBOL).Symbol)

        self.purchased          = []
        self.equity_symbol_list = [BENCHMARK_SYMBOL, 'FB', 'GOOG','FOXA','IBM', 'WM',  'BAC', 'AIG', 'AAPL']
        self.oh_prices          = {equity: {'open': 0, 'high': 0} for equity in self.equity_symbol_list} # construct open/high price dictionary
        self.is_put             = False
        self.is_call            = False
        
        # Add Equities
        self.benchmark: Equity = self.AddEquity(ticker=BENCHMARK_SYMBOL, resolution=RESOLUTION, market=Market.USA)
        
        self.equities = [self.AddEquity(ticker=equity, resolution=RESOLUTION, market=Market.USA) for equity in self.equity_symbol_list]
        self.options  = [self.AddOption(underlying=equity, resolution=RESOLUTION, market=Market.USA) for equity in self.equity_symbol_list]
        
        for option in self.options:
            option.SetFilter(lambda u: (u.Strikes(-10, +10).Expiration(0, 180))) # set our strike/expiry filter for this option chain    

        # Consolidate SPY SMA minute values to 50 Days
        consolidator = TradeBarConsolidator(timedelta(days=1))
        self.SubscriptionManager.AddConsolidator(BENCHMARK_SYMBOL, consolidator)
        self.spy_sma = SimpleMovingAverage('spy_sma', 50)
        self.RegisterIndicator(BENCHMARK_SYMBOL, self.spy_sma, consolidator)
        return
        
    def get_contracts(self, option_chain: OptionChain, call=False, put=False, itm=False, atm=False, otm=False) -> list:
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
        
    def is_long(self) -> bool:
        return self.spy_sma.Current.Value > self.benchmark.Close

    def is_short(self) -> bool:
        return self.spy_sma.Current.Value < self.benchmark.Close
        
    def has_min_price(self, price) -> bool:
        return price > 10
    
    def has_pop(self, high, open) -> bool:
        return ((high / open - 1) * 100 >= 3) if open != 1 else False
        
    def get_filtered_stocks(self, data: PythonSlice) -> set:
        result = set()
        # if data.HasData:
        #     for symbol in data.Keys:
        #         if data.ContainsKey(symbol.Value):
        #             bars: TradeBar = data[symbol.Value]
        #             if bars is not None:
        #                 if symbol.HasUnderlying:
        #                     symbol = symbol.Underlying

        """Stock filter results in an empty list every since the above code was commented out!"""
        
        # if self.has_min_price(o_symbol_price) and self.has_pop(h_symbol_price, o_symbol_price):
            # result.add(h_symbol)
            
        for symbol, oh_dict in self.oh_prices.items():
            open = oh_dict['open']
            high = oh_dict['high']
            if self.has_min_price(open) and self.has_pop(high, open):
                result.add(symbol)
                
        return result
        
    def set_open_prices(self, data: PythonSlice) -> None:
        if self.Time.hour == 9 and self.Time.minute == 31:
            if data.HasData:
                for symbol in data.Keys:
                    
                    if symbol.HasUnderlying:
                        symbol = symbol.Underlying
                    
                    if data.ContainsKey(symbol.Value):
                        bars: TradeBar = data[symbol.Value]
                        if bars is not None:
                            # self.open_values[symbol.Value] = bars.Open   
                            self.oh_prices[symbol.Value]['open'] = bars.Open
                            
    def set_high_prices(self, data: PythonSlice) -> None:
        """Continuously store the highest price of the day.
        Reset the high on market open."""
        if data.HasData:
            for symbol in data.Keys:
                
                if symbol.HasUnderlying:
                    symbol: Symbol = symbol.Underlying

                if data.ContainsKey(symbol.Value):
                    bars: TradeBar = data[symbol.Value]
                    if bars is not None:
                        # On market open, store the high for the day.
                        if self.Time.hour == 9 and self.Time.minute == 31:
                            # self.high_values[symbol.Value]  = bars.High
                            self.oh_prices[symbol.Value]['high'] = bars.High
                        else:
                            # If the current minute bar is higher than the our currently recorded high, 
                            # store that as the new high.
                            # if self.high_values[symbol.Value] < bars.High:
                                # self.high_values[symbol.Value] = bars.High
                                
                            # double check that this is passing in minute values rather than day values...
                            if self.oh_prices[symbol.Value]['high'] < bars.High:
                                self.oh_prices[symbol.Value]['high'] = bars.High
    
    def OnData(self, data: PythonSlice) -> None:
        if not self.spy_sma.IsReady:
            return
        
        print(f"[{self.Time}] Portfolio Cash: {self.Portfolio.Cash}, Unrealized Profit: {self.Portfolio.TotalUnrealisedProfit}")
        
        # if time == open, record the open prices.
        self.set_open_prices(data)
        self.set_high_prices(data)
        
        filter_results = self.get_filtered_stocks(data)

        if len(filter_results) > 0:
            print(filter_results)
            
        if self.Time.year == 2014 and self.Time.month == 6 and self.Time.day == 4:
            print("Time to step through the code")

        for filtered_symbol in filter_results:
            for kvp in data.OptionChains:
                if kvp.Key.Underlying != filtered_symbol:  continue
                if kvp.Value is None:                      continue
                if not self.IsMarketOpen(filtered_symbol): continue
                if filtered_symbol in self.purchased:      continue
                
                option_chain:  OptionChain = kvp.Value
                contract_list: list        = []
                
                if self.is_long():
                    contract_list = self.get_contracts(option_chain, call=True, atm=True)
                    self.is_call = True
                elif self.is_short():
                    contract_list = self.get_contracts(option_chain, put=True, atm=True)
                    self.is_put = True
                    
                if len(contract_list) > 0:  
                    symbol: Symbol = contract_list[0].Symbol # AAPL  141018C00645000
                    self.MarketOrder(symbol, 1)
                    print(f"Invested in {symbol.Value}")
                    print(f"Holdings: {self.Securities[symbol.Underlying.Value].Holdings}")
                    

        # expiries = [x.Key.ID.Date for x in self.Portfolio if x.Value.Invested and x.Value.Type==SecurityType.Option]
        # if len(expiries) > 0:
        #     print(expiries)
        return
    
    def OnOrderEvent(self, orderEvent: OrderEvent) -> None:
        order = self.Transactions.GetOrderById(orderEvent.OrderId)
        print("{0}: {1}: {2}".format(self.Time, order.Type, orderEvent))
        
        if orderEvent.Status == OrderStatus.Submitted:
            pass
        
        # check if our order filled then add it to the list
        if orderEvent.Status == OrderStatus.Filled:
            # print(order.Symbol.GetOptionTypeFromUnderlying(order.Symbol.Underlying))
            self.purchased.append(orderEvent.Symbol.Underlying.Value)
        if order.Type == OrderType.OptionExercise:
            print(f"{orderEvent.Symbol} Profit: {self.Portfolio[orderEvent.Symbol].Profit}, Total Profit: {self.Portfolio.TotalProfit}")
        return

    def OnSecuritiesChanged(self, changes: SecurityChanges) -> None:
        for security in changes.RemovedSecurities:
            if security.Invested:
                self.Liquidate(security.Symbol)
                if security.Symbol.Underlying.Value in self.purchased:
                    self.purchased.remove(security.Symbol.Underlying.Value)
        # for security in changes.AddedSecurities: # do I need this?
            # self.SetHoldings(security.Symbol, self.targetPercent)