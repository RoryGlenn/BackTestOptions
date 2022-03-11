from AlgorithmImports import *
from datetime         import timedelta

RESOLUTION       = Resolution.Minute
BENCHMARK_SYMBOL = 'SPY'


class MultiOptionTrade(QCAlgorithm):
    def Initialize(self) -> None:
        self.SetStartDate(2012, 1, 1)
        self.SetEndDate(2020, 1, 1)
        
        self.SetCash(100_000)
        self.SetSecurityInitializer(lambda x: x.SetDataNormalizationMode(DataNormalizationMode.Raw))
        self.SetBenchmark(self.AddEquity(BENCHMARK_SYMBOL, resolution=RESOLUTION).Symbol)

        self.purchased          = []
        self.equity_symbol_list = ['AAPL', 'FB', 'FOXA','IBM', 'WM', 'BAC', 'AIG', 'GOOG']
        self.oh_prices          = {equity: {'open': 0, 'high': 0} for equity in self.equity_symbol_list} # construct open/high price dictionary
        
        # Add Equities
        self.benchmark = self.AddEquity(ticker=BENCHMARK_SYMBOL, resolution=RESOLUTION, market=Market.USA)
        
        self.equities = [self.AddEquity(ticker=equity, resolution=RESOLUTION, market=Market.USA)     for equity in self.equity_symbol_list]
        self.options  = [self.AddOption(underlying=equity, resolution=RESOLUTION, market=Market.USA) for equity in self.equity_symbol_list]
        
        for option in self.options:
            option.SetFilter(lambda u: (u.Strikes(-5, +5).Expiration(30, 90))) # set our strike/expiry filter for this option chain

        # Consolidate SPY SMA minute values to 50 Days
        consolidator = TradeBarConsolidator(timedelta(days=1))
        self.SubscriptionManager.AddConsolidator(symbol=BENCHMARK_SYMBOL, consolidator=consolidator)
        self.benchmark_sma = SimpleMovingAverage('benchmark_sma', 50)
        self.RegisterIndicator(symbol=BENCHMARK_SYMBOL, indicator=self.benchmark_sma, consolidator=consolidator)
        return
        
    def get_contracts(self, option_chain, call=False, put=False, itm=False, atm=False, otm=False) -> list:
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
        return self.benchmark_sma.Current.Value > self.benchmark.Close

    def is_short(self) -> bool:
        return self.benchmark_sma.Current.Value < self.benchmark.Close
        
    def has_min_price(self, price) -> bool:
        return price > 10
    
    def has_pop(self, _high, _open) -> bool:
        return ((_high / _open - 1) * 100 >= 3) if _open != 1 else False
        
    def get_filtered_stocks(self, data) -> set:
        result = set()
        for symbol, oh_dict in self.oh_prices.items():
            _open = oh_dict['open']
            _high = oh_dict['high']
            if self.has_min_price(_open) and self.has_pop(_high, _open):
                result.add(symbol)
        return result
        
    def set_open_prices(self, data) -> None:
        if self.Time.hour == 9 and self.Time.minute == 31:
            if data.HasData:
                for symbol in data.Keys:
                    if symbol.HasUnderlying:
                        continue
                    
                    if data.ContainsKey(symbol.Value):
                        bars: TradeBar = data[symbol.Value]
                        if bars is not None:
                            if symbol.Value in self.oh_prices:
                                self.oh_prices[symbol.Value]['open'] = bars.Open
        return
    def set_high_prices(self, data) -> None:
        """Continuously store the highest price of the day.
        Reset the high on market open."""
        if data.HasData:
            for symbol in data.Keys:
                if symbol.HasUnderlying:
                    continue

                if data.ContainsKey(symbol.Value):
                    bars: TradeBar = data[symbol.Value]
                    if bars is not None:
                        # On market open, store the high for the day.
                        if self.Time.hour == 9 and self.Time.minute == 30: # MIGHT NEED TO CHANGE THIS BACK TO 31 IF DOESNT WORK
                            if symbol.Value in self.oh_prices:
                                self.oh_prices[symbol.Value]['high'] = bars.High
                        else:
                            # If the current minute bar is higher than the our currently recorded high, 
                            # store that as the new high.
                            if symbol.Value in self.oh_prices:
                                if self.oh_prices[symbol.Value]['high'] < bars.High:
                                    self.oh_prices[symbol.Value]['high'] = bars.High
        return
    
    def get_invested_options(self) -> list:
        return [x.Key for x in self.Portfolio if x.Value.Invested and x.Value.Type==SecurityType.Option]

    def liquidated_expiry_options(self, option_invested):
        """Liquidates options within 4 days of expire date"""
        if len(option_invested) > 0:
            for option in option_invested:
                # self.Debug(f"[Current Time {self.Time}], Option Expiration Time: {option.ID.Date}")
                # self.Debug(f"Invested Option {option.Underlying.Value}: {option}")
                if self.Time + timedelta(days=4) > option.ID.Date:
                    self.Liquidate(option, "Too Close to expirtation")
                    self.Debug(f"Liquidated {option}: Too Close to expirtation\n")
                    if option.Underlying.Value in self.purchased:
                        self.purchased.remove(option.Underlying.Value)
        return

    def OnData(self, data) -> None:
        if not self.benchmark_sma.IsReady:
            return
        
        self.set_open_prices(data)
        self.set_high_prices(data)
        
        filter_results  = self.get_filtered_stocks(data)
        option_invested = self.get_invested_options()
        self.liquidated_expiry_options(option_invested)

        for filtered_symbol in filter_results:
            for kvp in data.OptionChains:
                if kvp.Key.Underlying != filtered_symbol:  continue
                if kvp.Value is None:                      continue
                if not self.IsMarketOpen(filtered_symbol): continue
                if filtered_symbol in self.purchased:      continue
                
                # WHY DO WE KEEP TRYING TO BUY THE SAME SYMBOL MORE THAN ONCE?!?!>>>>>>>>>?>>>>>>>>>>>>>>>?
                
                option_chain  = kvp.Value
                contract_list = []
                
                if self.is_long():
                    contract_list = self.get_contracts(option_chain, call=True, atm=True)
                elif self.is_short():
                    contract_list = self.get_contracts(option_chain, put=True, atm=True)
                    
                if len(contract_list) > 0:
                    # symbol = contract_list[0].Symbol # AAPL  141018C00645000
                    contract = contract_list[0]
                    self.AddOptionContract(contract.Symbol, Resolution.Minute)
                    
                    if self.Portfolio.GetMarginRemaining(contract.Symbol, OrderDirection.Buy) > 0:
                        if contract.Symbol.Value not in self.purchased:
                            self.MarketOrder(contract.Symbol, 1)
                            # self.SetHoldings(symbol, 0.10) # spend 10% of our portfolio on this
                            self.Debug(f"{contract.Symbol} Purchased\n")
                            self.purchased.append(contract.Symbol.Underlying.Value)
        return
    
    def OnOrderEvent(self, orderEvent) -> None:
        order = self.Transactions.GetOrderById(orderEvent.OrderId)
        # self.Debug("OnOrderEvent {0}: {1}: {2}".format(self.Time, order.Type, orderEvent))
        
        # if orderEvent.Status == OrderStatus.Submitted:
        #     pass
        
        # check if our order filled then add it to the list
        # if orderEvent.Status == OrderStatus.Filled:
            # if orderEvent.Symbol.HasUnderlyingSymbol:
                # self.purchased.append(orderEvent.Symbol.Underlying)
            # else:
                # self.purchased.append(orderEvent.Symbol)
                
        if order.Type == OrderType.OptionExercise:
            self.Debug(f"OptionExercise {orderEvent.Symbol} Profit: {self.Portfolio[orderEvent.Symbol].Profit}, Total Profit: {self.Portfolio.TotalProfit}")
        return

    # def OnSecuritiesChanged(self, changes) -> None:
    #     for security in changes.RemovedSecurities:
    #         if security.Invested:
    #             self.Liquidate(security.Symbol)
    #         if security.Symbol.Underlying.Value in self.purchased:
    #             self.purchased.remove(security.Symbol.Underlying.Value)
    #     return