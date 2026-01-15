# quantalytics-gold-trading-strategy
A risk-adjusted EMA–ATR based intraday trading strategy for XAU/USD, developed for Quantalytics (Prometeo 2026, IIT Jodhpur).

# A Risk-Adjusted Trend-Following Strategy for Intraday Gold Trading

This repository contains the implementation and evaluation of a quantitative trading strategy developed for **Quantalytics**, a national-level quantitative research and algorithmic trading competition held as part of **Prometeo 2026 at IIT Jodhpur**.

##  Strategy Overview
The strategy is a trend-following system based on:
- Exponential Moving Average (EMA) crossovers for signal generation
- Average True Range (ATR) for volatility-aware risk management

The primary objective is to maximize **risk-adjusted performance**, with emphasis on Sharpe ratio and drawdown control rather than raw returns.

##  Key Results (XAU/USD, M1)
- Sharpe Ratio: **1.58**
- Sortino Ratio: **2.53**
- Maximum Drawdown: **−3.46%**
- Net Return: **7.30%**
- Maximum Trades per Day: **47** (rule compliant)

##  Risk Management
- Stop-loss: 1×ATR
- Take-profit: 2×ATR
- Single position at a time
- Transaction costs explicitly modeled

## ⚙️ Backtesting Framework
Backtesting and evaluation were performed using the `backtesting.py` library with realistic transaction cost modeling and trade-frequency compliance checks.

