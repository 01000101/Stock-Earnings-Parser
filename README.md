# Stock-Earnings-Parser
Small utility to collect, parse, and filter upcoming company stock earnings reports

## Getting Started

```bash
  pip install -r requirements.txt
  python ./stock_earnings_parser/main.py \
    --start-date="31/10/2016" \
    --analysts-min=3 \
    --analysts-max=9 \
    --expected-max=2 \
    --expected-min=0.5 \
    --surprise-delta-min=2 \
    --surprise-delta-max=10
```

The result should look like this:

```bash
date: 2016-Oct-31
ARE: http://www.nasdaq.com/earnings/report/are [SKIP]
AWI: http://www.nasdaq.com/earnings/report/awi [OK]
CAH: http://www.nasdaq.com/earnings/report/cah [OK]
DKL: http://www.nasdaq.com/earnings/report/dkl [OK]
DK: http://www.nasdaq.com/earnings/report/dk [SKIP]
ENH: http://www.nasdaq.com/earnings/report/enh [OK]
EURN: http://www.nasdaq.com/earnings/report/eurn [OK]
GGP: http://www.nasdaq.com/earnings/report/ggp [SKIP]
MIC: http://www.nasdaq.com/earnings/report/mic [SKIP]
APTS: http://www.nasdaq.com/earnings/report/apts [SKIP]
PEG: http://www.nasdaq.com/earnings/report/peg [SKIP]
VET: http://www.nasdaq.com/earnings/report/vet [SKIP]
VNO: http://www.nasdaq.com/earnings/report/vno [SKIP]
=========
== AWI ==
=========
{ 'analysts': 3,
  'estimated': 0.74,
  'history': [ { 'actual': 0.56,
                 'expected': 0.51,
                 'quarter': 'Jun2016',
                 'reported': '07/29/2016',
                 'surprise': 9.8}],
  'meta': { 'symbol': 'AWI',
            'url': 'http://www.nasdaq.com/earnings/report/awi'},
  'premarket': True}
```

## Running tests

* Install requirements: ```pip install -r requirements.txt```
* Install test requirements: ```pip install -r requirements_test.txt```
* Run tests: ```pytest tests/```
