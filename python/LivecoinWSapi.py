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
#ws.connect("wss://ws.api.livecoin.net/ws/beta")
ws.connect("ws://localhost:9160/ws/beta")

def onNewTicker(symbol, last, high, low, volume, vwap, maxBid, minAsk, bestBid, bestAsk):
  #here you can make your trade decision
  print ("ticker: %s/%f/%f/%f/%f/%f/%f/%f/%f/%f" % (symbol, last, high, low, volume, vwap, maxBid, minAsk, bestBid, bestAsk))

def onNewCandle(symbol, t, o, c, h, l, v, q):
  print("candle: %s/%s/%f/%f/%f/%f/%f/%f" % (
    symbol,
    datetime.datetime.fromtimestamp(t/1000).strftime('%Y-%m-%d %H:%M:%S'),
    o,
    c,
    h,
    l,
    v,
    q))

def onNewTrade(symbol, id, timestamp, price, quantity, isBuy):
  print ("trade: %s, id=%d time=%s type=%s price=%f quantity=%f" % (
    symbol,
    id,
    datetime.datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S'),
    "BUY" if isBuy else "SELL",
    price,
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


def onOrderbookChange(symbol, timestamp, price, quantity, isBid, initial=False):
  slots = orderbooks[symbol]["bids" if isBid else "asks"]
  if quantity == 0:
    if price in slots:
      del slots[price]
  else:
    slots[price] = quantity
  printOrderBook(symbol)

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

def onOrderbookRawChange(symbol, timestamp, id, price, quantity, isBid, initial=False):
  slots = orderbooksraw[symbol]["bids" if isBid else "asks"]
  if quantity == 0:
    if id in slots:
      del slots[id]
  else:
    slots[id] = (price,quantity)
  printOrderBookRaw(symbol)

def onUnsubscribe(channelType, symbol):
  print("unsibscribed from %s for %s" % (channelType, symbol))

def toWs(*arg):
  ws.send(json.dumps(list(arg)))

def subscribeTicker(symbol, frequency=None):
  if None == frequency:
    toWs("s", "t", symbol)
  else:
    toWs("s", "t", symbol, frequency)

def unsubscribeTicker(symbol):
  toWs("u", "t", symbol)

def subscribeOrderbook(symbol, depth=None):
  if None == depth:
    toWs("s", "o", symbol)
  else:
    toWs("s", "o", symbol, depth)

def unsubscribeOrderbook(symbol):
  toWs("u", "o", symbol)

def subscribeOrderbookRaw(symbol, depth=None):
  if None == depth:
    toWs("s", "r", symbol)
  else:
    toWs("s", "r", symbol, depth)

def unsubscribeOrderbookRaw(symbol):
  toWs("u", "r", symbol)

def subscribeTrades(symbol):
  toWs("s", "d", symbol)

def unsubscribeTrades(symbol):
  toWs("u", "d", symbol)

def subscribeCandle(symbol, interval, historyDepth=None):
  if None == historyDepth:
    toWs("s", "c", symbol, interval)
  else:
    toWs("s", "c", symbol, interval, historyDepth)

def unsubscribeCandleRaw(symbol):
  toWs("u", "c", symbol)

def NullableToFloat(num):
  if None == num:
    return float('nan')
  return float(num)

def handleIn(msg, isSnapshot = False):
  channelType = msg.pop(0)
  if "s" == channelType:
    handleIn(msg[0], isSnapshot = True) # format of snapshot is the same as notification format
  elif "u" == channelType:
    [type, symbol] = msg[0]
    onUnsubscribe(type, symbol)
  elif "r" == channelType: #raw orderbook
    symbol = msg.pop(0)
    if isSnapshot:
      orderbooksraw[symbol] = {"asks": {}, "bids": {}}  # clear it
    for [id, timestamp, price, quantity] in msg:
      onOrderbookRawChange(symbol, timestamp, id, abs(price), quantity, isBid = (price > 0), initial=isSnapshot)
  elif "o" == channelType:  # orderbook
    symbol = msg.pop(0)
    if isSnapshot:
      orderbooks[symbol] = {"asks": {}, "bids": {}}  # clear it
    for [price, quantity] in msg:
      timestamp = 0
      onOrderbookChange(symbol, timestamp, abs(price), quantity, isBid=(price > 0), initial=isSnapshot)
  elif "d" == channelType: #trades
    symbol = msg.pop(0)
    for [id, timestamp, price, quantity] in msg:
      onNewTrade(symbol, id, timestamp, abs(price), quantity, isBuy = (price > 0))
  elif "c" == channelType: #candles
    symbol = msg.pop(0)
    for [t, o, c, h, l, v, q] in msg:
      onNewCandle(symbol, t, o, c, h, l, v, q)
  elif "t" == channelType: #ticker
    symbol = msg.pop(0)
    for [last, high, low, volume, vwap, maxBid, minAsk, bestBid, bestAsk] in msg:
      # all the values can be null (for new pairs without any orders for example)
      onNewTicker(symbol, NullableToFloat(last), NullableToFloat(high), NullableToFloat(low), NullableToFloat(volume),
                  NullableToFloat(vwap), NullableToFloat(maxBid), NullableToFloat(minAsk), NullableToFloat(bestBid),
                  NullableToFloat(bestAsk))


subscribeOrderbookRaw('BTC/USD', NEED_TOP_ORDERS) # only NEED_TOP_ORDERS bids and asks in snapshot
subscribeTicker('BTC/USD', 2) #do not send me tickers too often (only one time in two seconds)
subscribeOrderbook('BTC/USD', NEED_TOP_ORDERS) # only NEED_TOP_ORDERS bids and asks positions in snapshot
subscribeTrades('BTC/USD')
subscribeCandle('BTC/USD', '1m', 10) # and give me 10 last candles

startedat = time.time()
eplased = 0
ticker = True
orderbook = True
orderbookRaw = True
trades = True
candles = True

while eplased < 180:
  result =  ws.recv()
  print ("Received '%s'" % result)

  if result != "": # not keepalive
    handleIn(json.loads(result))

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

  if (candles and eplased > 150):
    unsubscribeCandleRaw("BTC/USD")
    print("finish candles testing")
    candles = False

ws.close()