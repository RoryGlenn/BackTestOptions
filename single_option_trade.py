
from AlgorithmImports import *
# from pprint import pprint
# from datetime import timedelta

# lean backtest single_option_trade.py --debug ptvsd 


RESOLUTION = Resolution.Minute
SMA_VALUE = 50 # 50 days

### <summary>
### This example demonstrates how to add options for a given underlying equity security.
### It also shows how you can prefilter contracts easily based on strikes and expirations, and how you
### can inspect the option chain to pick a specific option contract to trade.
### </summary>
### <meta name="tag" content="using data" />
### <meta name="tag" content="options" />
### <meta name="tag" content="filter selection" />
class SingleOptionTrade(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2014, 6, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)
        
        self.symbol = 'AAPL'
        spy_symbol = self.AddEquity(ticker='SPY', resolution=RESOLUTION, market=Market.USA).Symbol
        self.SPY_SMA = self.SMA(symbol=spy_symbol, period=50, resolution=Resolution.Daily)

        equity = self.AddEquity(ticker=self.symbol, resolution=RESOLUTION, market=Market.USA)
        option = self.AddOption(self.symbol, RESOLUTION, market=Market.USA)
        
        # set our strike/expiry filter for this option chain
        option.SetFilter(lambda u: (u.Strikes(-2, +2)
                                     # Expiration method accepts TimeSpan objects or integer for days.
                                     # The following statements yield the same filtering criteria
                                     .Expiration(0, 180)))
                                     #.Expiration(TimeSpan.Zero, TimeSpan.FromDays(180))))

        self.option_symbol = option.Symbol
        self.AutomaticIndicatorWarmUp = True
        # Most common request; requesting raw prices for universe securities.
        # self.SetSecurityInitializer(lambda x: x.SetDataNormalizationMode(DataNormalizationMode.Raw))
        self.SetBenchmark(equity.Symbol)
        return
        
    def get_contracts(self, option_chain: OptionChain, call=False, put=False, itm=False, atm=False, otm=False):
        contract_list = [contract for contract in option_chain]
        print(len(contract_list))
        
        if call:
            call_list = [contract for contract in contract_list if contract.Right == OptionRight.Call]
            print(len(call_list))
            contract_list = call_list
        elif put:
            put_list  = [contract for contract in contract_list if contract.Right == OptionRight.Put]
            print(len(put_list))
            contract_list = put_list
        if itm:
            # choose ITM contracts
            itm_contract_list = [contract for contract in contract_list if contract.UnderlyingLastPrice - contract.Strike > 0]
            print(len(itm_contract_list))
            contract_list = itm_contract_list
        elif atm:
            # or choose ATM contracts
            atm_contract_list = sorted(contract_list, key=lambda contract: abs(option_chain.Underlying.Price - contract.Strike))#[0]
            print(len(atm_contract_list))
            contract_list = atm_contract_list
        elif otm:
            # or choose OTM contracts
            otm_contract_list = [contract for contract in contract_list if contract.UnderlyingLastPrice - contract.Strike < 0]
            print(len(otm_contract_list))
            contract_list = otm_contract_list
        return contract_list
        
    def is_long(self):
        return self.Securities['SPY'].Price > self.SPY_SMA.Current.Value

    def is_short(self):
        return self.Securities['SPY'].Price < self.SPY_SMA.Current.Value
        
        
        
    def OnData(self, data):
        print(f"Current Time: {self.Time}, Portfolio Cash: {self.Portfolio.Cash}, Unrealized Profit: {self.Portfolio.TotalUnrealisedProfit}")
        
        if self.IsWarmingUp:
            return
        
        # if not self.IsMarketOpen(self.option_symbol):
        #     return
        
        filter_results = [self.option_symbol]

        for filtered_symbol in filter_results:
            for kvp in data.OptionChains:
                if kvp.Key != self.option_symbol: continue
                if kvp.Value is None:             continue
                
                option_chain: OptionChain = kvp.Value
                
                contract_list = [contract for contract in option_chain]
                
                call_list = [contract for contract in contract_list if contract.Right == OptionRight.Call]
                
                put_list  = [contract for contract in contract_list if contract.Right == OptionRight.Put]
                
                # choose ITM contracts
                itm_contract_list = [contract for contract in call_list if contract.UnderlyingLastPrice - contract.Strike > 0]

                # or choose ATM contracts
                atm_contracts = sorted(call_list, key = lambda contract: abs(option_chain.Underlying.Price - contract.Strike))#[0]
                
                # or choose OTM contracts
                otm_contracts = [contract for contract in call_list if contract.UnderlyingLastPrice - contract.Strike < 0]
                                
                # Buy the ATM call option with the furthest expiration date
                if len(atm_contracts) > 0:  
                    symbol = atm_contracts[0].Symbol # AAPL  141018C00645000
                    if self.IsMarketOpen(symbol):
                        self.MarketOrder(symbol, 1)
                        print(f"Current Time: {self.Time}, Portfolio Cash: {self.Portfolio.Cash}, Unrealized Profit: {self.Portfolio.TotalUnrealisedProfit}")

        expiries = [x.Key.ID.Date for x in self.Portfolio if x.Value.Invested and x.Value.Type==SecurityType.Option]
        if len(expiries) > 0:
            print(expiries)
        return
    
    def OnOrderEvent(self, orderEvent):
        order = self.Transactions.GetOrderById(orderEvent.OrderId)
        print("{0}: {1}: {2}".format(self.Time, order.Type, orderEvent))        
        return
