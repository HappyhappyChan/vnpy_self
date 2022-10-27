from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager
)

class BollChannelStrategy01(CtaTemplate):

    author = "Leroy"

    boll_window = 18
    boll_dev = 3.4
    cci_window = 10 
    atr_window = 30
    sl_multiplier = 5.2 
    fixed_size = 1 

    boll_up = 0 
    boll_down = 0 
    cci_value = 0
    atr_value = 0 

    intra_trade_high = 0  
    intra_trade_low = 0
    long_stop = 0 
    short_stop = 0 
    
    parameters = [
        "boll_window",
        "boll_dev",
        "cci_window",
        "atr_window",
        "sl_multiplier", 
        "fixed_size"
    ]

    variables = [
        "boll_up",
        "boll_down",
        "cci_value",
        "atr_value",
        "intra_trade_high",
        "intra_trade_low",
        "long_stop",
        "short_stop"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar, 15, self.on_15min_bar)
        self.am = ArrayManager()
    
    def on_init(self):
        """
        初始化策略时on_init函数会被调用
        先调用write_log函数输出“策略初始化”日志
        再调用load_bar函数加载历史数据
        调用完on_init函数之后, 策略的inited状态才变为【True】
        """
        self.writelog("策略初始化")
        # 如果是基于Tick数据回测，请在此处调用load_tick函数
        self.load_bar(10)

    def on_start(self):
        """
        启动策略时on_start函数会被调用
        调用write_log函数输出“策略启动”日志
        调用策略的on_start函数启动策略后, trading状态变为【True】
        此时策略才能够发出交易信号
        """
        self.write_log("策略启动")


    def on_stop(self):
        """
        停止策略时on_stop函数会被调用
        调用write_log函数输出“策略停止”日志
        策略的trading状态变为【False】, \
        此时策略就不会发出交易信号了
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        当策略收到最新的Tick数据的行情推送时，on_tick函数会被调用
        通过BarGenerator的update_tick函数把收到的Tick数据推进前面创建的bg实例中以便合成1分钟的K线
        """
        self.bg.update_tick(tick)
    
    def on_bar(self, bar: BarData):
        """
        基于on_bar推进来的K线数据通过BarGenerator合成更长时间周期的K线来交易
        """
        self.bg.update_bar(bar)
    
    def on_15min_bar(self, bar: BarData):
        """
        过15分钟K线数据回报来生成CTA信号
        """

        # 清理未成交的委托
        # 保证策略在当前这15分钟开始时的整个状态是清晰和唯一的
        self.cancel_all()

        # 调用K线时间序列管理模块
        am = self.am
        # 将收到的K线推送进去
        am.update_bar(bar)
        # 没初始化成功就直接返回
        # 如果没有return，就可以开始计算技术指标了
        if not am.inited:
            return

        self.boll_up, self.boll_down = am.boll(self.boll_window, self.boll_dev)
        self.cci_value = am.cci(self.cci_window)
        self.atr_value = am.atr(self.atr_window)

        # 信号计算
        """
        停止单委托（buy/sell)
        设置离场点(short/cover)
        """
        if self.pos == 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price

            if self.cci_value > 0:
                self.buy(self.boll_up, self.fixed_size, True)
            elif self.cci_value < 0:
                self.short(self.boll_down, self.fixed_size, True)

        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.intra_trade_low = bar.low_price

            self.long_stop = self.intra_trade_high - self.atr_value * self.sl_multiplier
            self.sell(self.long_stop, abs(self.pos), True)

        elif self.pos < 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)

            self.short_stop = self.intra_trade_low + self.atr_value * self.sl_multiplier
            self.cover(self.short_stop, abs(self.pos), True)

        # 不要忘记调用put_event()函数
        self.put_event()
    
    def on_trade(self, trade: TradeData):
        """
        收到策略成交回报时on_trade函数会被调用
        """
        self.put_event()
    
    def on_order(self, order: OrderData):
        """
        收到策略委托回报时on_order函数会被调用
        """
        pass

    def on_stop_order(self, stop_order: StopOrder):
        """
        收到策略停止单回报时on_stop_order函数会被调用
        """
        pass

