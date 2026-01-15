import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover


# DATA LOADER
def load_data(path):
    df = pd.read_csv(
        path,
        header=None,
        names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    )

    df['Datetime'] = pd.to_datetime(
        df['Date'] + ' ' + df['Time'],
        format='%Y.%m.%d %H:%M'
    )

    df.set_index('Datetime', inplace=True)
    df.sort_index(inplace=True)

    return df[['Open', 'High', 'Low', 'Close', 'Volume']]


# STRATEGY
class EMATrend(Strategy):
    fast = 20
    slow = 50
    atr_period = 14
    rr = 2.0

    def init(self):
        close = self.data.Close

        self.ema_fast = self.I(
            lambda x: pd.Series(x).ewm(span=self.fast).mean(),
            close
        )
        self.ema_slow = self.I(
            lambda x: pd.Series(x).ewm(span=self.slow).mean(),
            close
        )

        self.atr = self.I(self._atr)

    def _atr(self):
        high = np.asarray(self.data.High)
        low = np.asarray(self.data.Low)
        close = np.asarray(self.data.Close)

        tr = np.zeros(len(close))
        for i in range(1, len(close)):
            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1])
            )

        return pd.Series(tr).rolling(self.atr_period).mean().to_numpy()

    def next(self):
        if np.isnan(self.atr[-1]):
            return

        price = self.data.Close[-1]
        atr = self.atr[-1]

        if not self.position:
            if crossover(self.ema_fast, self.ema_slow):
                self.buy(sl=price - atr, tp=price + atr * self.rr)

            elif crossover(self.ema_slow, self.ema_fast):
                self.sell(sl=price + atr, tp=price - atr * self.rr)


# METRIC EXTRACTION
def extract_metrics(stats, data):
    def safe(key):
        return stats[key] if key in stats.index else None

    metrics = {
        "Sharpe Ratio": safe("Sharpe Ratio"),
        "Sortino Ratio": safe("Sortino Ratio"),
        "Win Rate (%)": safe("Win Rate [%]"),
        "Net Profit (%)": safe("Return [%]"),
        "Maximum Drawdown (%)": safe("Max. Drawdown [%]"),
        "Total Closed Trades": safe("# Trades"),
        "Average Holding Duration": safe("Avg. Trade Duration"),
        "Largest Winning Trade (%)": safe("Best Trade [%]"),
        "Largest Losing Trade (%)": safe("Worst Trade [%]"),
        "Average Trade (%)": safe("Avg. Trade [%]"),
        "Profit Factor": safe("Profit Factor"),
    }

    bh_return = (
        (data.Close.iloc[-1] - data.Close.iloc[0]) / data.Close.iloc[0]
    ) * 100
    metrics["Buy & Hold Return (%)"] = bh_return

    return pd.DataFrame(metrics, index=["Value"]).T


# TRADE COMPLIANCE CHECK
def trade_compliance_check(stats):
    trades = stats._trades.copy()

    # Entry time is when the trade was opened
    trades['EntryDate'] = trades['EntryTime'].dt.date

    trades_per_day = trades.groupby('EntryDate').size()

    max_trades_day = trades_per_day.max()
    avg_trades_day = trades_per_day.mean()

    compliance = max_trades_day <= 100

    print("\n===== TRADE COMPLIANCE CHECK =====")
    print(f"Max trades in a single day : {max_trades_day}")
    print(f"Average trades per day     : {avg_trades_day:.2f}")
    print(f"Complies with ≤100/day     : {compliance}")

    return trades_per_day


# RUN
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python strategy.py data.csv")
        sys.exit(1)

    data = load_data(sys.argv[1])

    bt = Backtest(
        data,
        EMATrend,
        cash=100000,
        commission=lambda size, price: min(2, 0.00002 * size * price),
        exclusive_orders=True
    )

    stats = bt.run()

    metrics_df = extract_metrics(stats, data)
    trade_compliance_check(stats)

    print("\n===== FINAL METRICS =====\n")
    print(metrics_df)

    metrics_df.to_csv("final_metrics.csv")
