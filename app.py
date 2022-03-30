import dash
import plotly.graph_objects as go
from dash import dcc
from dash import html
from dash import Dash, dash_table
from dash.dependencies import Input, Output, State
from ibapi.contract import Contract
from ibapi.order import Order
from fintech_ibkr import *
import pandas as pd

# Make a Dash app!
app = dash.Dash(__name__)
server = app.server
# Define the layout.
app.layout = html.Div([

    # Section title
    html.H2("Section 1: Fetch & Display exchange rate historical data"),
    html.H3("Select duration string:"),
    html.Div(children=[
        dcc.Input(id="duration-str", type="text", value="10", style={'width': '365px'}),
        dcc.Dropdown(options=[
            {'label': 'Seconds', 'value': 'S'},
            {'label': 'Days', 'value': 'D'},
            {'label': 'Weeks', 'value': 'W'}],
            value="D", id='duration-unit')], style={'width': '365px'}),
    html.H3("Select bar size setting:"),
    html.Div(
        dcc.Dropdown(["1 sec", "5 secs", "15 secs", "30 secs", "1 min", "2 mins", "3 mins",
                      "5 mins", "15 mins", "30 mins", "1 hour", "1 day"], "1 hour", id='bar-size'),
        style={'width': '365px'}),
    html.H3("Select returning data:"),
    html.Div(
        dcc.RadioItems(
            id='all-or-trade', options=[
                {'label': 'return all data', 'value': False},
                {'label': 'return data within regular trading hours', 'value': True}
            ], value=1), style={'width': '400px'}),
    html.H3("Select value for whatToShow:"),
    html.Div(
        dcc.Dropdown(
            ["TRADES", "MIDPOINT", "BID", "ASK", "BID_ASK", "ADJUSTED_LAST",
             "HISTORICAL_VOLATILITY", "OPTION_IMPLIED_VOLATILITY", 'REBATE_RATE',
             'FEE_RATE', "YIELD_BID", "YIELD_ASK", 'YIELD_BID_ASK', 'YIELD_LAST',
             "SCHEDULE"],
            "MIDPOINT",
            id='what-to-show'
        ),
        style={'width': '365px'}
    ),
    html.H3("Select value for endDateTime:"),
    html.Div(
        children=[
            html.P("You may select a specific endDateTime for the call to " + \
                   "fetch_historical_data. If any of the below is left empty, " + \
                   "the current present moment will be used.")
        ],
        style={'width': '365px'}
    ),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Label('Date:'),
                    dcc.DatePickerSingle(id='edt-date')
                ],
                style={
                    # 'display': 'inline-block',
                    'margin-right': '20px',
                }
            ),
            html.Div(
                children=[
                    html.Label('Hour:'),
                    dcc.Dropdown(list(range(24)), id='edt-hour'),
                ],
                style={
                    'display': 'inline-block',
                    'padding-right': '5px'
                }
            ),
            html.Div(
                children=[
                    html.Label('Minute:'),
                    dcc.Dropdown(list(range(60)), id='edt-minute'),
                ],
                style={
                    'display': 'inline-block',
                    'padding-right': '5px'
                }
            ),
            html.Div(
                children=[
                    html.Label('Second:'),
                    dcc.Dropdown(list(range(60)), id='edt-second'),
                ],
                style={'display': 'inline-block'}
            )
        ]
    ),

    html.H3("Enter a currency pair:"),
    html.P(
        children=[
            "See the various currency pairs here: ",
            html.A(
                "currency pairs",
                href='https://www.interactivebrokers.com/en/index.php?f=2222&exch=ibfxpro&showcategories=FX'
            )
        ]
    ),
    # Currency pair text input, within its own div.
    html.Div(
        # The input object itself
        ["Input Currency: ", dcc.Input(
            id='currency-input', value='AUD.CAD', type='text'
        )],
        # Style it so that the submit button appears beside the input.
        style={'display': 'inline-block', 'padding-top': '5px'}
    ),
    # Submit button
    html.Button('Submit', id='submit-button', n_clicks=0),
    # Line break
    html.Br(),
    # Div to hold the initial instructions and the updated info once submit is pressed
    html.Div(id='currency-output', children='Enter a currency code and press submit', style={'color': 'red'}),
    # Div to hold the candlestick graph
    dcc.Loading(
        type="default",
        children=html.Div([dcc.Graph(id='candlestick-graph')])),
    # Another line break
    html.Br(),
    # Section title
    html.H3("Make a Trade:"),
    # Radio items to select buy or sell
    dcc.RadioItems(
        id='buy-or-sell',
        options=[
            {'label': 'BUY', 'value': 'BUY'},
            {'label': 'SELL', 'value': 'SELL'}
        ],
        value='BUY'
    ),
    dcc.RadioItems(
        id='order-type',
        options=[
            {'label': 'MKT', 'value': 'MKT'},
            {'label': 'LMT', 'value': 'LMT'}
        ],
        value='MKT'
    ),
    html.Div(
        ["Trade amount: ", dcc.Input(id='trade-amt', value='1', type='number')], style={'padding-top': '5px'}
    ),
    html.Div(
        # The input object itself
        ["Symbol: ", dcc.Input(id='symbol-input', value='SPY', type='text')], style={'padding-top': '5px'}
    ),
    html.Div(
        ["SecType: ", dcc.Input(id='secType-input', value='STK', type='text')], style={'padding-top': '5px'}
    ),
    html.Div(
        ["Exchange: ", dcc.Input(id='exchange-input', value='ARCA', type='text')], style={'padding-top': '5px'}
    ),
    html.Div(
        ["Currency: ", dcc.Input(id='trade-currency', value='USD', type='text')], style={'padding-top': '5px'}
    ),
    html.Div(
        # The input object itself
        ["Limit Price (optional): ", dcc.Input(id='limit-price', value='0', type='number')],
        style={'padding-top': '5px', 'visibility': 'visible'}
    ),
    html.Div(
        # The input object itself
        ["Primary Exchange (optional): ", dcc.Input(id='primary-exchange', value='', type='text')],
        style={'padding-top': '5px', 'visibility': 'visible'}
    ),
    html.Button('Trade', id='trade-button', n_clicks=0),
    # Div to confirm what trade was made
    html.Div(id='trade-output', style={'color': 'red'}),
    dash_table.DataTable(id='table')

])


