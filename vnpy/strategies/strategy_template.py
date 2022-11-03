from vnpy_ctastrategy import (
    CtaTemplate,
    TickData,
    BarData,
    OrderData,
    TradeData,
    StopOrder,
    BarGenerator,
    ArrayManager
)

from vnpy.trader.constant import Interval

# 类的命名注意不能重复
class StrategyDemo(CtaTemplate):
    """该类/策略的具体介绍"""
    author: str = "Leroy"

    # 参数命名区

    # 变量命名区

    parameters: list = [
        # 参数存放区，以字符串的形式
    ]

    variables: list = [
        # 变量存放区，以字符串的形式
    ]

    # 初始化策略类
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        # 父类初始化
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(
            # 调用1min周期的函数
            on_bar=self.on_bar,
            # 分钟的周期数
            window = 5,
            # 代表调用主要交易周期的函数
            on_window_bar=self.on_5min_bar,
            # 代表周期为分钟周期
            interval=Interval.MINUTE
        )

        # K线池，一定要注意括号内的参数为100根 \
        # 这100根不是一分钟的100根，而是主周期的那个5min_bar的100根
        self.am = ArrayManager(100)

        # 创建一些变量
    
    def on_init(self):
        """策略初始化"""
        # 下载数据，注意括号内的参数表示的是天数
        self.load_bar(10)
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
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """合成1minK线后调用的函数"""
        # 将1minK线数据传递给bg合成所需周期的K线
        self.bg.update_bar(bar)
        # 当上面的K线合成之后就会调用自己所需要的方法即下面的on_5min_bar

    # 自己定义的方法，名字可以随意
    def on_5min_bar(self, bar: BarData):
        """合成所需要的周期K线后调用的函数"""
        self.am.update_bar(bar)
        # 判断K线池有没有满
        if not self.am.inited:
            return
        # 撤掉上一轮的所有委托，以便后面发新的委托
        self.cancel_all()


    def on_order(self, order: OrderData):
        """委托出现变化后调用的函数，停止单委托达成交易后会先调用on_stop_order函数再调用本函数"""
        pass

    def on_stop_order(self, stop_order: StopOrder):
        """本地的停止单委托发生变化后调用的函数"""
        pass

    def on_trade(self, trade: TradeData):
        """有成交之后调用的函数，理论上先调用on_order"""
        pass
    
