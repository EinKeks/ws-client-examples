import websocket
import json
import datetime
import time
import ssl

NEED_TOP_ORDERS = 5

channels = dict()
orderbooks = dict()
orderbooksraw = dict()
ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE}) # python issue with comodo certs
ws.connect("wss://ws.api.livecoin.net/ws/beta")

def onNewTicker(symbol, last, high, low, volume, vwap, maxBid, minAsk, bestBid, bestAsk):
  #here you can make your trade decision
  print ("ticker: %s/%f/%f/%f/%f/%f/%f/%f/%f/%f" % (symbol, last, high, low, volume, vwap, maxBid, minAsk, bestBid, bestAsk))

def onNewTrade(symbol, id, timestamp, price, quantity):
  print ("trade: %s, id=%d time=%s type=%s price=%f quantity=%f" % (
    symbol,
    id,
    datetime.datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S'),
    "BUY" if price>0 else "SELL",
    abs(price),
    quantity
  ))
  # here you can make your trade decision

def printOrderBook(symbol):
  book = orderbooks[symbol]
  str = "bids: "
  for b in sorted(book["bids"], reverse=True):
    str += ("%f->%f " % (b, book["bids"][b]))
  print (str)
  str = "asks: "
  for b in sorted(book["asks"]):
    str += ("%f->%f" % (b, book["asks"][b]))
  print (str)


def onOrderbookChange(symbol, price, quantity, initial=False):
  if price > 0:
    if quantity == 0:
      if price in orderbooks[symbol]["bids"]:
        del orderbooks[symbol]["bids"][price]
    else:
      orderbooks[symbol]["bids"][price] = quantity
  else:
    if quantity == 0:
      if abs(price) in orderbooks[symbol]["asks"]:
        del orderbooks[symbol]["asks"][abs(price)]
    else:
      orderbooks[symbol]["asks"][abs(price)] = quantity
  printOrderBook(symbol)
  #todo: check if top ask <= orderbooks[symbol]["lastknownask"], reload orderbook (Unsubscribe && Subscribe)
  #todo: check if top bid >= orderbooks[symbol]["lastknownbid"], reload orderbook (Unsubscribe && Subscribe)
  # here you can make your trade decision

def printOrderBookRaw(symbol):
  book = orderbooksraw[symbol]
  str = "bidsraw: "
  for b in sorted(book["bids"], key=lambda x: book["bids"][x][0], reverse=True):
    str += ("%d:%f->%f " % (b, book["bids"][b][0], book["bids"][b][1]))
  print (str)
  str = "asksraw: "
  for b in sorted(book["asks"], key=lambda x: book["asks"][x][0]):
    str += ("%d:%f->%f" % (b, book["asks"][b][0], book["asks"][b][1]))
  print (str)

def onOrderbookRawChange(symbol, id, price, quantity, initial=False):
  if price > 0:
    if quantity == 0:
      if id in orderbooksraw[symbol]["bids"]:
        del orderbooksraw[symbol]["bids"][id]
    else:
      orderbooksraw[symbol]["bids"][id] = (price,quantity)
  else:
    if quantity == 0:
      if id in orderbooksraw[symbol]["asks"]:
        del orderbooksraw[symbol]["asks"][id]
    else:
      orderbooksraw[symbol]["asks"][id] = (abs(price), quantity)
  printOrderBookRaw(symbol)
  # todo: check if !initial && top ask <= orderbooksraw[symbol]["lastknownask"], reload orderbook (Unsubscribe && Subscribe)
  # todo: check if !initial && top bid >= orderbooksraw[symbol]["lastknownbid"], reload orderbook (Unsubscribe && Subscribe)
  # here you can make your trade decision


def subscribe(type, symbol, options):
  msg = {"Subscribe": {"channelType": type, "symbol": symbol}}
  for opt in options:
    msg["Subscribe"][opt] = options[opt]
  ws.send(json.dumps(msg))

def unsubscribe(type, symbol):
  for c in channels:
    if channels[c][0] == symbol and channels[c][1] == type:
      msg = {"Unsubscribe": {"channelId": c}}
      ws.send(json.dumps(msg))

def subscribeTicker(symbol, frequency=None):
  subscribe("ticker", symbol, {} if (frequency == None) else {"frequency":frequency})

