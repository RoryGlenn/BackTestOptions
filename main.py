from AlgorithmImports import *

from selection_data import SelectionData
from pprint import pprint

# Debug with LeanCLI
# lean backtest "main.py" --debug ptvsd

# https://github.com/QuantConnect/Lean/blob/master/Algorithm.Python/BasicTemplateOptionsAlgorithm.py


# options trading
# https://www.quantconnect.com/tutorials/api-tutorials/using-options-in-quantconnect


# READ THIS WHEN YOU WAKE UP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# https://github.com/QuantConnect/Lean/blob/master/.vscode/readme.md

RESOLUTION = Resolution.Daily
# RESOLUTION = Resolution.Minute


class BasicTemplateFrameworkAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2010, 1, 1) # Set Start Date
        self.SetEndDate(2011, 1, 1)   # Set End Date
        self.SetCash(100_000)         # Set Strategy Cash
        self.AutomaticIndicatorWarmUp = True
        self.SetBenchmark("SPY")

        self.dow_jones_symbols = ['AXP','AMGN','AAPL','BA','CAT','CSCO','CVX','GS','HD','HON','IBM','INTC','JNJ','KO','JPM','MCD','MMM','MRK','MSFT','NKE','PG','TRV','UNH','CRM','VZ','V','WBA','WMT','DIS','DOW']
        self.dow_jones         = [ Symbol.Create(symbol, SecurityType.Equity, Market.USA) for symbol in self.dow_jones_symbols ]
        
        self.sp500_symbols = ['MMM','AOS','ABT','ABBV','ABMD','ACN','ATVI','ADM','ADBE','ADP','AAP','AES','AFL','A','AIG','APD','AKAM','ALK','ALB','ARE','ALGN','ALLE','LNT','ALL','GOOGL','GOOG','MO','AMZN','AMCR','AMD','AEE','AAL','AEP','AXP','AMT','AWK','AMP','ABC','AME','AMGN','APH','ADI','ANSS','ANTM','AON','APA','AAPL','AMAT','APTV','ANET','AIZ','T','ATO','ADSK','AZO','AVB','AVY','BKR','BLL','BAC','BBWI','BAX','BDX','WRB','BRK.B','BBY','BIO','TECH','BIIB','BLK','BK','BA','BKNG','BWA','BXP','BSX','BMY','AVGO','BR','BRO','BF.B','CHRW','CDNS','CZR','CPB','COF','CAH','KMX','CCL','CARR','CTLT','CAT','CBOE','CBRE','CDW','CE','CNC','CNP','CDAY','CERN','CF','CRL','SCHW','CHTR','CVX','CMG','CB','CHD','CI','CINF','CTAS','CSCO','C','CFG','CTXS','CLX','CME','CMS','KO','CTSH','CL','CMCSA','CMA','CAG','COP','ED','STZ','CEG','COO','CPRT','GLW','CTVA','COST','CTRA','CCI','CSX','CMI','CVS','DHI','DHR','DRI','DVA','DE','DAL','XRAY','DVN','DXCM','FANG','DLR','DFS','DISCA','DISCK','DISH','DIS','DG','DLTR','D','DPZ','DOV','DOW','DTE','DUK','DRE','DD','DXC','EMN','ETN','EBAY','ECL','EIX','EW','EA','EMR','ENPH','ETR','EOG','EPAM','EFX','EQIX','EQR','ESS','EL','ETSY','RE','EVRG','ES','EXC','EXPE','EXPD','EXR','XOM','FFIV','FDS','FAST','FRT','FDX','FITB','FRC','FE','FIS','FISV','FLT','FMC','F','FTNT','FTV','FBHS','FOXA','FOX','BEN','FCX','AJG','GRMN','IT','GE','GNRC','GD','GIS','GPC','GILD','GL','GPN','GM','GS','GWW','HAL','HIG','HAS','HCA','PEAK','HSIC','HSY','HES','HPE','HLT','HOLX','HD','HON','HRL','HST','HWM','HPQ','HUM','HBAN','HII','IEX','IDXX','INFO','ITW','ILMN','INCY','IR','INTC','ICE','IBM','IP','IPG','IFF','INTU','ISRG','IVZ','IPGP','IQV','IRM','JBHT','JKHY','J','JNJ','JCI','JPM','JNPR','K','KEY','KEYS','KMB','KIM','KMI','KLAC','KHC','KR','LHX','LH','LRCX','LW','LVS','LDOS','LEN','LLY','LNC','LIN','LYV','LKQ','LMT','L','LOW','LUMN','LYB','MTB','MRO','MPC','MKTX','MAR','MMC','MLM','MAS','MA','MTCH','MKC','MCD','MCK','MDT','MRK','FB','MET','MTD','MGM','MCHP','MU','MSFT','MAA','MRNA','MHK','TAP','MDLZ','MPWR','MNST','MCO','MS','MOS','MSI','MSCI','NDAQ','NTAP','NFLX','NWL','NEM','NWSA','NWS','NEE','NLSN','NKE','NI','NDSN','NSC','NTRS','NOC','NLOK','NCLH','NRG','NUE','NVDA','NVR','NXPI','ORLY','OXY','ODFL','OMC','OKE','ORCL','OGN','OTIS','PCAR','PKG','PARA','PH','PAYX','PAYC','PYPL','PENN','PNR','PBCT','PEP','PKI','PFE','PM','PSX','PNW','PXD','PNC','POOL','PPG','PPL','PFG','PG','PGR','PLD','PRU','PEG','PTC','PSA','PHM','PVH','QRVO','PWR','QCOM','DGX','RL','RJF','RTX','O','REG','REGN','RF','RSG','RMD','RHI','ROK','ROL','ROP','ROST','RCL','SPGI','CRM','SBAC','SLB','STX','SEE','SRE','NOW','SHW','SBNY','SPG','SWKS','SJM','SNA','SEDG','SO','LUV','SWK','SBUX','STT','STE','SYK','SIVB','SYF','SNPS','SYY','TMUS','TROW','TTWO','TPR','TGT','TEL','TDY','TFX','TER','TSLA','TXN','TXT','TMO','TJX','TSCO','TT','TDG','TRV','TRMB','TFC','TWTR','TYL','TSN','UDR','ULTA','USB','UAA','UA','UNP','UAL','UNH','UPS','URI','UHS','VLO','VTR','VRSN','VRSK','VZ','VRTX','VFC','VTRS','V','VNO','VMC','WAB','WMT','WBA','WM','WAT','WEC','WFC','WELL','WST','WDC','WRK','WY','WHR','WMB','WTW','WYNN','XEL','XYL','YUM','ZBRA','ZBH','ZION','ZTS']        
        self.sp500         = [ Symbol.Create(symbol, SecurityType.Equity, Market.USA) for symbol in self.sp500_symbols ]
        self.sp500.append(Symbol.Create('SPY', SecurityType.Equity, Market.USA))

        self.options = []
        self.call    = None
        self.put     = None
        
        for symbol in self.sp500_symbols:
            option = self.AddOption(symbol, RESOLUTION)
            option.SetFilter(TimeSpan.FromDays(30), TimeSpan.FromDays(60))
            self.options.append(option)

        self.SPY = Symbol.Create("SPY", SecurityType.Equity, Market.USA)

        spy             = self.AddEquity("SPY", RESOLUTION).Symbol
        self.SPY_SMA_50 = self.SMA(spy, 50)
        
        # goog_option = self.AddOption("GOOG", RESOLUTION) # Add the option corresponding to underlying stock

        self._changes       = None
        self.stateData      = { }
        self.symbols_chosen = set()

        self.SetSecurityInitializer(lambda x: x.SetDataNormalizationMode(DataNormalizationMode.Raw))
        self.UniverseSettings.Resolution = RESOLUTION

        # https://github.com/QuantConnect/Lean/blob/master/Algorithm.Python/AddUniverseSelectionModelAlgorithm.py
        self.AddUniverseSelection(ManualUniverseSelectionModel(self.sp500))
        return

    def is_buy(self, sd):
        # if sd.price_max:                 # 1. $10 per share
        #     if sd.volume_min:            # 2. Min 1 million shares traded per day (Dow Jones and S&P 500 stocks)
        #         if sd.pop:               # 3. Stocks that pop 3% in a day
        #             if sd.double_volume: # 4. Stocks whos current daily volume is double their average daily volume (use the 50 day moving average volume)
        #                 return True
        # return False
        return sd.price_min and sd.pop

    def is_long(self):
        return self.Securities["SPY"].Price > self.SPY_SMA_50.Current.Value

    def is_short(self):
        return self.Securities["SPY"].Price < self.SPY_SMA_50.Current.Value

    def has_min_price(self, close):
        return close > 10
    
    def has_pop(self, high, open):
        if open <= 1:
            return False
        return (high / open - 1) * 100 >= 3

    def StockFilter(self, data) -> set:
        result = set()
        
        for symbol, value in data.items(): # symbol: QuantConnect.Symbol
            if data.Bars.ContainsKey(symbol) and symbol.Value in data.Bars.keys():
                # if symbol not in self.stateData.keys():
                #     self.stateData[data[symbol]] = SelectionData(symbol)

                # 1 day history call for symbols that we need to initialize
                # history = self.History([symbol], 1, RESOLUTION)
                # avg = self.stateData[data[symbol]]
                # avg.update(data[symbol].EndTime, data[symbol].Close, data[symbol].Volume, history) # data[symbol]: QuantConnect.Data.Market.TradeBar
                
                high  = data.Bars[symbol.Value].High
                open  = data.Bars[symbol.Value].Open
                close = data.Bars[symbol.Value].Close
                
                if self.has_min_price(close) and self.has_pop(high, open):
                    result.add(symbol.Value)

        # # if the stock is a buy, store it in values
        # values = [sd for sd in self.stateData.values() if self.is_buy(sd)]

        # # sort sd by the largest % jump in pop.
        # values.sort(key=lambda sd: sd.pop_percent_daily, reverse=True)

        # # return the top 10 symbol objects
        # return set([ sd.symbol for sd in values[:10] ])
        
        return result
        
        
