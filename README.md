# NVIDIA CEO Forecast

An offline Python forecaster for the 24 Yes-price markets in the make.fun competition. It estimates per-market volatility with robust median absolute deviations, holds the median at the latest price with a slow cross-market sum decay, and emits five ordered quantiles for each of the next 240 minutes.

```sh
MAKEFUN_INPUT_DIR=/input MAKEFUN_OUTPUT_DIR=/output python3 main.py
```

[![make.fun competition](https://make.fun/badge/polymarket-nvidia-ceo-forecast-01)](https://make.fun/bounty/polymarket-nvidia-ceo-forecast-01)

Competition: [polymarket-nvidia-ceo-forecast-01](https://make.fun/bounty/polymarket-nvidia-ceo-forecast-01). Repository name: `nvidia-ceo-forecast`.
