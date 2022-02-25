# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from AlgorithmImports import *

# from clr import AddReference
# AddReference("System")
# AddReference("QuantConnect.Algorithm")
# AddReference("QuantConnect.Common")

# from System import *
# from QuantConnect import *
# from QuantConnect.Algorithm import *
from datetime import timedelta

### <summary>
### This example demonstrates how to add options for a given underlying equity security.
### It also shows how you can prefilter contracts easily based on strikes and expirations, and how you
### can inspect the option chain to pick a specific option contract to trade.
### </summary>
### <meta name="tag" content="using data" />
### <meta name="tag" content="options" />
### <meta name="tag" content="filter selection" />
class BasicTemplateOptionsAlgorithm(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2015, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)

        option = self.AddOption("GOOG", Resolution.Minute)
        self.option_symbol = option.Symbol

        # set our strike/expiry filter for this option chain
        option.SetFilter(-2, +2, timedelta(0), timedelta(180))

        # use the underlying equity as the benchmark
        self.SetBenchmark("GOOG")

    def OnData(self,slice):
        
        print(f"Current Time: {self.Time}")
        if self.Portfolio.Invested: return

        for kvp in slice.OptionChains:
            if kvp.Key != self.option_symbol: continue
            chain = kvp.Value

            # we sort the contracts to find at the money (ATM) contract with farthest expiration
            contracts = sorted(sorted(sorted(chain, \
                key = lambda x: abs(chain.Underlying.Price - x.Strike)), \
                key = lambda x: x.Expiry, reverse=True), \
                key = lambda x: x.Right, reverse=True)

            # if found, trade it
            if len(contracts) == 0: continue
            symbol = contracts[0].Symbol
            self.MarketOrder(symbol, 1)
            self.MarketOnCloseOrder(symbol, -1)

    # def OnOrderEvent(self, orderEvent):
    #     print(str(orderEvent))