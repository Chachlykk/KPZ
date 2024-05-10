from dataclasses import dataclass
from zalik_func import *
import talib as ta


@dataclass
class Strategy:
    def __init__(self, df, settings):
        self.settings = settings
        self.df = df
        self.position_size: int = 0
        self.use_trailing_stop: bool = False
        self.longTermMA = calculateMA(settings["maTypeInput"], self.df["close"], settings["emaLongTermPeriod"])
        self.shortTermMA = calculateMA(settings["maTypeInput"], self.df["close"], settings["emaShortTermPeriod"])
        self.midTermMA = calculateMA(settings["maTypeInput"], self.df["close"], settings["emaMidTermPeriod"])

    def enter_long(self):
        self.df['buy'] = False
        if self.settings["entryConditionType"] == "Crossover":
            self.df['buy'] = (self.shortTermMA > self.midTermMA) & (self.df["close"] > self.longTermMA)
        elif self.settings["entryConditionType"] == "Above MA":
            self.df['buy'] = (self.shortTermMA > self.midTermMA) & (self.df["close"] > self.longTermMA)
        pass

    def exit_long(self):
        self.df['sell'] = False

        # === MACD Exit ===
        if self.settings["enableMacdExit"]:
            macdLine, signalLine, _ = ta.MACD(self.df["close"], self.settings["macdFastLength"],
                                          self.settings["macdSlowLength"],
                                          self.settings["macdSignalSmoothing"])
            for i in range(1, len(self.df)):
                if macdLine[i] < signalLine[i] and macdLine[i - 1] > signalLine[i - 1]:
                    self.df.at[i, 'sell'] = True

        # === EMA Close Exit ===
        if self.settings["useEMACloseExit"]:
            selectedMA = calculateMA(self.settings["maTypeInput"], self.df["close"], self.settings["emaCloseExitPeriod"])
            for i in range(1, len(self.df)):
                if self.df.at[i, "close"] < selectedMA[i]:
                    self.df.at[i, 'sell'] = True

        # === EMA Cross Exit ===
        if self.settings["useEMAExit"]:
            for i in range(1, len(self.df)):
                if self.shortTermMA[i - 1] > self.midTermMA[i - 1] and self.shortTermMA[i] < \
                        self.midTermMA[i]:
                    self.df.at[i, 'sell'] = True
        pass

    def use_ATR_filter(self):
        atr = ta.ATR(self.df["high"], self.df["low"], self.df["close"], timeperiod=self.settings["atr_periods"])
        atr_threshold = atr * self.settings["atr_multiplier"]
        for i in range(1, len(self.df)):
            self.df.at[i, "buy"] = self.df.at[i, "buy"] and atr[i] > atr_threshold[i - 1]
        pass

    def get_result(self):
        self.enter_long()
        self.exit_long()
        if self.settings["use_volatility_filter"]:
            self.use_ATR_filter()
        return self.df
