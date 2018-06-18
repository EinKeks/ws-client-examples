# Livecoin public websocket API

Current BETA version of Livecoin websocket API supports four types of channels: ticker, orderbook (grouped by price), orderbook raw, trades and candles.

First, you should connect to websocket (address is wss://ws.api.livecoin.net/ws/beta).

Then, you can subscribe/unsubscribe to any channel of an existing currency pair in the exchange.

You can find example clients for Java, JavaScript, Python and C# in this repo. 

`Restrictions`

1. You can resubscribe to each channel only once per minute (there is no restrictions for different channels).

2. Outgoing queue size of websocket is limited to 256 messages, so you can have a maximum of 256 'inflight' subscriptions (when you have sent
a message to subscribe and did not get the answer 'subscribed'). When you want to subscribe to more then 256 topics at once,
you have to queue subscriptions or wait a while between sending blocks of subscriptions. Sending too many subscription requests at once or
not receiving too many messages from websocket will lead to disconnection.

`Queue size will be increased on next update to handle 'subscribe one type of channel for all pairs at once'`

### 0. General information

You will get empty ("") messages every 30 seconds. You don't need to answer them or send anything to keep connection alive (but read the restrictions about the outgoing queue size!!!).

All subscriptions are valid and active from subscription until you sent 'Unsibscribe' message or your connection is close. There are no other ways to cancel your subscription.

Time is synchronized with public NTP servers, so timestamps in messages are accurate.

There are no restrictions on the connection time **for now** (really - until the next service update). But this can be changed, especially after the implementation of private functions.

There are no special restrictions on the subscriptions count.
But, for example, you will not be able to subscribe to candles of all the currency pairs - every minute system will try to send candles on each pair, and it will be more messages then outgoing queue size, so connection will be dropped.
Candle channels are a "special case" (too many simul,
Next case - if you will subscribe too many channels at once without reading from websocket - the same issue - outgoing queue can become full.

`Queue size will be increased on next update to handle 'subscribe one type of channel for all pairs at once' and 'subscribe and get candles for all pairs'`

### 1. Ticker channel

To subscribe send this message:

    {
        "Subscribe": {
            "channelType": "ticker",
            "symbol": "BTC/USD",
            "frequency": 2.0
        }
    }

where

`channelType` - constant "ticker";

`symbol` - currency pair you are interested in;

`frequency` - optional parameter. When omitted, you will get all ticker changes. When given, send rate will be limited to one message per `frequency` seconds. Minimum `frequency` is 0.1.

Upon subscribing you will get a response with channelId:

    {
        "channelId": "BTC/USD_ticker",
        operation": {
            Subscribe": {
                channelType": "ticker",
                symbol": "BTC/USD",
                frequency": 2.0
            }
        }
    }

`ATTENTION`: the method of channelId generation is subject to change in future releases!!! It maybe changed to a numeric value in a future release. Therefore you should not rely on currency pair symbol nor channel type from channelId remaining the same! Your code must save map (channelId -> channelType/symbol) according to the "Subscribe" response and use this map for decoding channelId to channelType/symbol.

When ticker changes you will get messages like this:

    {
        "channelId": "BTC/USD_ticker",
        "last": 12998,
        "high": 13002,
        "low": 12998,
        "volume": 0.00165000,
        "vwap": 12999.81818182,
        "maxBid": 13002,
        "minAsk": 12998,
        "bestBid": 12998,
        "bestAsk": 13002
    }

If you want to unsubscribe, send message like this:

    {
        "Unsubscribe": {
            "channelId": "BTC/USD_ticker"
        }
    }

You will get an answer:

    {
        "channelId": "BTC/USD_ticker",
        "operation": {
            "Unsubscribe": {
                "channelId": "BTC/USD_ticker"
            }
        }
    }


### 2. Orderbook grouped by prices

To subscribe send message like this:

    {
        "Subscribe": {
            "channelType": "orderbook",
            "symbol": "BTC/USD",
            "depth": 20
        }
    }

`depth` is an optional parameter (depth of orderbook, which will be sent in an subscription answer).

Upon subscribing you will get an answer with channelId and current orderbook state:

    {
        "channelId": "BTC/USD_orderbook",
        "operation": {
            "Subscribe": {
                "channelType": "orderbook",
                "symbol": "BTC/USD",
                "depth": 20
            }
        },
        "data": [{
            "price": -13002,
            "quantity": 0.04595
        }, {
            "price": -13003,
            "quantity": 0.05
        }, {
            "price": -13004,
            "quantity": 0.05
        }, {
            "price": 0.00001,
            "quantity": 1151.23011
        }]
    }

Price is positive for bids and negative for asks.

`ATTENTION`: the method of channelId generation is subject to change in future releases!!! It maybe changed to a numeric value in a future release. Therefore you should not rely on currency pair symbol nor channel type from channelId remaining the same! Your code must save map (channelId -> channelType/symbol) according to the "Subscribe" response and use this map for decoding channelId to channelType/symbol.

When orderbook changes you will get messages like this (for bid changes):

    {
        "channelId": "BTC/USD_orderbook",
        "price": 12998,
        "quantity": 1.90149297
    }

