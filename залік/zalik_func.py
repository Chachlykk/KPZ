import json
import talib as ta
import numpy as np
from matplotlib import pyplot as plt
from random import uniform, randint, choice
from datetime import datetime
import pandas as pd
from binance import Client


def read_settings(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


def write_settings(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


def calculateMA(type, source, length):
    result = None
    if type == "SMA":
        result = ta.SMA(source, length)
    elif type == "WMA":
        result = ta.WMA(source, length)
    elif type == "HMA":
        result = np.sqrt(
            ta.WMA(source, length / 2) * 2 - ta.WMA(source, length))  # Esempio di come integrare l'Hull Moving Average
    else:
        result = ta.EMA(source, length)
    return result




def get_klines(day_start: str, day_end: str, symb: str, interval: str):
    # get candles
    k_lines = Client().get_historical_klines(
        symbol=symb,
        interval=interval,
        start_str=str(day_start),
        end_str=str(day_end)
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
    return k_lines


def draw_plot(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df['time'], df['close'], label='BTCUSDT price')

    for index, cond in df.iterrows():
        if cond["buy"]:
            plt.scatter(cond["time"], cond["close"], color='green', label='Buy signal', marker='^', s=100)
        elif cond["sell"]:
            plt.scatter(cond["time"], cond["close"], color='red', label='Buy signal', marker='v', s=100)

    plt.title('BTCUSDT price and signals')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.grid(True)
    plt.show()


def create_settings():
    settings_tmp = {}
    settings_tmp["maTypeInput"] = choice(["EMA", "SMA", "WMA", "HMA"])
    settings_tmp["entryConditionType"] = choice(["Crossover", "Above MA"])
    settings_tmp["emaLongTermPeriod"] = randint(50, 700)
    settings_tmp["emaShortTermPeriod"] = randint(5, 100)
    settings_tmp["emaMidTermPeriod"] = randint(10, 500)

    settings_tmp["enableMacdExit"] = choice([True, False])
    if settings_tmp["enableMacdExit"]:
        settings_tmp["timeframeSelection"] = choice(["W", "D"])
        settings_tmp["macdFastLength"] = randint(10, 500)
        settings_tmp["macdSlowLength"] = randint(50, 700)
        settings_tmp["macdSignalSmoothing"] = randint(1, 200)
    else:
        settings_tmp["timeframeSelection"] = "W"
        settings_tmp["macdFastLength"] = 0
        settings_tmp["macdSlowLength"] = 0
        settings_tmp["macdSignalSmoothing"] = 0

    settings_tmp["useTrailingStop"] = choice([True, False])
    if settings_tmp["useTrailingStop"]:
        settings_tmp["trailingStopPercent"] = uniform(0.0001, 0.05)
    else:
        settings_tmp["trailingStopPercent"] = 0.

    settings_tmp["useEMACloseExit"] = choice([True, False])
    settings_tmp["useEMAExit"] = choice([True, False])
    if settings_tmp["useEMACloseExit"] or settings_tmp["useEMAExit"]:
        settings_tmp["emaCloseExitPeriod"] = randint(10, 500)
    else:
        settings_tmp["emaCloseExitPeriod"] = 0
    settings_tmp["use_volatility_filter"] = choice([True, False])
    if settings_tmp["use_volatility_filter"]:
        settings_tmp["atr_periods"] = randint(10, 200)
        settings_tmp["atr_multiplier"] = uniform(0.5, 1.7)
    else:
        settings_tmp["atr_periods"] = 0
        settings_tmp["atr_multiplier"] = 0.
    return settings_tmp


def profit_more(settings, settings_tmp):
    return settings["profit_factor_1"] + settings["profit_factor_2"] + settings["profit_factor_3"] + settings["profit_factor_4"] < \
        settings_tmp["profit_factor_1"] + settings_tmp["profit_factor_2"] + settings_tmp["profit_factor_3"] + settings_tmp["profit_factor_4"]
