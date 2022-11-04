from vnpy.trader.utility import BarGenerator
from typing import Callable
from vnpy.trader.constant import Interval
from vnpy.trader.object import BarData, TickData
from datetime import datetime
class BarGenerator_Daily(BarGenerator):
    """日线合成器"""
    def __init__(
        self,
        on_bar: Callable,
        window: int , 
        on_window_bar: Callable = None,
        interval: Interval = Interval.DAILY
    ):
        super().__init__(on_bar, window, on_window_bar, interval)
        self.daily_bar: BarData = None 

    def update_bar(self, bar: BarData) -> None:
        """将日线周期纳入条件中"""
        if self.interval == Interval.MINUTE:
            self.update_bar_minute_window(bar)
        elif self.interval == Interval.HOUR:
            self.update_bar_hour_window(bar)
        elif self.interval == Interval.DAILY:
            self.update_bar_daily_window(bar)
    
    def update_bar_daily_window(self, bar: BarData) -> None:
        """自定义日线合成的方法"""
        if not self.daily_bar:
            dt: datetime = bar.datetime.replace(second=0, microsecond=0)
            self.daily_bar = BarData(
                symbol=bar.symbol,
                exchange=bar.exchange,
                datetime=dt,
                gateway_name=bar.gateway_name,
                open_price=bar.open_price,
                high_price=bar.high_price,
                low_price=bar.low_price
            )
        else:
            self.daily_bar.high_price = max(
                self.daily_bar.high_price, 
                bar.high_price
            )
            self.daily_bar.low_price = min(
                self.daily_bar.low_price,
                bar.low_price 
            )
        
        self.daily_bar.close_price = bar.close_price
        self.daily_bar.volume += bar.volume
        self.daily_bar.turnover += bar.turnover
        self.daily_bar.open_interest = bar.open_interest

        if bar.datetime.hour == 14 and bar.datetime.minute == 59:
            self.on_window_bar(self.daily_bar)
            self.daily_bar = None

        self.last_bar = bar

# 10:00-10:15 10:30-10:40
class BarGenerator_Miss(BarGenerator):
    """解决20min 30min一根K线消失的问题"""
    def __init__(self, 
        on_bar: Callable,
        window: int = 0,
        on_window_bar: Callable = None,
        interval: Interval = Interval.MINUTE
    ):
        super().__init__(on_bar, window, on_window_bar, interval)
        self.window = window  

    def update_bar_new(self, bar: BarData):
        """自定义方法，在10:14 K线到达时调用回调函数on_window_bar"""
        if self.interval == Interval.MINUTE and bar.datetime.hour == 10 and bar.datetime.minute == 14:
            if self.window == 20 or self.window == 30:
                self.update_bar_minute_window_new(bar)
        else:
            super().update_bar(bar)
    
    def update_bar_minute_window_new(self, bar: BarData):
        """
        10:00-10:14:59 生成1根10:00 的K线
        10:30:00-10:39:59 生成另一根10:30的K线
        """
        self.window_bar.high_price = max(
                self.window_bar.high_price,
                bar.high_price
            )
        self.window_bar.low_price = min(
            self.window_bar.low_price,
            bar.low_price
        )

        self.window_bar.close_price = bar.close_price
        self.window_bar.volume += bar.volume
        self.window_bar.turnover += bar.turnover
        self.window_bar.open_interest = bar.open_interest

        self.on_window_bar(self.window_bar)
        self.window_bar = None

