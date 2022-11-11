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


class KingKeltnerStrategy(CtaTemplate):
    """"""

    author = "用Python的交易员"

    # 初始化天数
    kk_length = 11
    # 通道宽度偏差
    kk_dev = 1.6
    trailing_percent = 0.8 # 移动止损
    # 每次交易的数量
    fixed_size = 1

    # 通道上轨
    kk_up = 0
    # 通道下轨
    kk_down = 0
    intra_trade_high = 0
    intra_trade_low = 0

    # OCO委托买入开仓的委托号
    long_vt_orderids = []
    # OCO委托卖出开仓的委托号
    short_vt_orderids = []
    # 保存委托代码的列表
    vt_orderids = []

    parameters = ["kk_length", "kk_dev", "trailing_percent", "fixed_size"]
    variables = ["kk_up", "kk_down"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar, 5, self.on_5min_bar)
        self.am = ArrayManager()

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.bg.update_bar(bar)

    def on_5min_bar(self, bar: BarData):
        """"""
        # 为保证委托的唯一性，同样要撤销之前尚未成交的委托
        # 先在orderList列表中遍历出orderID
        for orderid in self.vt_orderids:
            # 然后删除掉，以保证清空orderList的目标
            self.cancel_order(orderid)
        self.vt_orderids.clear()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        # 计算KingKeltner通道的上下轨
        self.kk_up, self.kk_down = am.keltner(self.kk_length, self.kk_dev)

        if self.pos == 0:
            # 用最新的5分钟K线数据初始化持仓期的最高点,最低点
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price
            self.send_oco_order(self.kk_up, self.kk_down, self.fixed_size)

        elif self.pos > 0:
            # 调用Max（）函数统计日高点
            # 作用是设置固定百分比的移动止损离场
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.intra_trade_low = bar.low_price

            vt_orderids = self.sell(self.intra_trade_high * (1 - self.trailing_percent / 100),
                                    abs(self.pos), True)
            # 平仓委托也需要缓存到orderList列表中                        
            self.vt_orderids.extend(vt_orderids)

        elif self.pos < 0:
            self.intra_trade_high = bar.high_price
            # 调用Min（）统计出日低点，设置离场点
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)

            vt_orderids = self.cover(self.intra_trade_low * (1 + self.trailing_percent / 100),
                                     abs(self.pos), True)
            # 缓存该委托到orderList列表中
            self.vt_orderids.extend(vt_orderids)
            
        # 发出状态更新事件
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
        if self.pos != 0:
            if self.pos > 0:
                # 多头开仓成交后，撤消空头委托
                for short_orderid in self.short_vt_orderids:
                    self.cancel_order(short_orderid)

            elif self.pos < 0:
                # 空头开仓成交后，撤消多头委托，即遍历buyOrderIDList
                for buy_orderid in self.long_vt_orderids:
                    self.cancel_order(buy_orderid)

            for orderid in (self.long_vt_orderids + self.short_vt_orderids):
                if orderid in self.vt_orderids:
                    self.vt_orderids.remove(orderid)
        # 发出状态更新事件
        self.put_event()

    def send_oco_order(self, buy_price, short_price, volume):
        """
        OCO委托全称是One-Cancels-the-Other Order，意思是二选一委托
        在K线内同时发出止损买单和止损卖单

        OCO(One Cancel Other)委托：
        1. 主要用于实现区间突破入场
        2. 包含两个方向相反的停止单
        3. 一个方向的停止单成交后会立即撤消另一个方向的
        """
        # 发送双边的停止单委托，并记录委托号
        self.long_vt_orderids = self.buy(buy_price, volume, True)
        self.short_vt_orderids = self.short(short_price, volume, True)
        # 将委托号记录到列表中
        self.vt_orderids.extend(self.long_vt_orderids)
        self.vt_orderids.extend(self.short_vt_orderids)

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass
