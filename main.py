#!/usr/bin/env python3
"""Offline, robust-volatility quantile forecasts for make.fun cases."""

import json
import math
import os
from pathlib import Path

Z = (-1.644854, -0.67449, 0.0, 0.67449, 1.644854)
OUTER_WIDEN = 1.6
SIGMA_MULTIPLIER = 1.5


def median(values):
    ordered = sorted(values)
    n = len(ordered)
    if not n:
        return 0.0
    mid = n // 2
    if n % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def robust_sigma(prices):
    if len(prices) < 10:
        return 0.0025

    def mad_sigma(segment):
        changes = [segment[i] - segment[i - 1] for i in range(1, len(segment))]
        if not changes:
            return 0.0
        center = median(changes)
        return 1.4826 * median([abs(change - center) for change in changes])

    sigma72 = mad_sigma(prices)
    sigma6h = mad_sigma(prices[-361:])
    return min(0.01, max(0.0005, sigma72, sigma6h))


def price6(value):
    value = min(1.0, max(0.0, value))
    return round(value, 6) + 0.0


def forecast(case):
    markets = case["markets"]
    horizon = case["horizon_minutes"]
    lasts = [float(m["prices"][-1]) if m["prices"] else 0.5 for m in markets]
    total = sum(lasts)
    forecasts = []

    for market, x in zip(markets, lasts):
        prices = market["prices"]
        sigma = robust_sigma(prices) if prices else 0.0025
        sigma *= SIGMA_MULTIPLIER
        rows = []
        for h in range(1, horizon + 1):
            spread = sigma * math.sqrt(h)
            factor = 1.0
            if total > 0:
                factor += (0.98 / total - 1.0) * (h / float(horizon))
            median_new = x * factor
            shift = median_new - x
            raw = [x + z * spread * (OUTER_WIDEN if i in (0, 4) else 1.0) + shift
                   for i, z in enumerate(Z)]
            row = []
            running = 0.0
            for value in raw:
                value = price6(value)
                running = max(running, value)
                row.append(running)
            rows.append(row)
        forecasts.append({"id": market["id"], "q": rows})
    return {"forecasts": forecasts}


def main():
    input_dir = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    for input_path in sorted(input_dir.glob("*.in"), key=lambda path: path.name):
        with input_path.open(encoding="utf-8") as source:
            case = json.load(source)
        payload = json.dumps(forecast(case), separators=(",", ":"), allow_nan=False) + "\n"
        (output_dir / (input_path.stem + ".out")).write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    main()