class BarGenerator_Special(BarGenerator):
    """特殊K线的合成方法：7min K线等"""
    def __init__(self, 
        on_bar: Callable,
        window: int = 0, 
        on_window_bar: Callable = None,
        interval: Interval = Interval.MINUTE
    ):
        super().__init__(on_bar,
            window,
            on_window_bar,
            interval
        )
        self.min_count_num: int = 0
    
    def update_bar(self, bar: BarData) -> None:

        self.min_count_num += 1

        if not self.window_bar:
            dt: datetime = bar.datetime.replace(second=0, microsecond=0)
            self.window_bar = BarData(
                symbol=bar.symbol,
                exchange=bar.exchange,
                datetime=dt,
                gateway_name=bar.gateway_name,
                open_price=bar.open_price,
                high_price=bar.high_price,
                low_price=bar.low_price
            )
        # Otherwise, update high/low price into window bar
        else:
            self.window_bar.high_price = max(
                self.window_bar.high_price,
                bar.high_price
            )
            self.window_bar.low_price = min(
                self.window_bar.low_price,
                bar.low_price
            )

        # Update close price/volume/turnover into window bar
        self.window_bar.close_price = bar.close_price
        self.window_bar.volume += bar.volume
        self.window_bar.turnover += bar.turnover
        self.window_bar.open_interest = bar.open_interest

        """
        if not self.min_count_num % self.window:
            self.on_window_bar(self.window_bar)
            self.window_bar = None
            self.min_count_num = 0
        elif bar.datetime.hour == 14 and bar.datetime.minute == 59:
            self.on_window_bar(self.window_bar)
            self.window_bar = None
            self.min_count_num = 0
        """

        # 对上面的代码进行整合
        if (not self.min_count_num % self.window) or (bar.datetime.hour == 14 and bar.datetime.minute == 59):
            self.on_window_bar(self.window_bar)
            self.window_bar = None
            self.min_count_num = 0

        self.last_bar = bar

class BarGenerator_MS(BarGenerator):
    """57s合成K线"""
    def __init__(
        self,
        on_bar: Callable,
        window: int = 0,
        on_window_bar: Callable = None,
        interval: int = Interval.MINUTE
    ):
        super().__init__(
            on_bar,
            window,
            on_window_bar,
            interval
        )
    def update_tick(self, tick: TickData) -> None:
        """
        Update new tick data into generator.
        """
        new_minute: bool = False

        # Filter tick data with 0 last price
        # 过滤流动性不好的合约
        if not tick.last_price:
            return

        # Filter tick data with older timestamp
        if self.last_tick and tick.datetime < self.last_tick.datetime:
            return

        # self.bar初始化是None
        if not self.bar:
            new_minute = True
        elif self.last_tick.datetime.second < 57 and tick.datetime.second >= 57:
            """
            但实际上这是有问题的 
            21.00.00-21.00.57, 21.00.58-21.01.56 但是bar的记录时间是以起始时间记录的，就会导致
            21.00.00有2根K线
            """
            self.bar.datetime = self.bar.datetime.replace(
                second=0, microsecond=0
            )
            self.on_bar(self.bar)

            new_minute = True

        if new_minute:
            self.bar = BarData(
                symbol=tick.symbol,
                exchange=tick.exchange,
                interval=Interval.MINUTE,
                datetime=tick.datetime,
                gateway_name=tick.gateway_name,
                open_price=tick.last_price,
                high_price=tick.last_price,
                low_price=tick.last_price,
                close_price=tick.last_price,
                open_interest=tick.open_interest
            )
        else:
            self.bar.high_price = max(self.bar.high_price, tick.last_price)
            if tick.high_price > self.last_tick.high_price:
                self.bar.high_price = max(self.bar.high_price, tick.high_price)

            self.bar.low_price = min(self.bar.low_price, tick.last_price)
            if tick.low_price < self.last_tick.low_price:
                self.bar.low_price = min(self.bar.low_price, tick.low_price)

            self.bar.close_price = tick.last_price
            # 持仓量
            self.bar.open_interest = tick.open_interest
            self.bar.datetime = tick.datetime

        if self.last_tick:
            # 成交量变化
            volume_change: float = tick.volume - self.last_tick.volume
            self.bar.volume += max(volume_change, 0)

            turnover_change: float = tick.turnover - self.last_tick.turnover
            self.bar.turnover += max(turnover_change, 0)

        self.last_tick = tick   