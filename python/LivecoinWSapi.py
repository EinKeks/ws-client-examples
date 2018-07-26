import websocket
import datetime
import time
import ssl
import LivecoinWSapi_pb2
import hashlib
import hmac

MY_API_KEY = "gJx7Wa7qXkPtmTAaK3ADCtr6m5rCYYMy"
MY_SECRET_KEY = b"8eLps29wsXszNyEhOl9w8dxsOsM2lTzg"

NEED_TOP_ORDERS = 5

ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE}) # python issue with comodo certs
ws.connect("wss://ws.api.livecoin.net/ws/beta")

# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------- Subscription handlers ---------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
orderbooks = []
orderbooksraw = []

def onNewTickers(symbol, events):
    for t in events:
        print ("ticker: %s/%s/%s" % (
            symbol,
            datetime.datetime.fromtimestamp(t / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            str(events)))

def onNewCandles(symbol, interval, events):
    for t in events:
        print ("candles: %s[%s]/%s/%s" % (
            symbol,
            interval,
            datetime.datetime.fromtimestamp(t / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            str(events)))

def onNewTrades(symbol,events):
    for t in events:
        print ("trades: %s/%s/%s" % (
            symbol,
            datetime.datetime.fromtimestamp(t / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            str(events)))

def orderTypeToStr(enumConstant):
    return "bid" if enumConstant == LivecoinWSapi_pb2.BID else "ask"

def printOrderBook(symbol):
    book = orderbooks[symbol]
    for type in ["bids", "asks"]:
        str = type + "raw: "
        for b in sorted(book[type], reverse= (type=="bids")):
            str += ("%f->%f " % (b, book["bids"][b]))
        print (str)


def onNewOrders(symbol, orders, initial=False):
    if (initial):
        orderbooks[symbol] = {"asks":{}, "bids":{}}
    for order in orders:
        type = orderTypeToStr(order.order_type)
        if order.quantity == 0:
            if order.price in orderbooks[symbol][type]:
                del orderbooks[symbol][type][order.price]
        else:
            orderbooksraw[symbol][type][order.price] = (order.quantity,order.timestamp)
    printOrderBook(symbol)

def printOrderBookRaw(symbol):
  book = orderbooksraw[symbol]
  for type in ["bids", "asks"]:
      str = type+"raw: "
      for b in sorted(book[type], key=lambda x: book[type][x][0], reverse=(type == "bids")):
          str += ("%d:%f->%f " % (b, book[type][b][0], book[type][b][1]))
      print (str)

def onNewRawOrders(symbol, orders, initial=False):
    if (initial):
        orderbooksraw[symbol] = {"asks":{}, "bids":{}}
    for order in orders:
        type = orderTypeToStr(order.order_type)
        if order.quantity == 0:
            if order.id in orderbooksraw[symbol][type]:
                del orderbooksraw[symbol][type][order.id]
        else:
            orderbooksraw[symbol][type][order.id] = (order.price,order.quantity,order.timestamp)
    printOrderBookRaw(symbol)


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------- Subscription control methods --------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def sendUnsigned(msgtype, request, token):
    msg = LivecoinWSapi_pb2.WsRequest()
    msg.meta.SetInParent()
    msg.meta.request_type = msgtype
    if token is not None:
        msg.meta.token = token
    msg.msg = request.SerializeToString()
    ws.send_binary(msg.SerializeToString())

def subscribeTicker(symbol, frequency=None, token=None):
    request = LivecoinWSapi_pb2.SubscribeTickerChannelRequest()
    request.currency_pair = symbol
    request.frequency = frequency
    sendUnsigned(LivecoinWSapi_pb2.WsRequestMetaData.SUBSCRIBE_TICKER, request, token)

def unsubscribeTicker(symbol, token=None):
    request = LivecoinWSapi_pb2.UnsubscribeRequest()
    request.currency_pair = symbol
    request.channel_type = LivecoinWSapi_pb2.UnsubscribeRequest.TICKER
    sendUnsigned(LivecoinWSapi_pb2.WsRequestMetaData.UNSUBSCRIBE, request, token)

def subscribeOrderbook(symbol, depth=None, token=None):
    request = LivecoinWSapi_pb2.SubscribeOrderBookChannelRequest()
    request.currency_pair = symbol
    request.depth = depth
    sendUnsigned(LivecoinWSapi_pb2.WsRequestMetaData.SUBSCRIBE_ORDER_BOOK, request, token)

def unsubscribeOrderbook(symbol, token=None):
    request = LivecoinWSapi_pb2.UnsubscribeRequest()
    request.currency_pair = symbol
    request.channel_type = LivecoinWSapi_pb2.UnsubscribeRequest.ORDER_BOOK
    sendUnsigned(LivecoinWSapi_pb2.WsRequestMetaData.UNSUBSCRIBE, request, token)

def subscribeOrderbookRaw(symbol, depth=None, token=None):
    request = LivecoinWSapi_pb2.SubscribeOrderBookRawChannelRequest()
    request.currency_pair = symbol
    request.depth = depth
    sendUnsigned(LivecoinWSapi_pb2.WsRequestMetaData.SUBSCRIBE_ORDER_BOOK_RAW, request, token)

def unsubscribeOrderbookRaw(symbol, token=None):
    request = LivecoinWSapi_pb2.UnsubscribeRequest()
    request.currency_pair = symbol
    request.channel_type = LivecoinWSapi_pb2.UnsubscribeRequest.ORDER_BOOK_RAW
    sendUnsigned(LivecoinWSapi_pb2.WsRequestMetaData.UNSUBSCRIBE, request, token)

def subscribeTrades(symbol, token = None):
    request = LivecoinWSapi_pb2.SubscribeTradeChannelRequest()
    request.currency_pair = symbol
    sendUnsigned(LivecoinWSapi_pb2.WsRequestMetaData.SUBSCRIBE_TRADE, request, token)

def unsubscribeTrades(symbol, token=None):
    request = LivecoinWSapi_pb2.UnsubscribeRequest()
    request.currency_pair = symbol
    request.channel_type = LivecoinWSapi_pb2.UnsubscribeRequest.TRADE
    sendUnsigned(LivecoinWSapi_pb2.WsRequestMetaData.UNSUBSCRIBE, request, token)

def subscribeCandle(symbol, interval, depth, token=None):
    request = LivecoinWSapi_pb2.SubscribeCandleChannelRequest()
    request.currency_pair = symbol
    request.interval = interval
    if depth is not None:
        request.depth = depth
    sendUnsigned(LivecoinWSapi_pb2.WsRequestMetaData.SUBSCRIBE_CANDLE, request, token)

def unsubscribeCandle(symbol, token=None):
    request = LivecoinWSapi_pb2.UnsubscribeRequest()
    request.currency_pair = symbol
    request.channel_type = LivecoinWSapi_pb2.UnsubscribeRequest.CANDLE
    sendUnsigned(LivecoinWSapi_pb2.WsRequestMetaData.UNSUBSCRIBE, request, token)

# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------- Private api ------------- -----------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def sendSigned(msgtype, request, token, ttl):
    msg = LivecoinWSapi_pb2.WsRequest()
    msg.meta.SetInParent()
    msg.meta.request_type = msgtype
    if token is not None:
        msg.meta.token = token
    request.expire_control.SetInParent()
    request.expire_control.now = int(round(time.time() * 1000))
    request.expire_control.ttl = ttl
    msg.msg = request.SerializeToString()
    # now sign message
    msg.meta.sign = hmac.new(MY_SECRET_KEY, msg=msg.msg, digestmod=hashlib.sha256).hexdigest().upper()
    # send it
    ws.send_binary(msg.SerializeToString())


def login(token = None, ttl=10000): # ttl is in milliseconds
    msg = LivecoinWSapi_pb2.LoginRequest()
    msg.api_key = MY_API_KEY
    sendSigned(LivecoinWSapi_pb2.WsRequestMetaData.LOGIN, msg, token, ttl)

def putLimitOrder(symbol, isBuy, amount, price, token = None, ttl=10000): # ttl is in milliseconds
    msg = LivecoinWSapi_pb2.PutLimitOrderRequest()
    msg.currency_pair = symbol
    msg.order_type = LivecoinWSapi_pb2.BID if isBuy else LivecoinWSapi_pb2.ASK
    msg.amount = str(amount)
    msg.price = str(price)
    sendSigned(LivecoinWSapi_pb2.WsRequestMetaData.PUT_LIMIT_ORDER, msg, token, ttl)

def cancelLimitOrder(symbol, id, token = None, ttl=10000): # ttl is in milliseconds
    msg = LivecoinWSapi_pb2.CancelLimitOrderRequest()
    msg.currency_pair = symbol
    msg.id = id
    sendSigned(LivecoinWSapi_pb2.WsRequestMetaData.CANCEL_LIMIT_ORDER, msg, token, ttl)

# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------- Private api handlers ----------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def onSuccessfullLogin(token):
    print("Successfully logged in\n")

def onSuccessfullOrderPut(token, order_id, amount_left):
    print ("We created new order with id %d, quantity left %s" %(order_id, amount_left))

def onSuccessfullOrderCancel(token, order_id, amount_left):
    print ("We cancelled order with id %d, quantity left was %s" % (order_id, amount_left))

# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------- Incoming messages decoder -----------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def handleIn(rawmsg):
    response = LivecoinWSapi_pb2.WsResponse()
    response.ParseFromString(rawmsg)

    token = response.meta.token
    msgtype = response.meta.response_type
    msg = response.msg

    if msgtype == LivecoinWSapi_pb2.WsRequestMetaData.TICKER_CHANNEL_SUBSCRIBED:
        event = LivecoinWSapi_pb2.TickerChannelSubscribedResponse()
        event.ParseFromString(msg)
        onNewTickers(event.currency_pair, event.data)
    elif msgtype == LivecoinWSapi_pb2.WsRequestMetaData.TICKER_NOTIFY:
        event = LivecoinWSapi_pb2.TickerNotification()
        event.ParseFromString(msg)
        onNewTickers(event.currency_pair, event.data)
    elif msgtype == LivecoinWSapi_pb2.WsRequestMetaData.TRADE_CHANNEL_SUBSCRIBED:
        event = LivecoinWSapi_pb2.TradeChannelSubscribedResponse()
        event.ParseFromString(msg)
        onNewTrades(event.currency_pair, msg.data)
    elif msgtype == LivecoinWSapi_pb2.WsRequestMetaData.TRADE_NOTIFY:
        event = LivecoinWSapi_pb2.TradeNotification()
        event.ParseFromString(msg)
        onNewTrades(event.currency_pair, msg.data)
    elif msgtype == LivecoinWSapi_pb2.WsRequestMetaData.CANDLE_CHANNEL_SUBSCRIBED:
        event = LivecoinWSapi_pb2.CandleChannelSubscribedResponse()
        event.ParseFromString(msg)
        onNewCandles(event.currency_pair, event.interval, event.data)
    elif msgtype == LivecoinWSapi_pb2.WsRequestMetaData.CANDLE_NOTIFY:
        event = LivecoinWSapi_pb2.CandleNotification()
        event.ParseFromString(msg)
        onNewCandles(event.currency_pair, event.interval, event.data)
    elif msgtype == LivecoinWSapi_pb2.WsRequestMetaData.ORDER_BOOK_RAW_CHANNEL_SUBSCRIBED:
        event = LivecoinWSapi_pb2.OrderBookRawChannelSubscribedResponse()
        event.ParseFromString(msg)
        onNewRawOrders(event.currency_pair, i.data, initial = True)
    elif msgtype == LivecoinWSapi_pb2.WsRequestMetaData.ORDER_BOOK_RAW_NOTIFY:
        event = LivecoinWSapi_pb2.OrderBookRawNotification()
        event.ParseFromString(msg)
        onNewRawOrders(event.currency_pair, i.data)
    elif msgtype == LivecoinWSapi_pb2.WsRequestMetaData.ORDER_BOOK_CHANNEL_SUBSCRIBED:
        event = LivecoinWSapi_pb2.OrderBookChannelSubscribedResponse()
        event.ParseFromString(msg)
        onNewOrders(event.currency_pair, i.data, initial = True)
    elif msgtype == LivecoinWSapi_pb2.WsRequestMetaData.ORDER_BOOK_NOTIFY:
        event = LivecoinWSapi_pb2.OrderBookNotification()
        event.ParseFromString(msg)
        onNewOrders(event.currency_pair, i.data)
    elif msgtype == LivecoinWSapi_pb2.WsRequestMetaData.UNSUBSCRIBE:
        event = LivecoinWSapi_pb2.OrderBookNotification()
        event.ParseFromString(msg)
        onUnsubscribe(event.channel_type, event.currency_pair)
    elif msgtype == LivecoinWSapi_pb2.WsRequestMetaData.ERROR:
        event = LivecoinWSapi_pb2.ErrorResponse()
        event.ParseFromString(msg)
        onError(token, event.code, event.message)
    elif msgtype == LivecoinWSapi_pb2.WsRequestMetaData.LOGIN_RESPONSE:
        onSuccessfullLogin(token)
    elif msgtype == LivecoinWSapi_pb2.WsRequestMetaData.PUT_LIMIT_ORDER_RESPONSE:
        event = LivecoinWSapi_pb2.PutLimitOrderResponse()
        event.ParseFromString(msg)
        onSuccessfullOrderPut(token, event.order_id, event.amount_left)
    elif msgtype == LivecoinWSapi_pb2.WsRequestMetaData.CANCEL_LIMIT_ORDER_RESPONSE:
        event = LivecoinWSapi_pb2.OrderBookNotification()
        event.ParseFromString(msg)
        onSuccessfullOrderCancel(token, event.order_id, event.amount_left)

# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------- Test commands and subscriptions  ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

#test unsubscription
subscribeTrades('BTC/RUR')
unsubscribeTrades('BTC/RUR')
subscribeOrderbook('BTC/RUR', 1)
unsubscribeOrderbook('BTC/RUR')
subscribeOrderbookRaw('BTC/RUR', 1)
unsubscribeOrderbookRaw('BTC/RUR')
subscribeCandle('BTC/RUR', LivecoinWSapi_pb2.SubscribeCandleChannelRequest.CANDLE_1_MINUTE, 1)
unsubscribeCandle('BTC/RUR')
subscribeTicker('BTC/RUR', 1)
unsubscribeTicker('BTC/RUR')

#test channels
subscribeOrderbookRaw('BTC/USD', NEED_TOP_ORDERS) # only NEED_TOP_ORDERS bids and asks in snapshot
subscribeTicker('BTC/USD', 2) #do not send me tickers too often (only one time in two seconds)
subscribeOrderbook('BTC/USD', NEED_TOP_ORDERS) # only NEED_TOP_ORDERS bids and asks positions in snapshot
subscribeTrades('BTC/USD')
subscribeCandle('BTC/USD', LivecoinWSapi_pb2.SubscribeCandleChannelRequest.CANDLE_1_MINUTE, 10) # and give me 10 last candles

login("LOGIN")

# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------- Main running cycle ------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

startedat = time.time()

while time.time() - startedat < 180: # limit example running time to 3 minutes
    result =  ws.recv()
    if result != "": # not keepalive
        handleIn(result)

ws.close()