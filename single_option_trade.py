
from AlgorithmImports import *
from pprint import pprint
from datetime import timedelta
from time import asctime

import logging

# lean backtest single_option_trade.py --debug ptvsd 


RESOLUTION = Resolution.Daily
SMA_VALUE = 50 # 50 days


# Create logging, formatting and file handling variables
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
current_time = asctime().replace(':','-')
file_handler = logging.FileHandler(f'single_option_trade {current_time}.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)



class SingleOptionTrade(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2008, 1, 1)
        self.SetEndDate(2022, 1, 1)
        self.SetCash(100_000)
        self.SetBenchmark("SPY")
        
        self.option_symbol = 'AAPL'
        self.orders = []
        spy_symbol = self.AddEquity(ticker='SPY', resolution=RESOLUTION, market=Market.USA).Symbol
        self.SPY_SMA = self.SMA(symbol=spy_symbol, period=50, resolution=Resolution.Daily)

        self.symbol = self.AddEquity(ticker=self.option_symbol, resolution=RESOLUTION, market=Market.USA)
        self.option = self.AddOption(underlying=self.option_symbol, resolution=RESOLUTION, market=Market.USA)
        
        # Most common request; requesting raw prices for universe securities.
        self.SetSecurityInitializer(lambda x: x.SetDataNormalizationMode(DataNormalizationMode.Raw))
        
        # filter the contracts with strikes between (market price -1, market price +1)
        self.option.SetFilter(-20, +20, timedelta(0), timedelta(180))
        
        self.AutomaticIndicatorWarmUp = True   
        self.consolidators = dict()        
        return
        
    def is_long(self):
        return self.Securities['SPY'].Price > self.SPY_SMA.Current.Value

    def is_short(self):
        return self.Securities['SPY'].Price < self.SPY_SMA.Current.Value
        
    def options_filter(self, data):
        contracts = self.OptionChainProvider.GetOptionContractList(self.aapl.Symbol, data.Time)  ## Get list of Options Contracts for a specific time
        ## Use AddOptionContract() to subscribe the data for specified contract
        self.AddOptionContract(contracts[0], RESOLUTION)  ## Add the first contract in contracts
        return contracts[0]
        
    def OnData(self, data):
        print(f"Current Time: {self.Time}, Portfolio Cash: {self.Portfolio.Cash}, Unrealized Profit: {self.Portfolio.TotalUnrealisedProfit}")
        
        if self.IsWarmingUp:
            return
        
        filter_results = [self.option_symbol]
    
        for filtered_symbol in filter_results:            # iterate over filtered stock symbols
            
            # if '?'+filtered_symbol == symbol.Value:       # if the filtered symbol matches the symbol in the options chain
                # if not self.Portfolio[symbol].Invested:   # if we are currently not invested in the option
                    
            chain = data.OptionChains.GetValue('?'+filtered_symbol)
            
            if chain is None:
                return
                        
            if self.is_long():
                for contract in chain.Value:
                    call = [x for x in chain.Value if contract.Right == 0]
                
                # contracts = self.OptionChainProvider.
                self.Option
                
                for i in contracts:
                    print(i)
                
                # choose ITM contracts
                contracts = [x for x in call if x.UnderlyingLastPrice - x.Strike > 0]
                
                # or choose ATM contracts
                contracts = sorted(chain, key = lambda x: abs(chain.Underlying.Price - x.Strike))[0]
                
                # or choose OTM contracts
                contracts = [x for x in call if call.UnderlyingLastPrice - x.Strike < 0]
            elif self.is_short():  
                put = [x for x in chain if chain.Right == 1]
                    
            # if found, trade it
            if len(contracts) > 0:
                for c in contracts: # c: QuantConnect.Data.Market.OptionChains object
                    print(c)
                
                # trade the contracts with the farthest expiration
                symbol = contracts[0].Symbol
                
                # _contracts = self.OptionChainProvider.GetOptionContractList(symbol, data.Time)  ## Get list of Options Contracts for a specific time
                _contracts = self.OptionChainProvider.GetOptionContractList(self.option_symbol, data.Time)
                _option = self.AddOptionContract(symbol, RESOLUTION)
                
                for i in _contracts:
                    print(i)
                
                self.morder         = self.MarketOrder(symbol, 1)
                self.on_open_morder = self.MarketOnOpenOrder(symbol, 1)
                    
    # expiries = [x.Key.ID.Date for x in self.Portfolio if x.Value.Invested and x.Value.Type==SecurityType.Option]
    # if len(expiries) > 0:
    #     print(expiries)
        
        return
    
    def OnOrderEvent(self, orderEvent):
        order = self.Transactions.GetOrderById(orderEvent.OrderId)
        print("{0}: {1}: {2}".format(self.Time, order.Type, orderEvent))        
        return
        
    # def OnIVConsolidated(self, sender, bar):
    #     self.Log(f"Consolidated IV for {bar.Symbol} received at {self.Time} ... O:{bar.Open}; H:{bar.High}; L:{bar.Low}; C:{bar.Close}")
        
    # def OnSecuritiesChanged(self, changes):1
    #     for security in changes.AddedSecurities:
    #         if security.Type == SecurityType.Option:
    #             symbol = security.Symbol
    #             consolidator = BaseDataConsolidator(timedelta(hours=1))
    #             consolidator.DataConsolidated += self.OnIVConsolidated
    #             self.consolidators[symbol] = consolidator
                
    #     for security in changes.RemovedSecurities:
    #         if security.Type == SecurityType.Option:
    #             if security.Symbol in self.consolidators:
    #                 consolidator = self.consolidators.pop(security.Symbol)
    #                 consolidator.DataConsolidated -= self.OnIVConsolidated