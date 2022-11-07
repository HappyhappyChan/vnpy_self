from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    OrderData,
    TradeData,
    StopOrder,
    BarGenerator,
    ArrayManager,
)

from vnpy.trader.constant import Interval
from day_bar_generator import BarGenerator_Daily
from vnpy_ctastrategy.base import StopOrderStatus

# 类的命名注意不能重复
class Donchian_Special(CtaTemplate):
    """1. 唐奇安通道
       2. 日均线判断方向
       3. 自适应出场
    """
    author: str = "Leroy"

    # 参数命名区
    donchian_in_length: int = 20
    donchian_out_length: int = 8 # 最小的出场参数

    daily_length = 10

    fixed_size = 1

    # 变量命名区
    EntryLong_price = 0.0
    # 空单进场
    EntryShort_price = 0.0
    
    Exit_price = 0.0 
    donchian_out_change_length = 0.0 # 出场变化的K线数量

    dailyMA_value = 0.0 #日均线值

    barnum = 0 # 记录持仓后K线数量

    parameters: list = [
        # 参数存放区，以字符串的形式
        "donchian_in_length",
        "donchian_out_length",
        "daily_length",
        "fixed_size"
    ]

    variables: list = [
        # 变量存放区，以字符串的形式
        "EntryLong_price",
        "EntryShort_price",
        "Exit_price",
        "donchian_out_change_length",
        "dailyMA_value"
    ]

    # 初始化策略类
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        # 父类初始化
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg_min = BarGenerator(
            # 调用1min周期的函数
            on_bar=self.on_bar,
            # 分钟的周期数
            window = 20,
            # 代表调用主要交易周期的函数
            on_window_bar=self.on_20min_bar,
            # 代表周期为分钟周期
            interval=Interval.MINUTE
        )

        # K线池，一定要注意括号内的参数为100根 \
        # 这100根不是一分钟的100根，而是主周期的那个5min_bar的100根
        self.am_min = ArrayManager(100)

        self.bg_daily = BarGenerator(
            on_bar=self.on_bar,
            # 分钟的周期数
            window = 1,
            # 代表调用主要交易周期的函数
            on_window_bar=self.on_daily_bar,
            # 代表周期为分钟周期
            interval=Interval.DAILY
        )

        self.am_daily = ArrayManager(20) # 这里的是交易日
        self.buy_price = 0.0
        self.sell_price = 0.0
        self.short_price = 0.0
        self.cover_price = 0.0
        
        # 存放发出去的还没撤单的委托列表
        self.buy_vt_orderids = []
        self.short_vt_orderids = []
        self.sell_vt_orderids = []
        self.cover_vt_orderids = []

        # 创建一些变量
    
    def on_init(self):
        """策略初始化"""
        # 下载数据，注意括号内的参数表示的是天数
        self.load_bar(40) # load_bar 的是自然日
        self.write_log("策略初始化")

    def on_start(self):
        """策略启动"""
        self.write_log("策略启动")
        # 刷新ui界面的内容
        self.put_event()

    def on_stop(self):
        """策略停止"""
        self.write_log("策略停止")
        self.put_event()

    def on_tick(self, tick: TickData):
        """最新tick数据最先调用的函数"""
        # 将tick传递给bg合成1minK线
        self.bg_min.update_tick(tick)
        # self.bg_daily.update_tick(tick) # 这个和上面的bg_min 只用写一个就可以 否则会调用重
        # 因为多周期只需要合成一次1minK线即可

    def on_bar(self, bar: BarData):
        """合成1minK线后调用的函数"""
        # 将1minK线数据传递给bg合成所需周期的K线
        # 因为日线是一个参考周期，一般不做交易，分钟线交易的时候要用到日线 \
        # 如果把分钟线放前面，分钟线用的时候日线还没更新到

        self.bg_daily.update_bar(bar) 
        self.bg_min.update_bar(bar)
        # 当上面的K线合成之后就会调用自己所需要的方法即下面的on_5min_bar
        
        
    def on_daily_bar(self, bar: BarData):
        """日均线计算"""
        self.am_daily.update_bar(bar)
        if not self.am_daily.inited:
            return
        # 计算日均线
        self.dailyMA_value = self.am_daily.sma(self.daily_length)
        self.sync_data()

    # 自己定义的方法，名字可以随意
    def on_20min_bar(self, bar: BarData):
        """合成所需要的周期K线后调用的函数"""
        # 方法2：没有更新的时候就计算出来
        # self.EntryLong_price, self.EntryShort_price = self.am_min.donchian_close(self.donchian_in_length)
        # 判断大周期容器是否装满
        self.am_min.update_bar(bar)
        # 判断K线池有没有满
        if not self.am_min.inited or not self.am_daily.inited:
            return
        # 撤掉上一轮的所有委托，以便后面发新的委托
        # self.cancel_all()

        self.donchian_out_change_length -= 1
        self.donchian_out_change_length = max(self.donchian_out_change_length, self.donchian_out_length) #最小值为 donchian_out_length
        # self.EntryLong_price, self.EntryShort_price = self.am_min.donchian_close(self.donchian_in_length) # 注意返回两个值
        #方法1：
        """1 收盘价问题  2 最新K线问题"""
        up_array, down_array = self.am_min.donchian_close(self.donchian_in_length, True) # 注意返回两个值
        self.EntryLong_price = up_array[-2]
        self.EntryShort_price = down_array[-2]

        """进场"""
        # 这一部分是发送信号的
        if self.pos == 0:
            if bar.close_price > self.EntryLong_price and bar.close_price > self.dailyMA_value:
                self.buy_price = bar.close_price
                self.short_price = 0.0
                self.sell_price = 0.0
                self.cover_price = 0.0

            if bar.close_price < self.EntryShort_price and bar.close_price < self.dailyMA_value:
                self.buy_price = 0.0
                self.short_price = bar.close_price
                self.sell_price = 0.0
                self.cover_price = 0.0
        else:
            up_array_out, down_array_out = self.am_min.donchian_close(self.donchian_out_change_length, True) #计算平仓的高低点
            if self.pos > 0:
                self.Exit_price = down_array_out[-2]
                if bar.close_price < self.Exit_price:
                    self.sell_price = bar.close_price
                    self.cover_price = 0.0
                    self.buy_price = 0.0 #防止他有反手
                    self.short_price = 0.0 
                
                if bar.close_price < self.EntryShort_price and bar.close_price < self.dailyMA_value: #反手
                    self.short_price = bar.close_price

            if self.pos < 0:
                self.Exit_price = up_array_out[-2]
                if bar.close_price > self.Exit_price:
                    self.sell_price = 0.0
                    self.cover_price = bar.close_price
                    self.buy_price = 0.0 #防止他有反手
                    self.short_price = 0.0 

                if bar.close_price > self.EntryLong_price and bar.close_price > self.dailyMA_value:
                    self.buy_price = bar.close_price
        
        # 从这里开始下面是发送委托的以及撤单代码的
        if self.pos == 0:
            if self.buy_price:
                if self.buy_vt_orderids:
                    for orderid in self.buy_vt_orderids:
                        # 如果有的话就跳到 on_stop_order那里 先remove再挂单
                        self.cancel_order(orderid) 
                else:
                    self.buy_vt_orderids = self.buy(self.buy_price, self.fixed_size, True)
                    self.buy_price = 0.0 
            # 开空仓
            if self.short_price:
                if self.short_vt_orderids:
                    for orderid in self.short_vt_orderids:
                        # 如果有的话就跳到 on_stop_order那里 先remove再挂单
                        self.cancel_order(orderid) 
                else:
                    self.short_vt_orderids = self.short(self.short_price, self.fixed_size, True)
                    self.short_price = 0.0 

        elif self.pos > 0:
            if self.sell_price:
                if self.sell_vt_orderids:
                    for orderid in self.sell_vt_orderids:
                        self.cancel_order(orderid)
                else:
                    self.sell_vt_orderids = self.sell(self.sell_price, self.fixed_size, True)
                    self.sell_price = 0.0

            # 判断是否有反手的可能性
            if self.short_price:
                if self.short_vt_orderids:
                    for orderid in self.short_vt_orderids:
                        # 如果有的话就跳到 on_stop_order那里 先remove再挂单
                        self.cancel_order(orderid) 
                else:
                    self.short_vt_orderids = self.short(self.short_price, self.fixed_size, True)
                    self.short_price = 0.0

        elif self.pos < 0:
            if self.cover_price:
                if self.cover_vt_orderids:
                    for orderid in self.cover_vt_orderids:
                        self.cancel_order(orderid)
                else:
                    self.cover_vt_orderids = self.cover(self.cover_price, self.fixed_size, True)
                    self.cover_price = 0.0
            # 反手
            if self.buy_price:
                if self.buy_vt_orderids:
                    for orderid in self.buy_vt_orderids:
                        # 如果有的话就跳到 on_stop_order那里 先remove再挂单
                        self.cancel_order(orderid) 
                else:
                    self.buy_vt_orderids = self.buy(self.buy_price, self.fixed_size, True)
                    self.buy_price = 0.0

        self.sync_data() # 同步数据

    def on_order(self, order: OrderData):
        """委托出现变化后调用的函数，停止单委托达成交易后会先调用on_stop_order函数再调用本函数"""
        pass

    def on_stop_order(self, stop_order: StopOrder):
        """本地的停止单委托发生变化后调用的函数"""
        if stop_order.status == StopOrderStatus.WAITING:
            return
        for orderids in [
            self.buy_vt_orderids,
            self.sell_vt_orderids,
            self.cover_vt_orderids,
            self.short_vt_orderids
        ]:
            if stop_order.stop_orderid in orderids:
                orderids.remove(stop_order.stop_orderid)
        
        if self.pos == 0:
            if self.buy_price:
                self.buy_vt_orderids = self.buy(self.buy_price, self.fixed_size, True)
                self.buy_price = 0.0
            if self.short_price:
                self.short_vt_orderids = self.short(self.short_price, self.fixed_size, True)
                self.short_price = 0.0

        elif self.pos > 0:
            if self.sell_price:
                self.sell_vt_orderids = self.sell(self.sell_price, self.fixed_size, True)
                self.sell_price = 0.0
            if self.short_price: #反手
                self.short_vt_orderids = self.short(self.short_price, self.fixed_size, True)
                self.short_price = 0.0

        elif self.pos < 0:
            if self.cover_price: #先平仓
                self.cover_vt_orderids = self.cover(self.cover_price, self.fixed_size, True)
                self.cover_price = 0.0
            if self.buy_price: #反手
                self.buy_vt_orderids = self.buy(self.buy_price, self.fixed_size, True)
                self.buy_price = 0.0

    def on_trade(self, trade: TradeData):
        """有成交之后调用的函数，理论上先调用on_order"""
        # 有交易的时候是先调用on_trade 再调用 on_20min_bar
        # if self.pos != 0:
        self.donchian_out_change_length = self.donchian_in_length + 1
    
