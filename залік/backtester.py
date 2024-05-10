from zalik_func import *
from strategy import Strategy

df = pd.DataFrame(pd.read_csv("ETHUSDT.csv"))
settings = read_settings("settings.json")
df = Strategy(df, settings).get_result()

# BACKTESTING

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
        trailStopLevel = maxPriceSinceEntry * (1 - settings["trailingStopPercent"])
        if previousStopLevel == 0: previousStopLevel = trailStopLevel
    elif position_size != 0:
        if ((trailStopLevel > previousStopLevel) and (df.at[i, "close"] < previousStopLevel)) \
                or df.at[i, "close"] < position_size * 0.99:
            previousStopLevel = trailStopLevel
            total_loss += trailStopLevel - position_size
            # print(i, ": start:", position_size, " loss: ", trailStopLevel - position_size, "\n")
            position_size = 0
            total_number_of_trades += 1
            continue

        if (df.at[i, "sell"] and (df.at[i, "close"] > position_size)) or (df.at[i, "close"] > position_size * 1.01):
            total_profit += df.at[i, "close"] - position_size
            # print(i, ": start:", position_size, " profit: ", df.at[i, "close"] - position_size, "\n")
            position_size = 0
            number_of_winning_trades += 1
            total_number_of_trades += 1

win_rate = 0 if number_of_winning_trades == 0 or total_number_of_trades == 0 else (
                                                                                          number_of_winning_trades / total_number_of_trades) * 100
profit_factor = 1 if total_profit == 0 or total_loss == 0 else total_profit / abs(total_loss)
print("profit_factor: ", profit_factor, "\n")
print("total_pnl: ", total_profit + total_loss, "\n")
print("win_rate: ", win_rate, "\n")

# draw_plot(df)  # Создаем график
