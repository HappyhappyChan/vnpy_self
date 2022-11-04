from vnpy.trader.utility import BarGenerator
from typing import Callable
from vnpy.trader.constant import Interval
from vnpy.trader.object import BarData
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
