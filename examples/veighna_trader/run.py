# flake8: noqa
from vnpy.event import EventEngine

from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp

# 脚本加载数据库 --- begin 1.1--
from datetime import datetime
from typing import List
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import get_database
from vnpy.trader.object import BarData, TickData
# 脚本加载数据库 --- end 1.1--

# 脚本加载TuShare数据服务 --- begin 2.1--
# from vnpy.trader.datafeed import get_datafeed
# from vnpy.trader.object import HistoryRequest
# from vnpy_tushare import tushare_datafeed
# 脚本加载TuShare数据服务 --- end 2.1--

from vnpy.trader.datafeed import get_datafeed
from vnpy.trader.object import HistoryRequest
from vnpy_rqdata import rqdata_datafeed

from vnpy.trader.utility import TRADER_DIR

from vnpy_ctp import CtpGateway
# from vnpy_ctptest import CtptestGateway
# from vnpy_mini import MiniGateway
# from vnpy_femas import FemasGateway
# from vnpy_sopt import SoptGateway
# from vnpy_sec import SecGateway
# from vnpy_uft import UftGateway
# from vnpy_esunny import EsunnyGateway
# from vnpy_xtp import XtpGateway
# from vnpy_tora import ToraStockGateway
# from vnpy_tora import ToraOptionGateway
# from vnpy_comstar import ComstarGateway
# from vnpy_ib import IbGateway
# from vnpy_tap import TapGateway
# from vnpy_da import DaGateway
# from vnpy_rohon import RohonGateway
# from vnpy_tts import TtsGateway
# from vnpy_ost import OstGateway
# from vnpy_hft import GtjaGateway

from vnpy_ctastrategy import CtaStrategyApp
# 加载cta回测研究模块
from vnpy_ctabacktester import CtaBacktesterApp
from vnpy_spreadtrading import SpreadTradingApp
from vnpy_algotrading import AlgoTradingApp
from vnpy_optionmaster import OptionMasterApp
from vnpy_portfoliostrategy import PortfolioStrategyApp
from vnpy_scripttrader import ScriptTraderApp
from vnpy_chartwizard import ChartWizardApp
from vnpy_rpcservice import RpcServiceApp
from vnpy_excelrtd import ExcelRtdApp
from vnpy_datamanager import DataManagerApp
from vnpy_datarecorder import DataRecorderApp
from vnpy_riskmanager import RiskManagerApp
from vnpy_webtrader import WebTraderApp
from vnpy_portfoliomanager import PortfolioManagerApp
from vnpy_paperaccount import PaperAccountApp


