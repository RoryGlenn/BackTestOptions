![alt tag](https://raw.githubusercontent.com/QuantConnect/Lean/master/Documentation/logo.white.small.png) 
## LEAN Data Formats / FOREX

QuantConnect hosts FOREX data provided by Oanda and FXCM. The data contains only *Quote* data. You can explore and download FOREX data for free on our website at https://www.quantconnect.com/data/tree/forex/

The data are stored in compressed zip files, each containing a single CSV file.

FOREX data can be used with the following Resolutions:

* Tick
* Second
* Minute
* Hour
* Daily

The markets we currently support are:

* FXCM
* Oanda

### Minute and Second File Format
Second/minute files are located in the market / resolution / symbol folder. 

The ZIP files have the filename format: `YYYYMMDD_quote.zip`. The CSV file contained within has the filename format: `YYYYMMDD_symbol_resolution_quote.csv`

Second/minute quotes format and example data is as follows:

| Time | Bid Open | Bid High | Bid Low | Bid Close | Last Bid Size | Ask Open | Ask High | Ask Low | Ask Close | Last Ask Size |
| ---- | -------- | -------- | ------- | --------- | ------------- | -------- | -------- | ------- | --------- | ------------- |
| 113000 | 55.01 | 55.95 | 54.80 | 55.50 | 18968 | 55.10 | 56 | 54.85 | 55.55 | 2913 |

* Time - Milliseconds since midnight
* Bid Open - Opening price for the best bid
* Bid High - Highest recorded bid price
* Bid Low - Lowest recorded bid price
* Bid Close - Closing price for the best bid
* Last Bid Size - Size of best bid at close
* Ask Open - Opening price for the best ask
* Ask High - Highest recorded ask price
* Ask Low - Lowest recorded ask price
* Ask Close - Closing price for the best ask
* Last Ask Size - Size of best ask at close

### Hour and Daily File Format
Hour/daily files are located in the market / resolution folder.

The ZIP files have the filename format: `symbol.zip`. The CSV file contained within has the filename format: `symbol.csv`

Hour/Daily quotes format and example data is as follows:

| Time | Bid Open | Bid High | Bid Low | Bid Close | Last Bid Size | Ask Open | Ask High | Ask Low | Ask Close | Last Ask Size |
| ---- | -------- | -------- | ------- | --------- | ------------- | -------- | -------- | ------- | --------- | ------------- |
| 20190125 23:00 | 55.01 | 55.95 | 54.80 | 55.50 | 18968 | 55.10 | 56 | 54.85 | 55.55 | 2913 |

* Time - Formatted as `YYYYMMDD HH:mm`
* Bid Open - Opening price for the best bid
* Bid High - Highest recorded bid price
* Bid Low - Lowest recorded bid price
* Bid Close - Closing price for the best bid
* Last Bid Size - Size of best bid at close
* Ask Open - Opening price for the best ask
* Ask High - Highest recorded ask price
* Ask Low - Lowest recorded ask price
* Ask Close - Closing price for the best ask
* Last Ask Size - Size of best ask at close

### Tick File Format
Tick files are located in the market / tick / symbol folder. 

The ZIP files have the filename format: `YYYYMMDD_quote.zip`. The CSV file contained within has the filename format: `YYYYMMDD_symbol_resolution_quote.csv`

Tick quotes format and examlpe data is as follows:

| Time | Bid Price | Ask Price |
| ---- | --------- | --------- |
| 92000 | 10.38 | 10.40 |

* Time - Milliseconds since midnight
* Bid Price - Best bid price
* Ask Price - Best ask price