def unsubscribeTicker(symbol):
  unsubscribe("ticker", symbol)

def subscribeOrderbook(symbol, depth=None):
  subscribe("orderbook", symbol, {} if (depth == None) else {"depth": depth})

def unsubscribeOrderbook(symbol):
  unsubscribe("orderbook", symbol)

def subscribeOrderbookRaw(symbol, depth=None):
  subscribe("orderbookraw", symbol, {} if (depth == None) else {"depth": depth})

def unsubscribeOrderbookRaw(symbol):
  unsubscribe("orderbookraw", symbol)

def subscribeTrades(symbol):
  subscribe("trade", symbol, {})

def unsubscribeTrades(symbol):
  unsubscribe("trade", symbol)

def handleIn(rawmsg):
  msg = json.loads(rawmsg)
  channelId = msg["channelId"]
  if "operation" in msg:
    if "Subscribe" in msg["operation"]:
      sub = msg["operation"]["Subscribe"]
      symbol = sub["symbol"]
      chtype = sub["channelType"]
      channels[channelId] = (symbol, chtype)
      if chtype == 'orderbook':
        data = msg["data"]
        orderbooks[symbol] = {"asks":{}, "bids":{}}
        for i in data:
          onOrderbookChange(symbol, i["price"], i['quantity'])
        orderbooks[symbol]["lastknownbid"] = sorted(orderbooks[symbol]["bids"])[NEED_TOP_ORDERS]
        orderbooks[symbol]["lastknownask"] = sorted(orderbooks[symbol]["asks"], reverse=True)[NEED_TOP_ORDERS]
      if chtype == 'orderbookraw':
        data = msg["data"]
        orderbooksraw[symbol] = {"asks":{}, "bids":{}}
        for i in data:
          onOrderbookRawChange(symbol, i["id"], i["price"], i['quantity'], initial=True)
        orderbooksraw[symbol]["lastknownbid"] = sorted(orderbooksraw[symbol]["bids"],
                                                       key=lambda x: orderbooksraw[symbol]["bids"][x][0])[NEED_TOP_ORDERS]
        orderbooksraw[symbol]["lastknownask"] = sorted(orderbooksraw[symbol]["asks"],
                                                       key=lambda x: orderbooksraw[symbol]["asks"][x][0],
                                                       reverse=True)[NEED_TOP_ORDERS]
    elif "Unsubscribe" in msg:
      del channels[channelId]
  else:
    if channelId in channels:
      (symbol, channelType) = channels[channelId]
      if channelType == "ticker":
        onNewTicker(symbol, msg["last"], msg["high"], msg["low"], msg["volume"], msg["vwap"],
                         msg["maxBid"], msg["minAsk"], msg["bestBid"], msg["bestAsk"])
      elif channelType == "trade":
        onNewTrade(symbol, msg["id"], msg["timestamp"], msg["price"], msg["quantity"])
      elif channelType == "orderbook":
        onOrderbookChange(symbol, msg["price"], msg["quantity"])
      elif channelType == "orderbookraw":
        onOrderbookRawChange(symbol, msg["id"], msg["price"], msg["quantity"])

subscribeTicker('BTC/USD', 2) #do not send me tickers too often (only one time in two seconds)
subscribeOrderbook('BTC/USD', NEED_TOP_ORDERS*2)
subscribeOrderbookRaw('BTC/USD', NEED_TOP_ORDERS*2)
subscribeTrades('BTC/USD')

startedat = time.time()
eplased = 0
ticker = True
orderbook = True
orderbookRaw = True
trades = True

while eplased < 150:
  result =  ws.recv()
#  print ("Received '%s'" % result)

  if result != "": # not keepalive
    handleIn(result)

  eplased = time.time() - startedat
  if (orderbookRaw and eplased > 30):
      unsubscribeOrderbookRaw("BTC/USD")
      print ("finish raw orderbook testing")
      orderbookRaw = False

  if (orderbook and eplased > 60):
      print ("finish orderbook testing")
      unsubscribeOrderbook("BTC/USD")
      orderbook = False

  if (ticker and eplased > 90):
      print ("finish ticker testing")
      unsubscribeTicker("BTC/USD")
      ticker = False

  if (trades and eplased > 120):
      unsubscribeTrades("BTC/USD")
      print ("finish trades testing")
      trades = False

ws.close()