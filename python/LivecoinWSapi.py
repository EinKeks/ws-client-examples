import websocket
import json
import datetime
import time
import ssl

NEED_TOP_ORDERS = 5

currentMessageId = 0
channels = dict()
orderbooks = dict()
orderbooksraw = dict()
ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE}) # python issue with comodo certs
ws.connect("wss://ws.api.livecoin.net/ws/beta2")

def onNewTicker(symbol, timestamp, last, high, low, volume, vwap, maxBid, minAsk, bestBid, bestAsk):
  #here you can make your trade decision
  print ("ticker as of %s: %s/%f/%f/%f/%f/%f/%f/%f/%f/%f" % (
  datetime.datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S'),
    symbol, last, high, low, volume, vwap, maxBid, minAsk, bestBid, bestAsk))

def onNewCandle(symbol, t, o, c, h, l, v, q):
  print("candle: %s/%s/%f/%f/%f/%f/%f/%f" % (
    symbol,
    datetime.datetime.fromtimestamp(t/1000).strftime('%Y-%m-%d %H:%M:%S'),
      o, c, h, l, v, q))

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

def onUnsubscribe(channelType, symbol, token):
  print("unsibscribed from %s for %s (answer for request with token %s)" % (channelType, symbol, token))

def toWs(*arg):
  msg = json.dumps(list(arg))
  print("sending '"+msg+"'")
  ws.send(msg)

def subscribeTicker(symbol, token=None, frequency=None):
  toWs(token, "s", "t", symbol, frequency)

def unsubscribeTicker(symbol, token=None):
  toWs(token, "u", "t", symbol)

def subscribeOrderbook(symbol, token=None, depth=None):
  toWs(token, "s", "o", symbol, depth)

def unsubscribeOrderbook(symbol, token=None):
  toWs(token, "u", "o", symbol)

def subscribeOrderbookRaw(symbol, token=None, depth=None):
  toWs(token, "s", "r", symbol, depth)

def unsubscribeOrderbookRaw(symbol, token=None):
  toWs(token, "u", "r", symbol)

def subscribeTrades(symbol, token=None):
  toWs(token, "s", "d", symbol)

def unsubscribeTrades(symbol, token=None):
  toWs(token, "u", "d", symbol)

def subscribeCandle(symbol, interval, token=None, historyDepth=None):
  toWs(token, "s", "c", symbol, interval, historyDepth)

def unsubscribeCandleRaw(symbol, token=None):
  toWs(token, "u",  "c", symbol)

def NullableToFloat(num):
  if None == num:
    return float('nan')
  return float(num)

def handleIn(msg, isSnapshot = False, token=None):
  channelType = msg.pop(0)
  if "s" == channelType:
    token = msg.pop(0)
    print ("Subscribed to something (request token = %s)" % (token))
    handleIn(msg[0], isSnapshot = True, token = token) # format of snapshot is the same as notification format
  elif "u" == channelType:
    token = msg.pop(0)
    [type, symbol] = msg[0]
    onUnsubscribe(type, symbol, token)
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
    for [timestamp, price, quantity] in msg:
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
    for [timestamp, last, high, low, volume, vwap, maxBid, minAsk, bestBid, bestAsk] in msg:
      # all the values can be null (for new pairs without any orders for example)
      onNewTicker(symbol, timestamp, NullableToFloat(last), NullableToFloat(high), NullableToFloat(low), NullableToFloat(volume),
                  NullableToFloat(vwap), NullableToFloat(maxBid), NullableToFloat(minAsk), NullableToFloat(bestBid),
                  NullableToFloat(bestAsk))
  elif "e" == channelType: #error
    [originalMsg, errorCode, errorText] = msg[0]
    token = None
    try:
      out = json.loads(originalMsg)
      token = out[0]
    except:
      print("error extracting token")
    print("Error #%i (%s) for message with token '%s'" % (errorCode, errorText, token))




subscribeOrderbookRaw('BTC/USD', token="token1", depth = NEED_TOP_ORDERS) # only NEED_TOP_ORDERS bids and asks in snapshot
subscribeOrderbookRaw('ETH/USD', token="token5") # only NEED_TOP_ORDERS bids and asks in snapshot
unsubscribeOrderbook("BTC/USD", token="token2") #for error example
subscribeTicker('BTC/USD', frequency = 2) #do not send me tickers too often (only one time in two seconds)
subscribeOrderbook('BTC/USD', depth = NEED_TOP_ORDERS) # only NEED_TOP_ORDERS bids and asks positions in snapshot
subscribeTrades('BTC/USD')
subscribeCandle('BTC/USD', interval = '1m', historyDepth = 10) # and give me 10 last candles

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