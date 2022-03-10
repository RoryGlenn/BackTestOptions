from AlgorithmImports import *

class USEquitySecurityMasterAlgorithm (QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(1980, 1, 1) #[2013-10-04 09:31:00] SPY Open: 145.032465884 -> [2013-10-11 16:00:00] SPY Open: 147.133508522
        self.SetCash(1000000)
        
        equity = self.AddEquity("AAPL", Resolution.Daily, fillDataForward=False) # [2014-06-05 09:31:00] AAPL Open: 20.799606114481975 -> [2014-06-09 16:00:00] AAPL Open: 21.096665938
        option = self.AddOption('AAPL', Resolution.Daily, fillDataForward=False)
        
        print(f"Equity: {equity.Symbol.ID}, Start Date: {equity.Symbol.ID.Date}")
        print(f"Option: {option.Symbol.ID}, Start Date: {option.Symbol.ID.Date}")
        return
        
    def OnData(self, data: PythonSlice):
        for key in data:
            print(f"[{self.Time}] {key.Key} Open: {data.Bars[key.Key].Open}")
            
            if key.Key.HasUnderlying:
                print(key.Key)
            