def timeReformat(time):
    time = str(time)
    if len(time) != 2:
        time = "0" + time
    return time


# Callback for what to do when submit-button is pressed
@app.callback(
    [  # there's more than one output here, so you have to use square brackets to pass it in as an array.
        Output(component_id='currency-output', component_property='children'),
        Output(component_id='candlestick-graph', component_property='figure')
    ],
    Input('submit-button', 'n_clicks'),
    # The callback function will
    # fire when the submit button's n_clicks changes
    # The currency input's value is passed in as a "State" because if the user is typing and the value changes, then
    #   the callback function won't run. But the callback does run because the submit button was pressed, then the value
    #   of 'currency-input' at the time the button was pressed DOES get passed in.
    [State('currency-input', 'value'), State('what-to-show', 'value'),
     State('edt-date', 'date'), State('edt-hour', 'value'),
     State('edt-minute', 'value'), State('edt-second', 'value'),
     State('duration-str', 'value'), State('duration-unit', 'value'),
     State('bar-size', 'value'), State('all-or-trade', 'value')]
)
def update_candlestick_graph(n_clicks, currency_string, what_to_show,
                             edt_date, edt_hour, edt_minute, edt_second, duration_str,
                             duration_unit, bar_size, all_or_trade):
    # n_clicks doesn't
    # get used, we only include it for the dependency.

    if any([i is None for i in [edt_date, edt_hour, edt_minute, edt_second]]):
        endDateTime = ''
    else:
        date = ''.join(edt_date.split("-"))
        hour = timeReformat(edt_hour)
        minute = timeReformat(edt_minute)
        second = timeReformat(edt_second)
        endDateTime = date + ' ' + hour + ":" + minute + ":" + second
        print(edt_date, edt_hour, edt_minute, edt_second)

    # First things first -- what currency pair history do you want to fetch?
    # Define it as a contract object!
    contract = Contract()
    contract.symbol = currency_string.split(".")[0]
    contract.secType = 'CASH'
    contract.exchange = 'IDEALPRO'  # 'IDEALPRO' is the currency exchange.
    contract.currency = currency_string.split(".")[1]

    contract_details, isSuccess = fetch_contract_details(contract)

    outputString = ""

    if not isSuccess:
        outputString = contract_details
        return outputString, None

    if contract_details['symbol'][0] + '.' + contract_details['currency'][0] != currency_string:
        outputString = "Contract details inconsistent with the input data!!"
        return outputString, None

    ############################################################################
    ############################################################################
    # This block is the one you'll need to work on. UN-comment the code in this
    #   section and alter it to fetch & display your currency data!
    # Make the historical data request.
    # Where indicated below, you need to make a REACTIVE INPUT for each one of
    #   the required inputs for req_historical_data().
    # This resource should help a lot: https://dash.plotly.com/dash-core-components

    # Some default values are provided below to help with your testing.
    # Don't forget -- you'll need to update the signature in this callback
    #   function to include your new vars!
    cph = fetch_historical_data(
        contract=contract,
        endDateTime=endDateTime,
        durationStr=f'{duration_str} {duration_unit}',  # <-- make a reactive input
        barSizeSetting=bar_size,  # <-- make a reactive input
        whatToShow=what_to_show,
        useRTH=all_or_trade  # <-- make a reactive input
    )
    cph['date'] = pd.to_datetime(cph['date'])
    # # Make the candlestick figure
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=cph['date'],
                open=cph['open'],
                high=cph['high'],
                low=cph['low'],
                close=cph['close']
            )
        ]
    )
    # # Give the candlestick figure a title
    fig.update_layout(title=('Exchange Rate: ' + currency_string))
    ############################################################################
    ############################################################################

    ############################################################################
    ############################################################################
    # This block returns a candlestick plot of apple stock prices. You'll need
    # to delete or comment out this block and use your currency prices instead.
    # df = pd.read_csv(
    #     'https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv'
    # )
    # fig = go.Figure(
    #     data=[
    #         go.Candlestick(
    #             x=df['Date'],
    #             open=df['AAPL.Open'],
    #             high=df['AAPL.High'],
    #             low=df['AAPL.Low'],
    #             close=df['AAPL.Close']
    #         )
    #     ]
    # )

    # currency_string = 'default Apple price data fetch'
    ############################################################################
    ############################################################################

    # Return your updated text to currency-output, and the figure to candlestick-graph outputs
    return ('Submitted query for ' + currency_string), fig


