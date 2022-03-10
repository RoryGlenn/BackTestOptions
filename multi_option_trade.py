# To run program
# lean backtest single_option_trade.py --debug ptvsd 


from AlgorithmImports import *
from datetime         import timedelta
from pprint           import pprint

RESOLUTION       = Resolution.Minute
# BENCHMARK_SYMBOL = 'SPY'
BENCHMARK_SYMBOL = 'GFM'


class MultiOptionTrade(QCAlgorithm):
    def Initialize(self) -> None:
        self.SetStartDate(2015, 1, 1)
        self.SetEndDate(2017, 1, 1)
        self.SetCash(100_000)
        self.SetSecurityInitializer(lambda x: x.SetDataNormalizationMode(DataNormalizationMode.Raw))
        self.SetBenchmark(self.AddEquity(BENCHMARK_SYMBOL, resolution=RESOLUTION, fillDataForward=False).Symbol)

        self.purchased          = []
        self.equity_symbol_list = [BENCHMARK_SYMBOL]
        self.oh_prices          = {equity: {'open': 0, 'high': 0} for equity in self.equity_symbol_list} # construct open/high price dictionary
        
        # Add Equities
        self.benchmark: Equity = self.AddEquity(ticker=BENCHMARK_SYMBOL, resolution=RESOLUTION, market=Market.USA, fillDataForward=False)
        
        self.equities = [self.AddEquity(ticker=equity, resolution=RESOLUTION, market=Market.USA, fillDataForward=False)     for equity in self.equity_symbol_list]
        self.options  = [self.AddOption(underlying=equity, resolution=RESOLUTION, market=Market.USA, fillDataForward=False) for equity in self.equity_symbol_list]
        
        for option in self.options:
            option.SetFilter(lambda universe: universe.Strikes(-10, +10).Expiration(timedelta(0), timedelta(180))) # set our strike/expiry filter for this option chain    

        # Consolidate SPY SMA minute values to 50 Days
        consolidator = TradeBarConsolidator(timedelta(days=1))
        self.SubscriptionManager.AddConsolidator(symbol=BENCHMARK_SYMBOL, consolidator=consolidator)
        self.benchmark_sma = SimpleMovingAverage('benchmark_sma', 50)
        self.RegisterIndicator(symbol=BENCHMARK_SYMBOL, indicator=self.benchmark_sma, consolidator=consolidator)
        
        for equity in self.equities:
            print(f"Equity: {equity.Symbol}, Start Date: {equity.Symbol.ID.Date}")
            
        for option in self.options:
            print(f"Option: {option.Symbol}, Start Date: {option.Symbol.ID.Date}")
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
        return self.benchmark_sma.Current.Value > self.benchmark.Close

    def is_short(self) -> bool:
        return self.benchmark_sma.Current.Value < self.benchmark.Close
        
    def has_min_price(self, price) -> bool:
        return price > 10
    
    def has_pop(self, high, open) -> bool:
        return ((high / open - 1) * 100 >= 3) if open != 1 else False
        
    def get_filtered_stocks(self, data: PythonSlice) -> set:
        result = set()
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
                        continue
                    
                    if data.ContainsKey(symbol.Value):
                        bars: TradeBar = data[symbol.Value]
                        if bars is not None:
                            self.oh_prices[symbol.Value]['open'] = bars.Open
                            
    def set_high_prices(self, data: PythonSlice) -> None:
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
                        if self.Time.hour == 9 and self.Time.minute == 31:
                            if symbol.Value in self.oh_prices:
                                self.oh_prices[symbol.Value]['high'] = bars.High
                        else:
                            # If the current minute bar is higher than the our currently recorded high, 
                            # store that as the new high.
                            if symbol.Value in self.oh_prices:
                                # double check that this is passing in minute values rather than day values...
                                if self.oh_prices[symbol.Value]['high'] < bars.High:
                                    self.oh_prices[symbol.Value]['high'] = bars.High
    
    def OnData(self, data: PythonSlice) -> None:
        if not self.benchmark_sma.IsReady:
            return
        
        print(f"[{self.Time}] data.Keys length: {len(data)} Portfolio Cash: {self.Portfolio.Cash}, Unrealized Profit: {self.Portfolio.TotalUnrealisedProfit}")
    
        # record the open and high prices.
        self.set_open_prices(data)
        self.set_high_prices(data)
        
        filter_results = self.get_filtered_stocks(data)

        for symbol in filter_results:
            print(f"{symbol} open: {self.oh_prices[symbol]['open']}, high: {self.oh_prices[symbol]['high']}")

            # checking if contracts works
            contracts = self.OptionChainProvider.GetOptionContractList(symbol, data.Time)
            if len(contracts) > 0:
                ## Use AddOptionContract() to subscribe the data for specified contract
                self.AddOptionContract(contracts[0], Resolution.Minute)  ## Add the first contract in contracts
                symbol: Symbol = contracts[0]
                
                self.MarketOrder(symbol, 1)
                print(f"Invested in {symbol.Value}")
                print(f"Holdings: {self.Securities[symbol.Underlying.Value].Holdings}")        
        
        
        # doesn't crash lean if we don't use a list comprehension
        # option_invested = list()
        for security in self.Portfolio:
            if security.Value.Invested and security.Value.Type==SecurityType.Option:
                # option_invested.append(security.Key)
        
                # if len(option_invested) > 0:
                    if self.Time + timedelta(2) > security.Key.ID.Date:
                        self.Liquidate(security.Key, "Too Close to expirtation")
                        print(f"Liquidated {security.Key}: Too Close to expirtation")

        # for filtered_symbol in filter_results:
        #     for kvp in data.OptionChains:
        #         print(kvp)
        #         print(kvp.Key)
        #         print(kvp.Key.Underlying)
                
        #         if kvp.Key.Underlying != filtered_symbol:  continue
        #         if kvp.Value is None:                      continue
        #         if not self.IsMarketOpen(filtered_symbol): continue
        #         if filtered_symbol in self.purchased:      continue
                
        #         option_chain:  OptionChain = kvp.Value
        #         contract_list: list        = []
                
        #         if self.is_long():
        #             contract_list = self.get_contracts(option_chain, call=True, atm=True)
        #         elif self.is_short():
        #             contract_list = self.get_contracts(option_chain, put=True, atm=True)
                    
        #         if len(contract_list) > 0:  
        #             symbol: Symbol = contract_list[0].Symbol # AAPL  141018C00645000
        #             self.MarketOrder(symbol, 1)
        #             print(f"Invested in {symbol.Value}")
        #             print(f"Holdings: {self.Securities[symbol.Underlying.Value].Holdings}")
        return
    
    def OnOrderEvent(self, orderEvent: OrderEvent) -> None:
        order = self.Transactions.GetOrderById(orderEvent.OrderId)
        print("{0}: {1}: {2}".format(self.Time, order.Type, orderEvent))
        
        if orderEvent.Status == OrderStatus.Submitted:
            pass
        
        # check if our order filled then add it to the list
        if orderEvent.Status == OrderStatus.Filled:
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