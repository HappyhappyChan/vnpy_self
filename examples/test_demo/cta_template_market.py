from vnpy_ctastrategy.template import CtaTemplate
from typing import Any
from vnpy.trader.constant import Direction, Offset
from vnpy_ctastrategy.base import MarketOrder
from vnpy.trader.utility import virtual
class CtaTemplate_Market(CtaTemplate):
    def __init__(
        self,
        cta_engine: Any,
        strategy_name: str,
        vt_symbol: str,
        setting: dict,
    ):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
    
    def buy_market(
        self,
        price: float,
        volume: float,
        stop: bool = False,
        lock: bool = False,
        net: bool = False
    ) -> list:
        """
        Send buy order to open a long position.
        """
        return self.send_market_order(
            Direction.LONG,
            Offset.OPEN,
            price,
            volume,
            stop,
            lock,
            net
        )

    def sell_market(
        self,
        price: float,
        volume: float,
        stop: bool = False,
        lock: bool = False,
        net: bool = False
    ) -> list:
        """
        Send sell order to close a long position.
        """
        return self.send_market_order(
            Direction.SHORT,
            Offset.CLOSE,
            price,
            volume,
            stop,
            lock,
            net
        )

    def short_market(
        self,
        price: float,
        volume: float,
        stop: bool = False,
        lock: bool = False,
        net: bool = False
    ) -> list:
        """
        Send short order to open as short position.
        """
        return self.send_market_order(
            Direction.SHORT,
            Offset.OPEN,
            price,
            volume,
            stop,
            lock,
            net
        )

    def cover_market(
        self,
        price: float,
        volume: float,
        stop: bool = False,
        lock: bool = False,
        net: bool = False
    ) -> list:
        """
        Send cover order to close a short position.
        """
        return self.send_market_order(
            Direction.LONG,
            Offset.CLOSE,
            price,
            volume,
            stop,
            lock,
            net
        )
    
    def send_market_order(
        self,
        direction: Direction,
        offset: Offset,
        price: float,
        volume: float,
        stop: bool = False,
        lock: bool = False,
        net: bool = False
    ) -> list:
        """
        Send a new order.
        send_market_order 这个东西在 E:\VeighNa _Studio\Lib\site-packages\vnpy_ctastrategy\backtesting.py
        里面没有，所以要自己写在上面代码路径里面
        """
        if self.trading:
            vt_orderids: list = self.cta_engine.send_market_order(
                self, direction, offset, price, volume, stop, lock, net
            )
            return vt_orderids
        else:
            return []
    
    @virtual
    def on_market_bar(self, MarketOrder: MarketOrder):
        """
        Callback of new MarketOrder data update
        """
        pass