#########################################################################################################################################

    def OnSecuritiesChanged(self, changes):
        self._changes = changes

        for security in changes.RemovedSecurities:
            #  liquidate securities that have been removed
            if security.Invested:
                self.Liquidate(security.Symbol)
                self.Log("Exit {0} at {1}".format(security.Symbol, security.Close))

    def OnOrderEvent(self, fill):
        print(f"OnOrderEvent({self.Time}):: {fill}")

    def OnData(self, data):
        print(f"Current Time: {self.Time}")

        if self.IsWarmingUp:
            return

        filter_results = list(self.StockFilter(data))

        if len(filter_results) > 0:
            for i in range(len(filter_results)):
                self.symbols_chosen.add(filter_results[i])

            for symbol in filter_results:
                if not self.Portfolio[symbol].Invested:
                    # Let's shoot for 45-60 days expiration

                    if self.is_long():
                        # Straight calls for longs
        
                        for kvp in data.OptionChains:
                            if kvp.Key == symbol: 
                                chain = kvp.Value
                                    
                                # we sort the contracts to find at the money (ATM) contract with farthest expiration
                                contracts = sorted(sorted(sorted(chain, \
                                    key = lambda x: abs(chain.Underlying.Price - x.Strike)), \
                                    key = lambda x: x.Expiry, reverse=True), \
                                    key = lambda x: x.Right, reverse=True)                                    
                                    
                                # if found, trade it
                                if len(contracts) == 0: 
                                    continue
                                
                                symbol = contracts[0].Symbol
                                self.MarketOrder(symbol, 1)
                                self.MarketOnCloseOrder(symbol, -1)
                        return
                    
                    if self.is_short():
                        # Straight puts for shorts
                        return
            return

    def OnEndOfAlgorithm(self):
        pprint(str(self.UniverseManager.ActiveSecurities))

        if len(self.symbols_chosen) == 0:
            print(f"No symbols were chosen")
            return

        print("Chosen symbols") # AAPL,BAC,GOOGL,IBM,AIG,WM,GOOG,SPY,FB

        for symbol in self.symbols_chosen:
            print(symbol)
        return
    

