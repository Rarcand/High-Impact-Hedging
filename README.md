# High-Impact-Hedging



Algorithm Condiitons
- VIX
- ATR
- Events cannot be too close for high impact news
- high impact news cannot be all day
- Timed Event cannot have another all day high impact event


Co-factor * VIX%
- Find cofactor by getting candlestick movements on CPI/PPI/High impact days
- Multiply by VIX to get a more accurate preddiction of % movement for the high impact news

TP/SL
- set take profits to 80% (rough estimate, needs backtesting) of initial cVIX * ES/MES price on opening day
- set stop losses to 20% (rough estimate, needs backtesting) of initial cVIX * ES/MES price on opening day
