from datetime import datetime, timedelta
import pandas as pd
import pandas_ta as ta
from matplotlib import pyplot as plt
from binance import Client

from dataclasses import dataclass


@dataclass
class Signal:
    time: pd.Timestamp
    asset: str
    quantity: float
    side: str
    entry: float
    take_profit: float
    stop_loss: float
    result: float


def perfom_backtesting(signals, k_lines: pd.DataFrame):
    results = []
    for signal in signals:
        for ind, candle in list(enumerate(k_lines.iloc))[signals.index(signal):-1]:
            if signal.side == 'sell':
                if candle['low'] <= signal.take_profit:
                    signal.result = signal.entry - signal.take_profit
                elif candle['high'] >= signal.stop_loss:
                    signal.result = signal.entry - signal.stop_loss

            elif signal.side == 'buy':
                if candle['high'] >= signal.take_profit:
                    signal.result = signal.take_profit - signal.entry
                elif candle['low'] <= signal.stop_loss:
                    signal.result = signal.stop_loss - signal.entry

            if signal.result is not None:
                print(signals.index(signal), ": ", "price - ", candle["close"], "; result - ", signal.result,
                      "; signal - ", signal.side)
                results.append(signal)
                break
    return results


def calculate_pnl(trade_list: list[Signal]):
    total_pnl = 0
    for trade in trade_list:
        total_pnl += trade.result
    return total_pnl


def calculate_statistics(trade_list: list[Signal]):
    print("\n\nСтатистика:\n")
    print(f"{calculate_pnl(trade_list)=}")
    print(f"{profit_factor(trade_list)=}")


def profit_factor(trade_list: list[Signal]):
    total_loss = 0
    total_profit = 0
    for trade in trade_list:
        if trade.result > 0:
            total_profit += trade.result
        else:
            total_loss += trade.result
    return total_profit / abs(total_loss)


def create_signals(k_lines):
    """
    count signals with rsi and adx
    """
    signals = []
    for i in range(len(k_lines)):
        signal = "No signal"
        take_profit_price = None
        stop_loss_price = None
        current_price = k_lines.iloc[i]['close']
        if k_lines.iloc[i]['rsi'] > 65 and k_lines.iloc[i]['adx'] > 25:
            signal = 'sell'
        elif k_lines.iloc[i]['rsi'] < 35 and k_lines.iloc[i]['adx'] > 25:
            signal = 'buy'

        if signal == "buy":
            stop_loss_price = round((1 - 0.01) * current_price, 1)
            take_profit_price = round((1 + 0.01) * current_price, 1)
        elif signal == "sell":
            stop_loss_price = round((1 + 0.01) * current_price, 1)
            take_profit_price = round((1 - 0.01) * current_price, 1)

        signals.append(Signal(
            k_lines.iloc[i]['time'],
            'BTCUSDT',
            100,
            signal,
            current_price,
            take_profit_price,
            stop_loss_price,
            None  # Добавили аргумент result
        ))

    return signals


today = (datetime.now()).strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')

# get candles
k_lines = Client().get_historical_klines(
    symbol="BTCUSDT",
    interval=Client.KLINE_INTERVAL_1MINUTE,
    start_str=str(yesterday),
    end_str=str(today)
)

#  перетворення в DataFrame
k_lines = pd.DataFrame(k_lines)[[0, 1, 2, 3, 4]]

k_lines[0] = k_lines[0].apply(lambda el: datetime.fromtimestamp(el // 1000))

for index in range(1, 5):
    k_lines[index] = pd.Series(map(float, k_lines[index]))

k_lines = k_lines.rename(columns={
    0: 'time', 1: 'open', 2: 'high',
    3: 'low', 4: 'close'
})

# Розрахунок індикаторів
rsi_values = ta.rsi(k_lines.get('close'), 28)
adx_values = ta.adx(k_lines.get('high'), k_lines.get('low'), k_lines.get('close'), 28)
indicators = pd.concat([k_lines['time'], k_lines['close'], rsi_values, adx_values['ADX_28']],
                       axis=1)
indicators.columns = ["time", 'close', 'rsi', 'adx']

signals = create_signals(indicators)

results = perfom_backtesting(signals, k_lines)
calculate_statistics(results)
