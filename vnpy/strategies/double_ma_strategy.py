from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)


class DoubleMaStrategy(CtaTemplate):
    author = "用Python的交易员"
    # 参数信息
    fast_window = 10
    slow_window = 20

    # 变量信息
    fast_ma0 = 0.0
    fast_ma1 = 0.0

    slow_ma0 = 0.0
    slow_ma1 = 0.0

    # 1. ui界面显示的信息 2. 在本地存储信息
    parameters = ["fast_window", "slow_window"]
    variables = ["fast_ma0", "fast_ma1", "slow_ma0", "slow_ma1"]
 
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        # 合成器
        self.bg = BarGenerator(self.on_bar)
        # k线池 参考bar线
        # 这里的默认参数 size = 100
        self.am = ArrayManager()

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        # 载入历史数据，参数的单位是天, 这里是10d
        self.load_bar(10)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")
        # 刷新ui界面
        self.put_event()

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

        self.put_event()

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        # 合成1min k线
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """

        am = self.am
        am.update_bar(bar)
        # 如果池子没有满
        if not am.inited:
            return

        # k线池求均值
        fast_ma = am.sma(self.fast_window, array=True)
        self.fast_ma0 = fast_ma[-1]
        self.fast_ma1 = fast_ma[-2]

        slow_ma = am.sma(self.slow_window, array=True)
        self.slow_ma0 = slow_ma[-1]
        self.slow_ma1 = slow_ma[-2]

        cross_over = self.fast_ma0 > self.slow_ma0 and self.fast_ma1 < self.slow_ma1
        cross_below = self.fast_ma0 < self.slow_ma0 and self.fast_ma1 > self.slow_ma1

        if cross_over:
            if self.pos == 0:
                self.buy(bar.close_price, 1)
            elif self.pos < 0:
                # 先平空仓，再买多单 
                # 因为双均线策略是金叉做多，死叉做空, 做空之前要平仓
                self.cover(bar.close_price, 1)
                self.buy(bar.close_price, 1)

        elif cross_below:
            if self.pos == 0:
                self.short(bar.close_price, 1)
            elif self.pos > 0:
                self.sell(bar.close_price, 1)
                self.short(bar.close_price, 1)

        self.put_event()

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass
