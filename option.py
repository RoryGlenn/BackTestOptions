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

from clr import AddReference
AddReference("System")
AddReference("QuantConnect.Algorithm")
AddReference("QuantConnect.Common")

from System import *
from QuantConnect import *
from QuantConnect.Algorithm import *
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
        self.SetStartDate(2014, 1, 1)
        self.SetEndDate(2016, 1, 10)
        self.SetCash(100000)

        option = self.AddOption("GOOG")
        self.option_symbol = option.Symbol

        # set our strike/expiry filter for this option chain
        option.SetFilter(-2, +2, timedelta(0), timedelta(180))

        # use the underlying equity as the benchmark
        self.SetBenchmark("GOOG")
        
    def options_filter(self, slice):
        for chain in data.OptionsChains:
            for contract in chain.Value:
                
                # differentiate the call and put options
                call = [x for x in slice.OptionChains if contract.Right == 0]
                put  = [x for x in slice.OptionChains if contract.Right == 1]
                
                # choose ITM contracts
                contracts = [x for x in call if contract.UnderlyingLastPrice - contract.Strike > 0]
                
                # or choose ATM contracts
                contracts = sorted(slice.OptionChains, key = lambda x: abs(slice.OptionChains.Underlying.Price - x.Strike))[0]
                # or choose OTM contracts
                contracts = [x for x in call if call.UnderlyingLastPrice - x.Strike < 0]
                # sort the contracts by their expiration dates
                contracts = sorted(contracts, key = lambda x: x.Expiry, reverse = True)
                return contracts         

    def OnData(self,slice):
        if self.Portfolio.Invested: return

        for kvp in slice.OptionChains:
            if kvp.Key != self.option_symbol: continue
            chain = kvp.Value
            
            # we sort the contracts to find at the money (ATM) contract with farthest expiration
            contracts = sorted(sorted(sorted(chain, \
                key = lambda x: abs(chain.Underlying.Price - x.Strike)), \
                key = lambda x: x.Expiry, reverse=True), \
                key = lambda x: x.Right, reverse=True)

            # ITM
            contracts = sorted(sorted(sorted(chain, \
                # key = lambda x: abs(chain.Underlying.Price - x.Strike)), \
                key = lambda x: abs(x.UnderlyingLastPrice - x.Strike)), \
                key = lambda x: x.Expiry, reverse=True), \
                key = lambda x: x.Right, reverse=True)

            for c in chain:
                # differentiate the call and put options
                call = [x for x in slice.OptionChains if c.Right == 0]
                put = [x for x in slice.OptionChains if c.Right == 1]
                
                # choose ITM contracts
                contracts = [x for x in call if c.UnderlyingLastPrice - c.Strike > 0]
                
                # or choose ATM contracts
                contracts = sorted(slice.OptionChains, key = lambda x: abs(slice.OptionChains.Underlying.Price - x.Strike))[0]
                # or choose OTM contracts
                contracts = [x for x in call if call.UnderlyingLastPrice - x.Strike < 0]
                # sort the contracts by their expiration dates
                contracts = sorted(contracts, key = lambda x:x.Expiry, reverse = True)


            # if found, trade it
            if len(contracts) == 0: continue
            symbol = contracts[0].Symbol
            self.MarketOrder(symbol, 1)
            self.MarketOnCloseOrder(symbol, -1)

    def OnOrderEvent(self, orderEvent):
        self.Log(str(orderEvent))