def main():
    """"""
    qapp = create_qapp()

    event_engine = EventEngine()

    main_engine = MainEngine(event_engine)

    print(TRADER_DIR)
    main_engine.add_gateway(CtpGateway)
    # main_engine.add_gateway(CtptestGateway)
    # main_engine.add_gateway(MiniGateway)
    # main_engine.add_gateway(FemasGateway)
    # main_engine.add_gateway(SoptGateway)
    # main_engine.add_gateway(SecGateway)    
    # main_engine.add_gateway(UftGateway)
    # main_engine.add_gateway(EsunnyGateway)
    # main_engine.add_gateway(XtpGateway)
    # main_engine.add_gateway(ToraStockGateway)
    # main_engine.add_gateway(ToraOptionGateway)
    # main_engine.add_gateway(OesGateway)
    # main_engine.add_gateway(ComstarGateway)
    # main_engine.add_gateway(IbGateway)
    # main_engine.add_gateway(TapGateway)
    # main_engine.add_gateway(DaGateway)
    # main_engine.add_gateway(RohonGateway)
    # main_engine.add_gateway(TtsGateway)
    # main_engine.add_gateway(OstGateway)
    # main_engine.add_gateway(NhFuturesGateway)
    # main_engine.add_gateway(NhStockGateway)

    main_engine.add_app(PaperAccountApp)
    # 加载CtaStrategy模块
    main_engine.add_app(CtaStrategyApp)
    # 加载cta回测研究模块
    main_engine.add_app(CtaBacktesterApp)
    main_engine.add_app(SpreadTradingApp)
    main_engine.add_app(AlgoTradingApp)
    main_engine.add_app(OptionMasterApp)
    main_engine.add_app(PortfolioStrategyApp)
    main_engine.add_app(ScriptTraderApp)
    main_engine.add_app(ChartWizardApp)
    main_engine.add_app(RpcServiceApp)
    main_engine.add_app(ExcelRtdApp)
    main_engine.add_app(DataManagerApp)
    main_engine.add_app(DataRecorderApp)
    main_engine.add_app(RiskManagerApp)
    main_engine.add_app(WebTraderApp)
    main_engine.add_app(PortfolioManagerApp)
    
    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    
    # 利用rqdata加载数据
    # datafeed = rqdata_datafeed.RqdataDatafeed()
    # datafeed = get_datafeed()
    # # 获取k线级别的历史数据
    # req = HistoryRequest(
    #     # 合约代码（示例 IF2306 股指2306 合约代码，仅用于示范，具体合约代码请根据需求查询数据服务提供商）
    #     # symbol="IF2306",
    #     # symbol="IF1905",
    #     # symbol="cu1905",  #SHFE
    #     symbol="pb1905", #SHFE 600519.SSE 茅台 	300750.SZSE 宁德时代 603019.SSE 中科曙光
    #     # 合约所在交易所
    #     exchange=Exchange.SHFE,
    #     # 历史数据开始时间
    #     start=datetime(2019, 1, 1),
    #     # 历史数据结束时间
    #     end=datetime(2022, 10, 25),
    #     # 数据时间粒度，默认可选分钟级、小时级和日级，具体选择需要结合该数据服务的权限和需求自行选择
    #     interval=Interval.DAILY
    # )

    # #   获取k线历史数据
    # data = datafeed.query_bar_history(req)
    # print(len(data))
    # # 然后将读取到的数据写入数据库中
    # database = get_database()
    # database.save_bar_data(data)

    qapp.exec()
    """
    # 脚本加载TuShare数据服务 --- begin 2.2--
    datafeed = tushare_datafeed.TushareDatafeed()
    # datafeed = get_datafeed()
    # 获取k线级别的历史数据
    # req = HistoryRequest(
    #     # 合约代码（示例 IF2306 股指2306 合约代码，仅用于示范，具体合约代码请根据需求查询数据服务提供商）
    #     symbol="IF2306",
    #     # 合约所在交易所
    #     exchange=Exchange.CFFEX,
    #     # 历史数据开始时间
    #     start=datetime(2022, 1, 1),
    #     # 历史数据结束时间
    #     end=datetime(2022, 10, 25),
    #     # 数据时间粒度，默认可选分钟级、小时级和日级，具体选择需要结合该数据服务的权限和需求自行选择
    #     interval=Interval.DAILY
    # )

    # 因为积分权限不够，无法获取期货数据，改成获取股票日线数据
    req = HistoryRequest(
            # 合约代码（示例 IF2306 股指2306 合约代码，仅用于示范，具体合约代码请根据需求查询数据服务提供商）
            symbol="000002",
            # 合约所在交易所
            exchange=Exchange.SZSE,
            # 历史数据开始时间
            start=datetime(2019, 1, 1),
            # 历史数据结束时间
            end=datetime(2022, 10, 25),
            # 数据时间粒度，默认可选分钟级、小时级和日级，具体选择需要结合该数据服务的权限和需求自行选择
            interval=Interval.DAILY
        )
    # 获取k线历史数据
    data = datafeed.query_bar_history(req)
    # print(type(data))
    # 然后将读取到的数据写入数据库中
    database = get_database()
    database.save_bar_data(data)
    # 脚本加载TuShare数据服务 --- end 2.2--
    """


    """
    # 脚本加载数据库 --- begin 1.2 --
    database = get_database()

    # 配置所需合约的具体参数数据
    # 合约代码，IF2306 为 股指2306 的合约，仅用于示范，具体合约代码请根据需求自行更改
    symbol = "IF2306"

    # 交易所，目标合约的交易所
    exchange = Exchange.CFFEX

    # 历史数据开始时间，精确到日
    start = datetime(2022, 1, 1)

    # 历史数据结束时间，精确到日
    end = datetime(2022, 10, 25)

    # 数据的时间粒度，这里示例采用日级别
    interval = Interval.DAILY
    # 脚本加载数据库 --- end 1.2 --

    # 数据库读取 --- begin 1.3 --
    # 读取数据库中k线数据
    # bar1 = database.load_bar_data(
    #     symbol=symbol,
    #     exchange=exchange,
    #     interval=interval,
    #     start=start,
    #     end=end
    # )

    # # 读取数据库中tick数据
    # tick1 = database.load_tick_data(
    #     symbol=symbol,
    #     exchange=exchange,
    #     start=start,
    #     end=end
    # )

    # 数据库读取 --- end 1.3 --

    # 数据库写入 --- begin 1.4 --
    # 需要存入的k线数据，请自行获取并转换成所需的形式
    # 示例中的bar_data和tick_data均未在示例中展现获取和转换方法
    # 如需以脚本方式写入，请自行参考源码或其他途径，转换成示例中的数据结构
    # bar_data: List[BarData] = None

    # database.save_bar_data(bar_data)

    # # 需要存入的k线数据，请自行获取并转换成所需的形式
    # tick_data: List[TickData] = None

    # # 将tick数据存入数据库
    # database.save_tick_data(tick_data)
    # 数据库写入 --- end 1.4 --
    """
    
if __name__ == "__main__":
    main()