# Callback for what to do when trade-button is pressed
@app.callback(
    # We're going to output the result to trade-output
    [Output(component_id='trade-output', component_property='children'),
     Output(component_id='table', component_property='data'),
     Output(component_id='table', component_property='columns')],
    # We only want to run this callback function when the trade-button is pressed
    Input('trade-button', 'n_clicks'),
    # We DON'T want to run this function whenever buy-or-sell, trade-currency, or trade-amt is updated, so we pass those
    #   in as States, not Inputs:
    [State('buy-or-sell', 'value'), State('order-type', 'value'), State('limit-price', 'value'),
     State('symbol-input', 'value'), State('secType-input', 'value'), State('exchange-input', 'value'),
     State('primary-exchange', 'value'), State('trade-currency', 'value'), State('trade-amt', 'value')],
    # We DON'T want to start executing trades just because n_clicks was initialized to 0!!!
    # prevent_initial_call=True
)
# Still don't use n_clicks, but we need the dependency
def trade(n_clicks, action, orderType, lmtPrice, symbol, secType, exchange, primaryExchange, trade_currency, trade_amt):
    localData = pd.read_csv("/Users/rora/Desktop/submitted_order.csv")
    columns = [{"name": i, "id": i} for i in localData.columns]
    data = localData.to_dict('records')

    if n_clicks is 0:
        return None, data, columns

    matching_symbols = fetch_matching_symbols(symbol)

    if not (matching_symbols['symbol'].str.contains(symbol).any() and matching_symbols['sec_type'].str.contains(
            secType).any() and matching_symbols['primary_exchange'].str.contains(exchange).any() and \
            matching_symbols['currency'].str.contains(trade_currency).any()):
        message = "No matching contract found!!"
        return message, data, columns

    contract = Contract()
    contract.symbol = symbol
    contract.secType = secType
    contract.exchange = exchange
    contract.currency = trade_currency

    if primaryExchange != "":
        contract.primaryExchange = primaryExchange

    contract_details, isSuccess = fetch_contract_details(contract)

    if not isSuccess:
        message = contract_details
        return message, data, columns

    if contract_details['symbol'][0] != symbol or contract_details['currency'][0] != trade_currency:
        message = "Contract details inconsistent with the input data!!"
        return message, data, columns

    order = Order()
    order.action = action
    order.orderType = orderType
    order.totalQuantity = trade_amt

    if orderType == 'LMT':
        order.lmtPrice = lmtPrice

    contract_details = fetch_contract_details(contract)[0]
    order_status = place_order(contract, order)
    current_time = fetch_current_time()
    current_time = current_time.strftime("%d/%m/%Y %H:%M:%S")
    last = len(order_status) - 1

    localData = pd.read_csv("/Users/rora/Desktop/submitted_order.csv")
    localData = localData.append({'timestamp': current_time, 'order_id': order_status['order_id'].max(),
                                  'client_id': order_status['client_id'][last], 'perm_id': order_status['perm_id'][last],
                                  'con_id': contract_details['con_id'][0], 'symbol': symbol, 'action': action,
                                  'size': trade_amt, 'order_type': orderType, 'lmt_price': lmtPrice}, ignore_index=True)
    localData.to_csv("/Users/rora/Desktop/submitted_order.csv", index=False)
    # Make the message that we want to send back to trade-output
    message = "Successfully " + action + ' ' + str(trade_amt) + ' share(s) of ' + symbol + "!"

    localData = pd.read_csv("/Users/rora/Desktop/submitted_order.csv")
    columns = [{"name": i, "id": i} for i in localData.columns]
    data = localData.to_dict('records')

    return message, data, columns


# Run it!
if __name__ == '__main__':
    app.run_server(debug=True)
