
import pandas as pd
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import threading
import time
from datetime import datetime

# If you want different default values, configure it here.
default_hostname = '127.0.0.1'
default_port = 7497
default_client_id = 1 # can set and use your Master Client ID
timeout_sec = 5

# This is the main app that we'll be using for sync and async functions.
class ibkr_app(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.error_messages = pd.DataFrame(columns=[
            'reqId', 'errorCode', 'errorString'
        ])
        self.next_valid_id = None
        self.current_time = None
        ########################################################################
        # Here, you'll need to change Line 30 to initialize
        # self.historical_data as a dataframe having the column names you
        # want to use. Clearly, you'll want to make sure your colnames match
        # with what you tell the candlestick figure to expect when you create
        # it in your app!
        # I've already done the same general process you need to go through
        # in the self.error_messages instance variable, so you can use that as
        # a guide.
        self.historical_data = pd.DataFrame(
            columns=['date', 'open', 'high', 'low', 'close', 'volume',
                     'bar_count', 'average']
        )
        self.historical_data_end = None
        self.contract_details = None
        self.contract_details_end = None
        self.matching_symbols = None
        self.order_status = pd.DataFrame(
            columns=['orderId', 'status', 'filled', 'remaining', 'avgFillPrice',
                     'permId', 'parentId', 'lastFillPrice', 'clientId',
                     'whyHeld', 'mktCapPrice']
        )

    def error(self, reqId, errorCode, errorString):
        self.error_messages = pd.concat(
            [self.error_messages, pd.DataFrame({
                "reqId": [reqId],
                "errorCode": [errorCode],
                "errorString": [errorString]
            })])

    def managedAccounts(self, accountsList):
        self.managed_accounts = [i for i in accountsList.split(",") if i]

    def nextValidId(self, orderId: int):
        self.next_valid_id = orderId

    def currentTime(self, time:int):
        self.current_time = datetime.fromtimestamp(time)

    def historicalData(self, reqId, bar):

        self.historical_data = pd.concat(
            [
                self.historical_data,
                pd.DataFrame(
                    {
                        'date': [bar.date],
                        'open': [bar.open],
                        'high': [bar.high],
                        'low': [bar.low],
                        'close': [bar.close],
                    }
                )
            ],
            ignore_index=True
        )

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        self.historical_data_end = reqId

    def contractDetailsEnd(self, reqId: int):
        self.contract_details_end = reqId

    def contractDetails(self, reqId:int, contractDetails):
        self.contract_details = pd.DataFrame({
            "con_id": [contractDetails.contract.conId],
            "symbol": [contractDetails.contract.symbol],
            "long_name": [contractDetails.longName],
            "industry": [contractDetails.industry],
            "category": [contractDetails.category],
            "subcategory": [contractDetails.subcategory],
            "sec_type": [contractDetails.contract.secType],
            "stock_type": [contractDetails.stockType],
            "exchange": [contractDetails.contract.exchange],
            "primary_exchange": [contractDetails.contract.primaryExchange],
            "currency": [contractDetails.contract.currency],
            "local_symbol": [contractDetails.contract.localSymbol],
            "market_name": [contractDetails.marketName],
            "min_tick": [contractDetails.minTick],
            "order_types": [contractDetails.orderTypes],
            "valid_exchanges": [contractDetails.validExchanges],
            "price_magnifier": [contractDetails.priceMagnifier],
            "time_zone_id": [contractDetails.timeZoneId],
            "trading_hours": [contractDetails.tradingHours],
            "liquid_hours": [contractDetails.liquidHours]
        })

    def symbolSamples(self, reqId:int, contractDescriptions):
        df = pd.DataFrame(
            columns=[
                'con_id', 'symbol', 'sec_type', 'primary_exchange', 'currency'
            ]
        )
        for contract_description in contractDescriptions:
            df = pd.concat([
                df,
                pd.DataFrame({
                    "con_id": [contract_description.contract.conId],
                    "symbol": [contract_description.contract.symbol],
                    "sec_type": [contract_description.contract.secType],
                    "primary_exchange": [
                        contract_description.contract.primaryExchange
                    ],
                    "currency": [contract_description.contract.currency]
                })
            ],
                ignore_index=True
            )
        self.matching_symbols = df

    def orderStatus(self, orderId, status:str, filled:float,
                    remaining:float, avgFillPrice:float, permId:int,
                    parentId:int, lastFillPrice:float, clientId:int,
                    whyHeld:str, mktCapPrice: float):

        print('order status')
        # print('orderId:' + str(orderId))
        # print('status:' + status)
        # print('filled:' + str(filled))
        # print('remaining:' + str(remaining))
        # print('avgFillPrice:' + str(avgFillPrice))
        # print('permId:' + str(permId))
        # print('parentId:' + str(parentId))
        # print('lastFillPrice:' + str(lastFillPrice))
        # print('clientId:' + str(clientId))
        # print('whyHeld:' + str(69))
        # print('mktCapPrice:' + str(mktCapPrice))

        print(self.order_status)
        print(type(self.order_status))
        self.order_status = pd.concat(
            [
                self.order_status,
                pd.DataFrame({
                    'order_id': [orderId],
                    'status': [status],
                    'filled': [filled],
                    'remaining': [remaining],
                    'avg_fill_price': [avgFillPrice],
                    'perm_id': [permId],
                    'parent_id': [parentId],
                    'last_fill_price': [lastFillPrice],
                    'client_id': [clientId],
                    'why_held': [whyHeld],
                    'mkt_cap_price': [mktCapPrice]
                })
            ],
            ignore_index=True
        )
        self.order_status.drop_duplicates(inplace=True)

    def openOrder(self, orderId, contract, order, orderState):
        print('open order')
        print(contract)
        print(order)
        print(orderState)

    def openOrderEnd(self):
        print('open order end')


def fetch_current_time(hostname=default_hostname,
                       port=default_port, client_id=default_client_id):
    app = ibkr_app()
    app.connect(hostname, int(port), int(client_id))
    start_time = datetime.now()
    while not app.isConnected():
        time.sleep(0.01)
        if (datetime.now() - start_time).seconds > timeout_sec:
            app.disconnect()
            raise Exception(
                "fetch_current_time",
                "timeout",
                "couldn't connect to IBKR"
            )

    def run_loop():
        app.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    start_time = datetime.now()
    while app.next_valid_id is None:
        time.sleep(0.01)
        if (datetime.now() - start_time).seconds > timeout_sec:
            app.disconnect()
            raise Exception(
                "fetch_current_time",
                "timeout",
                "next_valid_id not received"
            )

    app.reqCurrentTime()
    start_time = datetime.now()
    while app.current_time is None:
        time.sleep(0.01)
        if (datetime.now() - start_time).seconds > timeout_sec:
            app.disconnect()
            raise Exception(
                "fetch_current_time",
                "timeout",
                "current_time not received"
            )
    app.disconnect()
    return app.current_time


def fetch_managed_accounts(hostname=default_hostname, port=default_port,
                           client_id=default_client_id):
    app = ibkr_app()
    app.connect(hostname, port, client_id)
    while not app.isConnected():
        time.sleep(0.01)

    def run_loop():
        app.run()
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    while isinstance(app.next_valid_id, type(None)):
        time.sleep(0.01)
    app.disconnect()
    return app.managed_accounts


def fetch_historical_data(contract, endDateTime='', durationStr='30 D',
                          barSizeSetting='1 hour', whatToShow='MIDPOINT',
                          useRTH=True, hostname=default_hostname,
                          port=default_port, client_id=default_client_id):
    app = ibkr_app()
    app.connect(hostname, port, client_id)
    while not app.isConnected():
        time.sleep(0.01)

    def run_loop():
        app.run()
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    while isinstance(app.next_valid_id, type(None)):
        time.sleep(0.01)
    tickerId = app.next_valid_id
    app.reqHistoricalData(
        tickerId, contract, endDateTime, durationStr, barSizeSetting,
        whatToShow, useRTH, formatDate=1, keepUpToDate=False, chartOptions=[])
    while app.historical_data_end != tickerId:
        time.sleep(0.01)
    app.disconnect()
    return app.historical_data


def fetch_contract_details(contract, hostname=default_hostname,
                          port=default_port, client_id=default_client_id):
    app = ibkr_app()
    app.connect(hostname, port, client_id)
    while not app.isConnected():
        time.sleep(0.01)

    def run_loop():
        app.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    while isinstance(app.next_valid_id, type(None)):
        time.sleep(0.01)
    tickerId = app.next_valid_id
    app.reqContractDetails(tickerId, contract)
    while app.contract_details_end != tickerId:
        time.sleep(0.01)
        if len(app.error_messages) != -app.error_messages['reqId'].sum():
            app.disconnect()
            return app.error_messages['errorString'].iloc[-1] + "!!", False
    app.disconnect()
    return app.contract_details, True


def place_order(contract, order, hostname=default_hostname,
                port=default_port, client_id=default_client_id):
    app = ibkr_app()
    app.connect(hostname, port, client_id)
    while not app.isConnected():
        time.sleep(0.01)

    def run_loop():
        app.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    while app.next_valid_id is None:
        time.sleep(0.01)

    app.placeOrder(app.next_valid_id, contract, order)
    while not ('Submitted' in set(app.order_status['status']) or 'Filled' in set(app.order_status['status'])):
        time.sleep(0.25)

    app.disconnect()

    return app.order_status


def fetch_matching_symbols(pattern, hostname=default_hostname,
                           port=default_port, client_id=default_client_id):
    app = ibkr_app()
    app.connect(hostname, int(port), int(client_id))
    start_time = datetime.now()
    while not app.isConnected():
        time.sleep(0.01)
        if (datetime.now() - start_time).seconds > timeout_sec:
            app.disconnect()
            raise Exception(
                "fetch_contract_details",
                "timeout",
                "couldn't connect to IBKR"
            )

    def run_loop():
        app.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    start_time = datetime.now()
    while app.next_valid_id is None:
        time.sleep(0.01)
        if (datetime.now() - start_time).seconds > timeout_sec:
            app.disconnect()
            raise Exception(
                "fetch_contract_details",
                "timeout",
                "next_valid_id not received"
            )

    req_id = app.next_valid_id
    app.reqMatchingSymbols(req_id, pattern)

    start_time = datetime.now()
    while app.matching_symbols is None:
        time.sleep(0.01)
        if (datetime.now() - start_time).seconds > timeout_sec:
            app.disconnect()
            raise Exception(
                "fetch_contract_details",
                "timeout",
                "contract_details not received"
            )

    app.disconnect()

    return app.matching_symbols
