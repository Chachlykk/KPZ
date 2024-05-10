from zalik_func import *

from datetime import datetime, timedelta
from strategy import Strategy
import pandas as pd

settings = read_settings("settings.json")

df1 = pd.DataFrame(pd.read_csv("BTCUSDT.csv"))
df2 = pd.DataFrame(pd.read_csv("BNBUSDT.csv"))
df3 = pd.DataFrame(pd.read_csv("ETHBTC.csv"))
df4 = pd.DataFrame(pd.read_csv("ETHUSDT.csv"))


# OPTIMIZATION

settings_tmp = {}
ind_symbol = 1
while True:
    settings_tmp = create_settings()
    df = df1.copy()

    # BACKTESTING
    while True:
        df = Strategy(df.copy(), settings_tmp).get_result()
        total_loss = 0
        total_profit = 0
        total_pnl = 0
        position_size = 0
        maxPriceSinceEntry = 0
        trailStopLevel = 0
        previousStopLevel = 0
        number_of_winning_trades = 0
        total_number_of_trades = 0
        for i in range(len(df)):
            if position_size == 0 and df.at[i, "buy"]:
                position_size = df.at[i, "close"]
                maxPriceSinceEntry = df.at[i, "high"]
                trailStopLevel = maxPriceSinceEntry * (1 - settings_tmp["trailingStopPercent"])
                if previousStopLevel == 0: previousStopLevel = trailStopLevel
            elif position_size != 0:
                if ((trailStopLevel > previousStopLevel) and (df.at[i, "close"] < previousStopLevel)) \
                        or df.at[i, "close"] < position_size * 0.99:#відхилення на 1% від початкової ціни
                    previousStopLevel = trailStopLevel
                    total_loss += trailStopLevel - position_size
                    # print(i, ": start:", position_size, " loss: ", trailStopLevel - position_size, "\n")
                    position_size = 0
                    total_number_of_trades += 1
                    continue

                if (df.at[i, "sell"] and (df.at[i, "close"] > position_size)) or (
                        df.at[i, "close"] > position_size * 1.01):#відхилення на 1% від початкової ціни
                    total_profit += df.at[i, "close"] - position_size
                    # print(i, ": start:", position_size, " profit: ", df.at[i, "close"] - position_size, "\n")
                    position_size = 0
                    number_of_winning_trades += 1
                    total_number_of_trades += 1

        win_rate = 0 if number_of_winning_trades == 0 or total_number_of_trades == 0 else (
                        number_of_winning_trades / total_number_of_trades) * 100
        profit_factor = 1 if total_profit == 0 or total_loss == 0 else total_profit / abs(total_loss)
        total_pnl = total_profit + total_loss
        if win_rate < 50 or profit_factor < 1.3 or total_pnl < df.at[0, "close"]*0.4:
            ind_symbol = 1
            break
        elif ind_symbol < 4:
            settings_tmp[f"profit_factor_{ind_symbol}"] = profit_factor
            settings_tmp[f"win_rate_{ind_symbol}"] = win_rate
            settings_tmp[f"total_pnl_{ind_symbol}"] = total_pnl
            ind_symbol += 1
            df = globals()[f"df{ind_symbol}"].copy()
        elif ind_symbol == 4:
            settings_tmp[f"profit_factor_{ind_symbol}"] = profit_factor
            settings_tmp[f"win_rate_{ind_symbol}"] = win_rate
            settings_tmp[f"total_pnl_{ind_symbol}"] = total_pnl
            ind_symbol = 1
            if profit_more(settings, settings_tmp):# якщо більший прибут ніж попередній
                print(settings_tmp)
                settings = settings_tmp
                write_settings("settings.json", settings_tmp)
            break

# draw_plot(df)  # Создаем график