# # List of OptionContract objects
# class OptionChain(self):
#      self.Underlying  # Symbol of underlying asset.
#      self.QuoteBars   # All quotebars in this chain.
#      self.Contracts   # All tradebars in this chain.

# # Tradable Option Contract From Option Chain for Asset
# class OptionContract(self):
#      self.Symbol    # Symbol of tradable asset.
#      self.UnderlyingSymbol    # Symbol of underlying asset.
#      self.Strike     # (decimal) strike price for contract.
#      self.Expiry     # (datetime) expiry date for the contract.
#      self.Right      # (OptionRight) Put or Call
#      self.TheoreticalPrice # (decimal) Price generated from option model.
#      self.ImpliedVolatility   # (decimal) Implied volatility from option model.
#      self.Greeks     # (Greeks) collection of greek properties
#      self.Time       # (datetime) Time of the data.
#      self.OpenInterest # (decimal ) Number of contracts available.
#      self.LastPrice  # (decimal) Last Trade Price
#      self.Volume     # Number of contracts traded this minute.
#      self.BidPrice   # (decimal) Bid price.
#      self.BidSize    # (long) Bid Size
#      self.AskPrice   # (decimal) Asking Price
#      self.AskSize    # (long) Ask Size.
#      self.UnderlyingLastPrice # (decimal) Underlying price of asset.