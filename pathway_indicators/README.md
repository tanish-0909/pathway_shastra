# Trading Signal Pipeline - Refactored

A modular, production-ready trading signal generation system using **Pathway** for real-time data streaming and technical indicator computation.

## Overview

This refactored version of the trading signal pipeline separates concerns into clean, maintainable modules while preserving 100% of the original functionality.

### Structure

```
indicators_refactored/
├── accumulators.py          # Technical indicator accumulators
├── signal_generator.py      # Signal generation logic & utilities
├── main_indicators.py       # Main pipeline orchestration
└── README.md                # This file
```
### Running the Pipeline

```bash
cd indicators_refactored
python main_indicators.py
```


## Module Documentation

### 1. `accumulators.py`

Contains all **Pathway accumulator classes** for computing technical indicators.

#### Indicators Implemented

| Indicator | Class | Window | Description |
|-----------|-------|--------|-------------|
| MACD | `MACDAccumulator` | 12/26/9 | Moving Average Convergence Divergence |
| RSI | `RSIAccumulator` | 14 | Relative Strength Index |
| SMA 20 | `SMA20Accumulator` | 20 | Simple Moving Average |
| SMA 50 | `SMA50Accumulator` | 50 | Simple Moving Average |
| Bollinger Bands | `BollingerBand20Accumulator` | 20, 2σ | Upper/Lower price bands |
| ATR | `ATR14Accumulator` | 14 | Average True Range |
| VWAP | `VWAPAccumulator` | All | Volume Weighted Average Price |
| ADL | `ADLAccumulator` | All | Accumulation/Distribution Line |
| OBV | `OBVAccumulator` | All | On-Balance Volume |
| CMO | `CMOAccumulator` | 14 | Chande Momentum Oscillator |
| CRSI | `CRSIAccumulator` | 3/2 | Composite RSI |
| Klinger | `KlingerAccumulator` | 34/55/13 | Klinger Volume Oscillator |
| Keltner Mid | `KeltnerMidAccumulator` | 20 | Keltner Channel Midline |

