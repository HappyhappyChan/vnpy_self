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


class AtrRsiStrategy(CtaTemplate):
    """"""

    author = "用Python的交易员"

    atr_length = 22         # 计算ATR指标的窗口数   
    atr_ma_length = 10      # 计算ATR均线的窗口数
    rsi_length = 5          # 计算RSI的窗口数
    rsi_entry = 16          # RSI的开仓信号
    trailing_percent = 0.8  # 百分比移动止损
    fixed_size = 1          # 每次交易的数量

    atr_value = 0
    atr_ma = 0
    rsi_value = 0
    rsi_buy = 0
    rsi_sell = 0
    intra_trade_high = 0
    intra_trade_low = 0

    parameters = [
        "atr_length",
        "atr_ma_length",
        "rsi_length",
        "rsi_entry",
        "trailing_percent",
        "fixed_size"
    ]
    variables = [
        "atr_value",
        "atr_ma",
        "rsi_value",
        "rsi_buy",
        "rsi_sell",
        "intra_trade_high",
        "intra_trade_low"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        # 初始化RSI入场阈值
        self.rsi_buy = 50 + self.rsi_entry
        self.rsi_sell = 50 - self.rsi_entry

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
        self.cancel_all()
        # 保存K线数据
        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return
        # 计算指标数值
        atr_array = am.atr(self.atr_length, array=True)
        self.atr_value = atr_array[-1]
        self.atr_ma = atr_array[-self.atr_ma_length:].mean()
        self.rsi_value = am.rsi(self.rsi_length)

        # 判断是否要进行交易
        
        # 当前无仓位
        if self.pos == 0:
            # 先初始化K线日高点和日低点的值
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price

            # ATR数值上穿其移动平均线，说明行情短期内波动加大
            # 即处于趋势的概率较大，适合CTA开仓
            if self.atr_value > self.atr_ma:
                # 使用RSI指标的趋势行情时，会在超买超卖区钝化特征，作为开仓信号
                if self.rsi_value > self.rsi_buy:
                    # 这里为了保证成交，选择超价5个整指数点下单
                    self.buy(bar.close_price + 5, self.fixed_size)
                elif self.rsi_value < self.rsi_sell:
                    self.short(bar.close_price - 5, self.fixed_size)
        
        # 持有多头仓位
        elif self.pos > 0:
            # 计算多头持有期内的最高价，以及重置最低价
            # 统计当日K线达到的最高点
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.intra_trade_low = bar.low_price

            # 计算多头移动止损
            # 移动止损设置为当K线达到日高点后 \
            # 回落 trailing_percent 时用停止单（Stop Order）进行平仓离场
            long_stop = self.intra_trade_high * \
                (1 - self.trailing_percent / 100)
            
            # 发出本地止损委托
            self.sell(long_stop, abs(self.pos), stop=True)

        # 持有空头仓位
        elif self.pos < 0:
            # min（）函数来统计当日K线达到的最底点
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
            self.intra_trade_high = bar.high_price

            # 移动止损设置为当K线达到日低点后 \
            # 反弹0.8%时用停止单（Stop Order）进行平仓离场。
            short_stop = self.intra_trade_low * \
                (1 + self.trailing_percent / 100)
            self.cover(short_stop, abs(self.pos), stop=True)

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
