from vnpy_ctastrategy import CtaTemplate
from vnpy_ctastrategy import (
    TickData,
    BarData,
    StopOrder,
    TradeData, 
    OrderData, 
    BarGenerator,
    ArrayManager,
)
class AtrTreeDemo(CtaTemplate):
    
    author = "Leroy"

    # 参数
    # 倍数
    atr_multiple: int = 5
    # K线根数
    atr_par: int = 20
    # 止盈 到时候要/1000
    fixed_pro_tar: int = 100
    # 止损 到时候要/100
    fixed_stop: int = 15 
    # 每天交易次数
    count_control: int = 1

    # 变量
    atr_value: float = 0.0
    up_line: float = 0.0
    mid_line: float = 0.0
    down_line: float = 0.0

    # 止盈线
    pro_tar: float = 0.0
    # 止损线 平仓线
    net_stop: float = 0.0
    # 交易了几回
    count_control_num: int = 0 

    parameters: list = [
        "atr_multiple",
        # K线根数
        "atr_par",
        # 止盈 到时候要/1000
        "fixed_pro_tar",
        # 止损 到时候要/100
        "fixed_stop", 
        # 每天交易次数
        "count_control"
    ]

    variables: list = [
        "atr_value",
        "up_line",
        "mid_line",
        "down_line",
        # 止盈线
        "pro_tar",
        # 止损线 平仓线
        "net_stop",
        # 交易了几回
        "count_control_num"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        # 初始化父类
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar, 5, self.on_5min_bar)
        self.am = ArrayManager()

        self.last_bar: BarData = None

    def on_init(self):
        self.write_log("策略初始化")
        # 下载K线
        self.load_bar(days=10)

    def on_start(self):
        self.write_log("策略启动")
        self.put_event()

    def on_tick(self, tick: TickData):
        # 在回测中基本不会使用该方法
        # self.bg.update_tick(tick)
        pass
    
    def on_bar(self, bar: BarData):
        self.bg.update_bar(bar)


    def on_5min_bar(self, bar: BarData):
        # 更新K线池
        self.am.update_bar(bar)
        # 判断K线池有没有满
        if not self.am.inited:
            return
        
        # 要把之前发的单子都给撤了
        self.cancel_all()

        # 代表14.55.00-14.59.59s这5min的K线
        # 写法1： 
        # if self.last_bar.datetime.hour == 14 and self.last_bar.datetime.minute == 55:
            # pass
        # 写法2：
        if self.last_bar and str(self.last_bar.datetime)[-14:-6] == "14:55:00":
            self.mid_line = bar.open_price
            self.atr_value = self.am.atr(self.atr_par, array=False)
            self.up_line = self.mid_line + self.atr_multiple * self.atr_value
            self.down_line = self.mid_line - self.atr_multiple * self.atr_value
            self.count_control_num = 0
            print(f"""
                mid_line: {self.mid_line}
                atr_value:{self.atr_value}
                时间: {bar.datetime}
                    """)
        if self.pos == 0 and self.count_control_num <= self.count_control:
            if bar.close_price > self.up_line :
                self.buy(bar.close_price, 1)
                # 开仓了才算交易1次 \
                # 但实际上只是发了一个单子，并不一定成交 \
                # 如果去撮合的话，有可能撮合不成功 \
                # 因为是限价单不一定成交，如果是停止单一般都能直接成交 \
                # 所以不建议放在这里 虽然符合逻辑 \
                # 所以换个地方计算次数
                # self.count_control_num += 1
            if bar.close_price < self.down_line :
                self.short(bar.close_price, 1)
        elif self.pos > 0:
            if bar.close_price < self.down_line:
                self.sell(bar.close_price, abs(self.pos))
                if self.count_control_num <= self.count_control:
                    self.short(bar.close_price, 1)
            # 止盈挂单
            # 止盈的时候挂服务器都挂限价单
            # 一般大多时候都会反手，这个时候如果你的单子被这个止盈单给用掉了，反手的话会自动给你锁仓

            if self.pro_tar:
                self.sell(self.pro_tar, abs(self.pos))
            # 止损挂单
            if self.net_stop:
                self.sell(self.net_stop, abs(self.pos), stop=True)

        elif self.pos < 0:
            if bar.close_price > self.up_line:
                self.cover(bar.close_price, abs(self.pos))
                if self.count_control_num <= self.count_control:
                    self.buy(bar.close_price, 1)
            if self.pro_tar:
                self.cover(self.pro_tar, abs(self.pos))
            if self.net_stop:
                self.cover(self.net_stop, abs(self.pos), stop=True)


        self.last_bar = bar


    def on_order(self, order: OrderData):
        """
        """
        pass

    def on_trade(self, trade: TradeData):
        """"""
        # 说明刚才成交的是多单
        if self.pos > 0:
            self.pro_tar = trade.price * (1000 + self.fixed_pro_tar)/100
            self.net_stop = trade.price * (1000 - self.fixed_stop)/1000
            # 当前成交后将成交次数+1
            # 有次数+1 那就要有归0 \
            # 那就在第一根K线收盘价的时候给他归0
            self.count_control_num += 1
        elif self.pos < 0:
            self.pro_tar = trade.price * (1000 - self.fixed_pro_tar)/1000
            self.net_stop = trade.price * (1000 + self.fixed_stop)/1000
            self.count_control_num += 1
        elif self.pos == 0:
            self.pro_tar = 0
            self.net_stop = 0
        self.put_event()
    
    def on_stop_order(self, stop_order: StopOrder):
        """"""
        pass
