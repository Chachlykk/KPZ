from datetime import datetime, timedelta
from binance.client import Client
from pandas import concat
from pandas_ta import rsi, cci, macd, Series, DataFrame


def count_meaning(data):
    """
    Прогнозує ціну
    """
    rsi_meaning = "Ціна падатиме"
    if data["RSI"] > 70:
        rsi_meaning = "Ціна зростатиме"
    elif data["RSI"] > 30:
        rsi_meaning = "Невідомо"

    cci_meaning = "Ціна падатиме"
    if data["CCI"] < -100:
        cci_meaning = "Ціна зростатиме"
    elif data["CCI"] < 100:
        cci_meaning = "Невідомо"

    macd_meaning = "Невідомо"
    if len(data) >= 2:
        if data['MACD'] > data['MACDs'] and data['MACD_prev'] < data['MACDs_prev']:
            macd_meaning = "Ціна зростатиме"

        if data['MACD'] < data['MACDs'] and data['MACD_prev'] > data['MACDs_prev']:
            macd_meaning = "Ціна падатиме"

    meaning = "Невідомо"
    if cci_meaning != "Невідомо": meaning = cci_meaning
    elif rsi_meaning != "Невідомо": meaning = rsi_meaning
    elif macd_meaning != "Невідомо": meaning = macd_meaning

    return meaning


today = (datetime.now()).strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

# get candles
k_lines = Client().get_historical_klines(
    symbol="BTCUSDT",
    interval=Client.KLINE_INTERVAL_1MINUTE,
    start_str=str(yesterday),
    end_str=str(today)
)

#  перетворення в DataFrame
k_lines = DataFrame(k_lines)[[0, 1, 2, 3, 4]]

k_lines[0] = k_lines[0].apply(lambda el: datetime.fromtimestamp(el // 1000))

for index in range(1, 5):
    k_lines[index] = Series(map(float, k_lines[index]))

k_lines = k_lines.rename(columns={
    0: 'time', 1: 'open', 2: 'high',
    3: 'low', 4: 'close'
})

# Розрахунок індикаторів
rsi_values = rsi(k_lines.get('close'))
cci_values = cci(k_lines.get('high'), k_lines.get('low'), k_lines.get('close'))
macd_values = macd(k_lines.get('close'))
results = concat([rsi_values, cci_values, macd_values], axis=1).dropna().reset_index(drop=True)
results.columns = ['RSI', 'CCI', 'MACD', 'MACDh', 'MACDs']

# Прогнозування
results['MACD_prev'] = results['MACD'].shift(1)
results['MACDs_prev'] = results['MACDs'].shift(1)
results["Meaning"] = results.apply(count_meaning, axis=1)


# Запис результатів
results.loc[:, ['RSI', 'CCI', 'MACD', 'MACDs','Meaning']].to_csv('prediction.csv', index=False)