or this (for ask changes):

    {
        "channelId": "BTC/USD_orderbook",
        "price": -13002,
        "quantity": 0.04565
    }

Closed position will be sent with zero quantity.

To unsubscribe send message like this:

    {
        "Unsubscribe": {
            "channelId": "BTC/USD_orderbook"
        }
    }

### 3. Raw orderbook

To subscribe send message like this:

    {
        "Subscribe": {
            "channelType": "orderbookraw",
            "symbol": "BTC/USD",
            "depth": 10
        }
    }

`depth` is an optional parameter (depth of orderbook, which will be sent in an subscription answer).

You will get an answer:

    {
        "channelId": "BTC/USD_orderbookraw",
        "operation": {
            "Subscribe": {
                "channelType": "orderbookraw",
                "symbol": "BTC/USD",
                "depth": 1
            }
        },
        "data": [{
            "id": 568405551,
            "price": -13002,
            "quantity": 0.04565
        }, {
            "id": 568402601,
            "price": 12998,
            "quantity": 1
        }]
    }

Price is positive for bids and negative for asks.

`ATTENTION`: the method of channelId generation is subject to change in future releases!!! It maybe changed to a numeric value in a future release. Therefore you should not rely on currency pair symbol nor channel type from channelId remaining the same! Your code must save map (channelId -> channelType/symbol) according to the "Subscribe" response and use this map for decoding channelId to channelType/symbol.

When orderbook changes you will get messages like this (for bid changes):

    {
        "channelId": "BTC/USD_orderbookraw",
        "id": 568408501,
        "price": 13002,
        "quantity": 0
    }

or like this (for ask changes):

    {
        "channelId": "BTC/USD_orderbookraw",
        "id": 568405551,
        "price": -13002,
        "quantity": 0.04550
    }

Closed position will be sent with zero quantity.

To unsubscribe, send message like this:

    {
        "Unsubscribe": {
            "channelId": "BTC/USD_orderbookraw"
        }
    }

### 4. Trades

To subscribe send message like this:

    {
        "Subscribe": {
            "channelType": "trade",
            "symbol": "BTC/USD"
        }
    }

Upon subscribing you will get an answer with channelId:

    {
        "channelId": "BTC/USD_trade",
        "operation": {
            "Subscribe": {
                "channelType": "trade",
                "symbol": "BTC/USD"
            }
        }
    }

`ATTENTION`: the method of channelId generation is subject to change in future releases!!! It maybe changed to a numeric value in a future release. Therefore you should not rely on currency pair symbol nor channel type from channelId remaining the same! Your code must save map (channelId -> channelType/symbol) according to the "Subscribe" response and use this map for decoding channelId to channelType/symbol.

Upon new trades you will get messages like this (when trade is "BUY"):

    {
        "channelId": "BTC/USD_trade",
        "id": 227794451,
        "timestamp": 1527013099415,
        "price": -12998,
        "quantity": 0.00015
    }

or like this (when trade is "SELL"):

    {
        "channelId": "BTC/USD_trade",
        "id": 227794501,
        "timestamp": 1527013100822,
        "price": 13002,
        "quantity": 0.00015
    }

timestamp is Unix timestamp multiplied by 1000.

To unsubscribe send message like this:

    {
        "Unsubscribe": {
            "channelId": "BTC/USD_trade"
        }
    }

### 5. Candles

To subscribe send message like this:

    {
        "Subscribe": {
            "channelType": "candle",
            "symbol": "BTC/USD",
            "interval": "1m"
        }
    }

interval now supports only "1m" (1 minute).

Upon subscribing you will get an answer with channelId and current orderbook state:

    {
        "channelId": "BTC/USD_candle",
        "operation": {
            "Subscribe": {
                "channelType": "orderbook",
                "symbol": "BTC/USD",
                "interval": "1m"
            }
        },
        "data": [
            {"t":1528447620000,"o":7883.0874,"c":7883.0874,"h":7883.0874,"l":7883.0874,"v":0,"q":0},
            {"t":1528447680000,"o":7883.0874,"c":7885,"h":7885,"l":7883.0874,"v":16.52396370,"q":0.00209562},
            ...
        ]
    }

`t` is interval's start timestamp (Unix timestamp multiplied by 1000),

`o` is open price (price at timestamp `t`),

`c` is close price (price at timestamp `t` + `interval` [1m] ), 

`h` is the highest trade price at the interval,

`l` is the lowest trade price at the interval,

`v` is volume traded at the interval,

`q` is quantity traded at the interval.

In the `data` field you will get last 240 candles.

`ATTENTION`: the method of channelId generation is subject to change in future releases!!! It maybe changed to a numeric value in a future release. Therefore you should not rely on currency pair symbol nor channel type from channelId remaining the same! Your code must save map (channelId -> channelType/symbol) according to the "Subscribe" response and use this map for decoding channelId to channelType/symbol.

Every `interval` (currently - every minute) you will get messages like this:

    {"channelId":"BTC/USD_candle","t":1528462020000,"o":7.9E+3,"c":7901.58001,"h":7.92E+3,"l":7.9E+3,"v":613.21937803,"q":0.07762054}

To unsubscribe send a message like this:

    {
        "Unsubscribe": {
            "channelId": "BTC/USD_candle"
        }
    }
