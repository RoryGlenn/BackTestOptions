from AlgorithmImports import *

class USEquitySecurityMasterAlgorithm (QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(1998, 1, 1)
        self.SetCash(1000000)
        
        self.equity = self.AddEquity("AAPL", Resolution.Daily).Symbol
        
    def OnData(self, data):
        # Accessing Data - Splits
        split = data.Splits.get(self.equity)
        if split:
            self.Debug(f"{self.Time} >> SPLIT >> {split.Symbol} - {split.SplitFactor} - {self.Portfolio.Cash} - {self.Portfolio[self.equity].Price}")
        
        # Accessing Data - Dividends
        dividend = data.Dividends.get(self.equity)
        if dividend:
            self.Debug(f"{self.Time} >> DIVIDEND >> {dividend.Symbol} - {dividend.Distribution} - {self.Portfolio.Cash} - {self.Portfolio[self.equity].Price}")
            
        # Accessing Data - Delisting
        delisting = data.Delistings.get(self.equity)
        if delisting:
            delistingType = {0: "Warning", 1: "Delisted"}.get(delisting.Type)
            self.Debug(f"{self.Time} >> DELISTING >> {delisting.Symbol} - {delistingType}")
            
        # Accessing Data - Symbol Changed Event
        symbolChangedEvent = data.SymbolChangedEvents.get(self.equity)
        if symbolChangedEvent:
            self.Debug(f"{self.Time} >> SYMBOL CHANGED >> {symbolChangedEvent.OldSymbol} -> {symbolChangedEvent.NewSymbol}")