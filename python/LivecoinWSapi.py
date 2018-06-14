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

def subscribeCandle(symbol, interval):
  subscribe("candle", symbol, {"interval": interval})

def unsubscribeCandleRaw(symbol):
  unsubscribe("candle", symbol)

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
      if chtype == 'candle':
        data = msg["data"]
        for i in data:
          onNewCandle(symbol, i['t'], i['o'], i['c'], i['h'], i['l'], i['v'], i['q'])
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
      elif channelType == "candle":
        onNewCandle(symbol, msg["t"], msg["o"], msg["c"], msg["h"], msg["l"], msg["v"], msg["q"])

#subscribeTicker('BTC/USD', 2) #do not send me tickers too often (only one time in two seconds)
#subscribeOrderbook('BTC/USD', NEED_TOP_ORDERS*2)
#subscribeOrderbookRaw('BTC/USD', NEED_TOP_ORDERS*2)
#subscribeTrades('BTC/USD')
#subscribeCandle('BTC/USD', '1m')

subscribeTrades('BTC/USD')
subscribeTrades('BTC/EUR')
subscribeTrades('LTC/USD')
subscribeTrades('EUR/USD')
subscribeTrades('BTC/RUR')
subscribeTrades('EMC/USD')
subscribeTrades('USD/RUR')
subscribeTrades('EMC/BTC')
subscribeTrades('LTC/BTC')
subscribeTrades('DASH/BTC')
subscribeTrades('DOGE/BTC')
subscribeTrades('DOGE/USD')
subscribeTrades('PPC/BTC')
subscribeTrades('NMC/BTC')
subscribeTrades('MONA/BTC')
subscribeTrades('CURE/BTC')
subscribeTrades('ETH/BTC')
subscribeTrades('SIB/BTC')
subscribeTrades('TX/BTC')
subscribeTrades('RBIES/BTC')
subscribeTrades('ADZ/BTC')
subscribeTrades('MOJO/BTC')
subscribeTrades('BSD/BTC')
subscribeTrades('SXC/BTC')
subscribeTrades('BTA/BTC')
subscribeTrades('VOX/BTC')
subscribeTrades('CRBIT/BTC')
subscribeTrades('SHIFT/BTC')
subscribeTrades('YOC/BTC')
subscribeTrades('CREVA/BTC')
subscribeTrades('ETH/USD')
subscribeTrades('ETH/RUR')
subscribeTrades('LSK/BTC')
subscribeTrades('EL/BTC')
subscribeTrades('EL/RUR')
subscribeTrades('HNC/BTC')
subscribeTrades('YOC/USD')
subscribeTrades('YOC/RUR')
subscribeTrades('MOIN/BTC')
subscribeTrades('BLU/BTC')
subscribeTrades('LEO/BTC')
subscribeTrades('EMC/RUR')
subscribeTrades('REE/BTC')
subscribeTrades('LEO/USD')
subscribeTrades('LEO/RUR')
subscribeTrades('GAME/BTC')
subscribeTrades('SLR/BTC')
subscribeTrades('BLK/BTC')
subscribeTrades('SYS/BTC')
subscribeTrades('DGB/BTC')
subscribeTrades('VRC/BTC')
subscribeTrades('THS/BTC')
subscribeTrades('GYC/BTC')
subscribeTrades('XMR/BTC')
subscribeTrades('XMR/USD')
subscribeTrades('THS/USD')
subscribeTrades('BTS/BTC')
subscribeTrades('CLOAK/BTC')
subscribeTrades('GB/BTC')
subscribeTrades('VRM/BTC')
subscribeTrades('ARC/BTC')
subscribeTrades('ATX/BTC')
subscribeTrades('POST/BTC')
subscribeTrades('BURST/BTC')
subscribeTrades('ENT/BTC')
subscribeTrades('CRBIT/LEO')
subscribeTrades('NXT/BTC')
subscribeTrades('EDR/BTC')
subscribeTrades('KRB/BTC')
subscribeTrades('OD/BTC')
subscribeTrades('DMC/BTC')
subscribeTrades('DMC/USD')
subscribeTrades('ADZ/USD')
subscribeTrades('EL/USD')
subscribeTrades('LSK/USD')
subscribeTrades('DASH/USD')
subscribeTrades('VRS/BTC')
subscribeTrades('XRC/BTC')
subscribeTrades('BIT/BTC')
subscribeTrades('CLOAK/USD')
subscribeTrades('DOLLAR/BTC')
subscribeTrades('XAUR/BTC')
subscribeTrades('GOLOS/BTC')
subscribeTrades('VLTC/BTC')
subscribeTrades('SIB/RUR')
subscribeTrades('CCRB/BTC')
subscribeTrades('UNC/BTC')
subscribeTrades('BPC/BTC')
subscribeTrades('VSL/BTC')
subscribeTrades('BLU/USD')
subscribeTrades('DIME/RUR')
subscribeTrades('DIME/USD')
subscribeTrades('DIME/EUR')
subscribeTrades('DIME/BTC')
subscribeTrades('ICN/BTC')
subscribeTrades('PRES/BTC')
subscribeTrades('ZBC/BTC')
subscribeTrades('DIBC/BTC')
subscribeTrades('LUNA/BTC')
subscribeTrades('ABN/BTC')
subscribeTrades('NVC/BTC')
subscribeTrades('XSPEC/BTC')
subscribeTrades('ACN/BTC')
subscribeTrades('CRBIT/ETH')
subscribeTrades('LDC/BTC')
subscribeTrades('MSCN/ETH')
subscribeTrades('MSCN/BTC')
subscribeTrades('MSCN/RUR')
subscribeTrades('MSCN/USD')
subscribeTrades('MSCN/EUR')
subscribeTrades('POSW/BTC')
subscribeTrades('POSW/ETH')
subscribeTrades('OBITS/BTC')
subscribeTrades('EDR/USD')
subscribeTrades('EDR/RUR')
subscribeTrades('TIME/BTC')
subscribeTrades('OBITS/ETH')
subscribeTrades('OBITS/USD')
subscribeTrades('WAVES/BTC')
subscribeTrades('INCNT/BTC')
subscribeTrades('DANC/ZBC')
subscribeTrades('VRS/USD')
subscribeTrades('ZBC/USD')
subscribeTrades('ZBC/ETH')
subscribeTrades('ZBC/EUR')
subscribeTrades('ZBC/XMR')
subscribeTrades('ZBC/RUR')
subscribeTrades('EMC/ETH')
subscribeTrades('EMC/XMR')
subscribeTrades('EMC/DASH')
subscribeTrades('DBIX/BTC')
subscribeTrades('TAAS/USD')
subscribeTrades('ARC/USD')
subscribeTrades('ARC/RUR')
subscribeTrades('ARC/ETH')
subscribeTrades('POSW/DASH')
subscribeTrades('POSW/RUR')
subscribeTrades('POSW/USD')
subscribeTrades('POSW/EUR')
subscribeTrades('POSW/XMR')
subscribeTrades('POSW/LTC')
subscribeTrades('TAAS/BTC')
subscribeTrades('XMS/BTC')
subscribeTrades('THS/ETH')
subscribeTrades('POST/ETH')
subscribeTrades('DIBC/ETH')
subscribeTrades('LEO/ETH')
subscribeTrades('DANC/BTC')
subscribeTrades('CCRB/ETH')
subscribeTrades('SOAR/BTC')
subscribeTrades('FUNC/USD')
subscribeTrades('FUNC/ETH')
subscribeTrades('FUNC/BTC')
subscribeTrades('PIVX/BTC')
subscribeTrades('PIVX/USD')
subscribeTrades('PIVX/EUR')
subscribeTrades('PIVX/RUR')
subscribeTrades('PIVX/ETH')
subscribeTrades('KRB/USD')
subscribeTrades('KRB/RUR')
subscribeTrades('ITI/BTC')
subscribeTrades('ITI/RUR')
subscribeTrades('ITI/ETH')
subscribeTrades('ITI/EUR')
subscribeTrades('PUT/BTC')
subscribeTrades('PUT/ETH')
subscribeTrades('GUP/BTC')
subscribeTrades('GUP/ETH')
subscribeTrades('MNE/BTC')
subscribeTrades('MNE/ETH')
subscribeTrades('WINGS/BTC')
subscribeTrades('WINGS/ETH')
subscribeTrades('UNRC/BTC')
subscribeTrades('PUT/USD')
subscribeTrades('RLT/BTC')
subscribeTrades('RLT/RUR')
subscribeTrades('RLT/ETH')
subscribeTrades('RLT/USD')
subscribeTrades('UNY/BTC')
subscribeTrades('UNY/ETH')
subscribeTrades('UNY/LTC')
subscribeTrades('UNY/USD')
subscribeTrades('STRAT/BTC')
subscribeTrades('STRAT/ETH')
subscribeTrades('STRAT/USD')
subscribeTrades('FORTYTWO/BTC')
subscribeTrades('FORTYTWO/ETH')
subscribeTrades('FORTYTWO/USD')
subscribeTrades('UNRC/USD')
subscribeTrades('INSN/BTC')
subscribeTrades('INSN/ETH')
subscribeTrades('INSN/USD')
subscribeTrades('QAU/BTC')
subscribeTrades('QAU/ETH')
subscribeTrades('QAU/USD')
subscribeTrades('TRUMP/BTC')
subscribeTrades('TRUMP/ETH')
subscribeTrades('FNC/BTC')
subscribeTrades('FNC/ETH')
subscribeTrades('FNC/USD')
subscribeTrades('MCO/BTC')
subscribeTrades('MCO/ETH')
subscribeTrades('MCO/USD')
subscribeTrades('DANC/USD')
subscribeTrades('DIBC/USD')
subscribeTrades('XRC/USD')
subscribeTrades('PUT/RUR')
subscribeTrades('PPY/BTC')
subscribeTrades('PPY/ETH')
subscribeTrades('PPY/USD')
subscribeTrades('ASAFE2/BTC')
subscribeTrades('PLBT/BTC')
subscribeTrades('PLBT/USD')
subscribeTrades('PLBT/ETH')
subscribeTrades('ASAFE2/USD')
subscribeTrades('DIME/ETH')
subscribeTrades('KPL/BTC')
subscribeTrades('KPL/USD')
subscribeTrades('KPL/ETH')
subscribeTrades('BCH/BTC')
subscribeTrades('BCH/USD')
subscribeTrades('BCH/ETH')
subscribeTrades('BCH/ZBC')
subscribeTrades('BCH/RUR')
subscribeTrades('NVC/USD')
subscribeTrades('MCR/BTC')
subscribeTrades('MCR/ETH')
subscribeTrades('FU/BTC')
subscribeTrades('FU/ETH')
subscribeTrades('WIC/BTC')
subscribeTrades('WIC/ETH')
subscribeTrades('PIPL/BTC')
subscribeTrades('PIPL/ETH')
subscribeTrades('HVN/BTC')
subscribeTrades('HVN/ETH')
subscribeTrades('HVN/USD')
subscribeTrades('XRL/BTC')
subscribeTrades('XRL/ETH')
subscribeTrades('MGO/BTC')
subscribeTrades('MGO/ETH')
subscribeTrades('THS/RUR')
subscribeTrades('GRS/BTC')
subscribeTrades('GRS/ETH')
subscribeTrades('XEM/BTC')
subscribeTrades('XEM/ETH')
subscribeTrades('XEM/USD')
subscribeTrades('PRO/BTC')
subscribeTrades('PRO/ETH')
subscribeTrades('PRO/USD')
subscribeTrades('REE/ETH')
subscribeTrades('REE/USD')
subscribeTrades('GRS/USD')
subscribeTrades('SOAR/ETH')
subscribeTrades('VOISE/BTC')
subscribeTrades('VOISE/ETH')
subscribeTrades('VOISE/USD')
subscribeTrades('VOISE/EUR')
subscribeTrades('CPC/BTC')
subscribeTrades('CPC/ETH')
subscribeTrades('CPC/USD')
subscribeTrades('eETT/BTC')
subscribeTrades('eETT/ETH')
subscribeTrades('eETT/USD')
subscribeTrades('eETT/wETT')
subscribeTrades('wETT/BTC')
subscribeTrades('wETT/ETH')
subscribeTrades('wETT/USD')
subscribeTrades('wETT/WAVES')
subscribeTrades('SUMO/BTC')
subscribeTrades('SUMO/ETH')
subscribeTrades('VIB/USD')
subscribeTrades('VIB/ETH')
subscribeTrades('VIB/BTC')
subscribeTrades('GNT/BTC')
subscribeTrades('GNT/ETH')
subscribeTrades('GNT/USD')
subscribeTrades('KNC/BTC')
subscribeTrades('KNC/ETH')
subscribeTrades('KNC/USD')
subscribeTrades('CVC/BTC')
subscribeTrades('CVC/ETH')
subscribeTrades('CVC/USD')
subscribeTrades('DGD/BTC')
subscribeTrades('DGD/ETH')
subscribeTrades('DGD/USD')
subscribeTrades('MTL/BTC')
subscribeTrades('MTL/ETH')
subscribeTrades('MTL/USD')
subscribeTrades('REP/BTC')
subscribeTrades('REP/ETH')
subscribeTrades('REP/USD')
subscribeTrades('BAT/BTC')
subscribeTrades('BAT/ETH')
subscribeTrades('BAT/USD')
subscribeTrades('EOS/BTC')
subscribeTrades('EOS/ETH')
subscribeTrades('EOS/USD')
subscribeTrades('BNT/BTC')
subscribeTrades('BNT/ETH')
subscribeTrades('BNT/USD')


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

  if result != "":
    try: # not keepalive
      handleIn(result)
    except:
      print("failed")

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