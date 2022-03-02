
# I did this step while having my conda env activated
# 1. pip install lean==1.0.78 (this will install the quantconnect api into the conda env)
# 2. conda activate lean
# 3. lean backtest main.py --debug ptvsd 

# for ref
# https://github.com/QuantConnect/Lean/tree/master/Algorithm.Python#installing-python-36


# options trading
# https://www.quantconnect.com/tutorials/api-tutorials/using-options-in-quantconnect


"""

TODO

Create a new script that only trades AAPL
Add the equity and the option with and without he universe
Is there an options chain when OnData is called?


"""

import QuantConnect
from AlgorithmImports import *
from pprint import pprint
from datetime import timedelta
import logging

from time import asctime

RESOLUTION = Resolution.Daily


# Create logging, formatting and file handling variables
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")

current_time = asctime().replace(':','-')

file_handler = logging.FileHandler(f'src/strategies/logs/alpaca {current_time}.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)




class BasicTemplateFrameworkAlgorithm(QCAlgorithm):
    def Initialize(self):
        # pprint(dir(QuantConnect))
        
        self.SetStartDate(2010, 1, 1)
        self.SetEndDate(2015, 1, 1)
        self.SetCash(100_000)
        self.SetBenchmark("SPY")

        

        self.dow_jones_symbols = ['AXP','AMGN','AAPL','BA','CAT','CSCO','CVX','GS','HD','HON','IBM','INTC','JNJ','KO','JPM','MCD','MMM','MRK','MSFT','NKE','PG','TRV','UNH','CRM','VZ','V','WBA','WMT','DIS','DOW']
        self.dow_jones         = [ Symbol.Create(symbol, SecurityType.Equity, Market.USA) for symbol in self.dow_jones_symbols ]
        
        self.sp500_symbols = ['MMM','AOS','ABT','ABBV','ABMD','ACN','ATVI','ADM','ADBE','ADP','AAP','AES','AFL','A','AIG','APD','AKAM','ALK','ALB','ARE','ALGN','ALLE','LNT','ALL','GOOGL','GOOG','MO','AMZN','AMCR','AMD','AEE','AAL','AEP','AXP','AMT','AWK','AMP','ABC','AME','AMGN','APH','ADI','ANSS','ANTM','AON','APA','AAPL','AMAT','APTV','ANET','AIZ','T','ATO','ADSK','AZO','AVB','AVY','BKR','BLL','BAC','BBWI','BAX','BDX','WRB','BRK.B','BBY','BIO','TECH','BIIB','BLK','BK','BA','BKNG','BWA','BXP','BSX','BMY','AVGO','BR','BRO','BF.B','CHRW','CDNS','CZR','CPB','COF','CAH','KMX','CCL','CARR','CTLT','CAT','CBOE','CBRE','CDW','CE','CNC','CNP','CDAY','CERN','CF','CRL','SCHW','CHTR','CVX','CMG','CB','CHD','CI','CINF','CTAS','CSCO','C','CFG','CTXS','CLX','CME','CMS','KO','CTSH','CL','CMCSA','CMA','CAG','COP','ED','STZ','CEG','COO','CPRT','GLW','CTVA','COST','CTRA','CCI','CSX','CMI','CVS','DHI','DHR','DRI','DVA','DE','DAL','XRAY','DVN','DXCM','FANG','DLR','DFS','DISCA','DISCK','DISH','DIS','DG','DLTR','D','DPZ','DOV','DOW','DTE','DUK','DRE','DD','DXC','EMN','ETN','EBAY','ECL','EIX','EW','EA','EMR','ENPH','ETR','EOG','EPAM','EFX','EQIX','EQR','ESS','EL','ETSY','RE','EVRG','ES','EXC','EXPE','EXPD','EXR','XOM','FFIV','FDS','FAST','FRT','FDX','FITB','FRC','FE','FIS','FISV','FLT','FMC','F','FTNT','FTV','FBHS','FOXA','FOX','BEN','FCX','AJG','GRMN','IT','GE','GNRC','GD','GIS','GPC','GILD','GL','GPN','GM','GS','GWW','HAL','HIG','HAS','HCA','PEAK','HSIC','HSY','HES','HPE','HLT','HOLX','HD','HON','HRL','HST','HWM','HPQ','HUM','HBAN','HII','IEX','IDXX','INFO','ITW','ILMN','INCY','IR','INTC','ICE','IBM','IP','IPG','IFF','INTU','ISRG','IVZ','IPGP','IQV','IRM','JBHT','JKHY','J','JNJ','JCI','JPM','JNPR','K','KEY','KEYS','KMB','KIM','KMI','KLAC','KHC','KR','LHX','LH','LRCX','LW','LVS','LDOS','LEN','LLY','LNC','LIN','LYV','LKQ','LMT','L','LOW','LUMN','LYB','MTB','MRO','MPC','MKTX','MAR','MMC','MLM','MAS','MA','MTCH','MKC','MCD','MCK','MDT','MRK','FB','MET','MTD','MGM','MCHP','MU','MSFT','MAA','MRNA','MHK','TAP','MDLZ','MPWR','MNST','MCO','MS','MOS','MSI','MSCI','NDAQ','NTAP','NFLX','NWL','NEM','NWSA','NWS','NEE','NLSN','NKE','NI','NDSN','NSC','NTRS','NOC','NLOK','NCLH','NRG','NUE','NVDA','NVR','NXPI','ORLY','OXY','ODFL','OMC','OKE','ORCL','OGN','OTIS','PCAR','PKG','PARA','PH','PAYX','PAYC','PYPL','PENN','PNR','PBCT','PEP','PKI','PFE','PM','PSX','PNW','PXD','PNC','POOL','PPG','PPL','PFG','PG','PGR','PLD','PRU','PEG','PTC','PSA','PHM','PVH','QRVO','PWR','QCOM','DGX','RL','RJF','RTX','O','REG','REGN','RF','RSG','RMD','RHI','ROK','ROL','ROP','ROST','RCL','SPGI','CRM','SBAC','SLB','STX','SEE','SRE','NOW','SHW','SBNY','SPG','SWKS','SJM','SNA','SEDG','SO','LUV','SWK','SBUX','STT','STE','SYK','SIVB','SYF','SNPS','SYY','TMUS','TROW','TTWO','TPR','TGT','TEL','TDY','TFX','TER','TSLA','TXN','TXT','TMO','TJX','TSCO','TT','TDG','TRV','TRMB','TFC','TWTR','TYL','TSN','UDR','ULTA','USB','UAA','UA','UNP','UAL','UNH','UPS','URI','UHS','VLO','VTR','VRSN','VRSK','VZ','VRTX','VFC','VTRS','V','VNO','VMC','WAB','WMT','WBA','WM','WAT','WEC','WFC','WELL','WST','WDC','WRK','WY','WHR','WMB','WTW','WYNN','XEL','XYL','YUM','ZBRA','ZBH','ZION','ZTS']        
        self.sp500         = [ Symbol.Create(symbol, SecurityType.Equity, Market.USA) for symbol in self.sp500_symbols ]
        # self.sp500.append(Symbol.Create('SPY', SecurityType.Equity, Market.USA))

        self.sp500_options      = []
        self.sp500_options_dict = {}
        self.call       = None
        self.put        = None
        self.openingBar = None
        
        self.SPY = Symbol.Create("SPY", SecurityType.Equity, Market.USA)

        self.SPY_SMA_50 = self.SMA(self.AddEquity("SPY", RESOLUTION).Symbol, 50)
        self.AutomaticIndicatorWarmUp = True
        
        self._changes       = None
        self.stateData      = { }
        self.symbols_chosen = set()
        self.consolidators = {}
        oneDayConsolidator = TradeBarConsolidator(timedelta(days=1)) # try using minutes=1440 if it doesn't work

        # for symbol in self.sp500:
        #     symbol = Symbol.CreateOption(symbol, Option.)
        #     self.sp500_options

        self.SetSecurityInitializer(lambda x: x.SetDataNormalizationMode(DataNormalizationMode.Raw))
        self.UniverseSettings.Resolution = RESOLUTION

        # this works.
        self.AddUniverseSelection(ManualUniverseSelectionModel(self.sp500))
        
        # Why is our data.OptionsChain empty?
        # Is it because we haven't added our options to the universe, even though we have added them into self.sp500_options_dict?
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

    def StockFilter(self, data: QuantConnect.Python.PythonSlice) -> set:
        result = set()

        if data.HasData:
            for symbol in data.Keys:
                if data.ContainsKey(symbol.Value):
                    bars = data[symbol.Value] # bars = QuantConnect.Data.Market.TradeBar
                    
                    if bars is not None:
                        if self.has_min_price(bars.Close) and self.has_pop(bars.High, bars.Open):
                            result.add(symbol.Value)
        return result
        
        
#########################################################################################################################################

    def OnSecuritiesChanged(self, changes):
        self._changes = changes

        # for security in changes.RemovedSecurities:
        #     #  liquidate securities that have been removed
        #     if security.Invested:
        #         self.Liquidate(security.Symbol)
        #         self.Log("Exit {0} at {1}".format(security.Symbol, security.Close))
                
                
        # https://github.com/QuantConnect/Lean/blob/master/Algorithm.Python/BasicTemplateOptionsConsolidationAlgorithm.py
        for security in changes.AddedSecurities:
            if security.Type == SecurityType.Equity:
                consolidator = TradeBarConsolidator(timedelta(days=1))
                consolidator.DataConsolidated += self.OnTradeBarConsolidated
            else:
                consolidator = QuoteBarConsolidator(timedelta(days=1))
                consolidator.DataConsolidated += self.OnQuoteBarConsolidated
            self.SubscriptionManager.AddConsolidator(security.Symbol, consolidator)
            self.consolidators[security.Symbol] = consolidator
            
        for security in changes.RemovedSecurities:
            consolidator = self.consolidators.pop(security.Symbol)
            self.SubscriptionManager.RemoveConsolidator(security.Symbol, consolidator)
            if security.Type == SecurityType.Equity:
                consolidator.DataConsolidated -= self.OnTradeBarConsolidated
            else:
                consolidator.DataConsolidated -= self.OnQuoteBarConsolidated
        return
    

    # https://www.quantconnect.com/forum/discussion/4594/option-hourly-resolution/p1
    def OnOptionConsolidated(self, consolidated):
        symbol = consolidated.Symbol
        chains = self.CurrentSlice.OptionChains
        # add logic to find symbol in chains
        return
                        

    def OnOrderEvent(self, fill):
        print(f"OnOrderEvent({self.Time}):: {fill}")

    def OnData(self, data: PythonSlice):
        print(f"Current Time: {self.Time}")
        
        
        if self.IsWarmingUp:
            return

        for symbol in self.StockFilter(data):
            self.symbols_chosen.add(symbol)
            
            # if not self.IsMarketOpen(symbol):
            #     return

            # https://www.quantconnect.com/forum/discussion/4594/option-hourly-resolution/p1
            self.Consolidate(optionContractSymbol, timedelta(hours=4), self.OnOptionConsolidated)


            option = self.AddOption(symbol, RESOLUTION)
            print(option)
            
            for i in data.OptionChains:
                print(i)

            if data.OptionChains.GetValue(symbol) is None:
                return
                
            print(f"{symbol}: we finally have an option!")
            
            option = self.AddOption(symbol, RESOLUTION)
            # option.SetFilter(TimeSpan.FromDays(30), TimeSpan.FromDays(60))
            options_chain = data.OptionChains.GetValue(option.Symbol)
            
            if options_chain is None:
                return

            print(options_chain)
            print(type(options_chain))
            
            for x in options_chain:
                print(x)

            
            self.sp500_options_dict[symbol] = option
                

            if not self.Portfolio[symbol].Invested:
                # Let's shoot for 45-60 days expiration

                # chain = data.OptionChains.GetValue(symbol)


                if self.is_long():
                    # Straight calls for longs
                    
                    for kvp in data.OptionChains:
                        if kvp.Key == symbol:
                            options_chain = kvp.Value
                                
                            # we sort the contracts to find at the money (ATM) contract with farthest expiration
                            contracts = sorted(sorted(sorted(options_chain, \
                                key = lambda x: abs(options_chain.Underlying.Price - x.Strike)), \
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

    def OnDataConsolidated(self, bar):
        """On market open, save the opening bar data"""
        if bar.Time.hour == 9 and bar.Time.minute == 30:
            self.openingBar = bar
            

    def OnEndOfAlgorithm(self):
        pprint(str(self.UniverseManager.ActiveSecurities))

        if len(self.symbols_chosen) == 0:
            print(f"No symbols were chosen")
            return

        print("Chosen symbols") # FB, GOOG, FOXA, AAPL, IBM, WM, BAC, AIG

        for symbol in self.symbols_chosen:
            print(symbol)
        return
    
