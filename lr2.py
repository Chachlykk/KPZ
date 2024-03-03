from datetime import datetime, timedelta
from binance.client import Client
import pandas as pd


def get_rsi(asset, periods):
    today = (datetime.now()).strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    k_lines = Client().get_historical_klines(
        symbol=asset,
        interval=Client.KLINE_INTERVAL_1MINUTE,
        start_str=str(yesterday),
        end_str=str(today)
    )

    # get candles
    k_lines = pd.DataFrame(k_lines)[[0, 1, 2, 3, 4, 5]]
    # Преобразование временной метки в формат datetime
    k_lines[0] = k_lines[0].apply(lambda el: datetime.fromtimestamp(el // 1000))

    for index in range(1, 6):
        k_lines[index] = pd.Series(map(float, k_lines[index]))
    k_lines = k_lines.rename(columns={
        0: 'time', 1: 'open', 2: 'high',
        3: 'low', 4: 'close', 5: 'volume'
    })

    # count rsi
    price_diff = k_lines['close'].diff(1)
    gains = price_diff.where(price_diff > 0, 1)
    losses = price_diff.where(price_diff < 0, -1).abs()

    result = pd.DataFrame(k_lines['time'])
    for period in periods:
        # avarage gains and losses
        avg_gain = gains.rolling(window=period + 1, min_periods=1).mean()
        avg_loss = losses.rolling(window=period + 1, min_periods=1).mean()

        #  RS and RSI
        rs_first = avg_gain.iloc[:period] / avg_loss.iloc[:period]
        rsi_first = 100 - (100 / (1 + rs_first))
        rs_rest = avg_gain / avg_loss
        rsi_rest = 100 - (100 / (1 + rs_rest))

        result['RSI' + str(period)] = pd.concat([pd.Series(rsi_first), rsi_rest.reset_index(drop=True)],
                                                ignore_index=True)
    return result


print(get_rsi("BTCUSDT", [14, 27, 100]))
