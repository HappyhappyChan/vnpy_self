from vnpy_ctastrategy import CtaTemplate
from typing import Callable, Any
from vnpy.trader.object import TradeData, OrderData, TickData, BarData
from vnpy_ctastrategy.base import StopOrder
from vnpy.trader.utility import BarGenerator, ArrayManager
from vnpy.trader.constant import Interval

class Tree_Line_Demo1(CtaTemplate):

    # 参数
    atr_length:int = 20
    don_length: int = 20
    avg_length: int = 10
    cum_sum_length: int = 20
    over_bought_value: int = 40
    over_sold_value: int = -40
    fixed_size: int = 1

    # 变量
    atr_value: float = 0.0
    up_line: float = 0.0
    down_line: float = 0.0
    mid_line: float = 0.0
    avg_value: float = 0.0
    cum_sum_value: float = 0.0 

    paramters = [
        "atr_length",
        "don_length",
        "avg_length",
        "cum_sum_length",
        "over_bought_value",
        "over_sold_value",
        "fixed_size",
    ]

    variables = [
        "atr_value",
        "up_line",
        "down_line",
        "mid_line",
        "avg_value",
        "cum_sum_value",
    ]

    def __init__(self, cta_engine: Any, strategy_name: str, vt_symbol: str, setting: str):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(
            self.on_bar,
            5,
            self.on_5min_bar,
            Interval.MINUTE)

        self.am = ArrayManager(100)
        self.am_filter = ArrayManager(50) # 过滤后的K线池
        self.up_line_last = 0.0
        self.down_line_last = 0.0
        self.mid_line_last = 0.0

    def on_init(self):
        self.load_bar(10)
        self.write_log("策略初始化")
    
    def on_start(self):

        self.write_log("策略启动")
        self.put_event()
    
    def on_stop(self) -> None:
        self.write_log("策略停止")
        self.put_event()
    
    def on_tick(self, tick: TickData):
        self.bg.update_tick(tick)
    
    def on_bar(self, bar: BarData):
        self.bg.update_bar(bar)

    def on_5min_bar(self, bar: BarData):
        self.am.update_bar(bar)
        if not self.am.inited:
            return
        
        self.atr_value = self.am.atr(self.atr_length)
        if abs(bar.close_price - bar.open_price) >= self.atr_value:
            self.am_filter.update_bar(bar)
        
        if not self.am_filter.inited:
            return

        self.cancel_all()

        # 确定三条线
        self.up_line, self.down_line = self.am_filter.donchian_close(self.don_length)
        self.mid_line = (self.up_line + self.down_line)/2.0

        # 计算均线值
        self.avg_value = self.am_filter.sma(self.avg_length) 

        # 计算累加值
        self.cum_sum_value = self.am_filter.cum_sum(self.cum_sum_length)

        cross_over_mid = False
        cross_under_mid = False
        cross_under_up = False
        cross_over_down = False

        if self.up_line_last:
            if bar.close_price > self.mid_line and self.am.close_array[-2] <= self.mid_line_last:
                cross_over_mid = True
            
            if bar.close_price < self.mid_line and self.am.close_array[-2] >= self.mid_line_last:
                cross_under_mid = True

            if bar.close_price < self.up_line and self.am.close_array[-2] >= self.up_line_last:
                cross_under_up = True
            
            if bar.close_price > self.down_line and self.am.close_array[-2] <= self.down_line_last:
                cross_over_down = True

        # 无仓开仓
        if self.pos == 0:
            if cross_over_mid and bar.close_price > self.avg_value and self.cum_sum_value < self.over_sold_value:
                self.buy(bar.close_price, self.fixed_size, True)
            
            if cross_under_mid and bar.close_price < self.avg_value and self.cum_sum_value > self.over_bought_value:
                self.short(bar.close_price, self.fixed_size, True)
                
        # 要满足开空仓的条件一定要满足下穿中线
        elif self.pos > 0:
            if cross_under_up or bar.close_price < self.down_line:
                self.sell(bar.close_price, abs(self.pos), True)
            # 反手情况
            if cross_under_mid and bar.close_price < self.avg_value and self.cum_sum_value > self.over_bought_value:
                if bar.close_price >= self.down_line and self.am.close_array[-2] <= self.up_line:
                    # 因为如果 < self.down_line 就在上面平仓了 防止大阴线极端情况
                    self.sell(bar.close_price, abs(self.pos), True)
                self.short(bar.close_price, self.fixed_size, True)

        elif self.pos < 0:
            # 需要平仓的话 一个止盈一个止损
            if cross_over_down or bar.close_price > self.down_line:
                self.cover(bar.close_price, abs(self.pos), True)
            # 反手情况
            if cross_over_mid and bar.close_price > self.avg_value and self.cum_sum_value < self.over_sold_value:
                # 极端情况下过滤
                if bar.close_price >= self.down_line and self.am.close_array[-2] <= self.up_line:
                    # 因为如果 < self.down_line 就在上面平仓了 防止大阴线极端情况
                    self.cover(bar.close_price, abs(self.pos), True)
                self.buy(bar.close_price, self.fixed_size, True)

        self.up_line_last = self.up_line
        self.down_line_last = self.down_line
        self.mid_line_last = self.mid_line

    def on_order(self, order: OrderData):
        """委托单发生变化就调用，就是限价单"""
        pass

    def on_stop_order(self, stop_order: StopOrder) -> None:
        """本地触发之后调用，如果这个on_stop_order成交了必然会调用on_order 但是会先调用on_stop_order"""
        pass

    def on_trade(self, trade: TradeData) -> None:
        pass



