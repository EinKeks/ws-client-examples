# Livecoin public websocket API

Current BETA version of Livecoin websocket API supports four types of channels: ticker, orderbook (grouped by price), orderbook raw and trades.

First, you should connect to websocket (address is wss://ws.api.livecoin.net/ws/beta ).

Then, you can subscribe \ unsubscribe any channel on any existent currency pair.

You can find example clients for Java, JavaScript, Python and C# in this repo. 

Restrictions: you can resubscrube to particular channel only once per minute (there is no restrictions for different channels).

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

`symbol` - currency pair you are intrested in;

`frequency` - optional parameter. When omitted, you wil get all ticker changes. When given, send rate will be limited to one message per `frequency` seconds. Minimal `frequency` is 0.1.

Upon subscribing you will get an answer with channelId:

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

`ATTENTION`: the method of channelId generation is a subject to change in future releases!!! It can become numeric in some future release, and you should not get nor currency pair symbol neither channel type from channelId! Your code must save map (channelId -> channelType/symbol) according "Subscribe" answers and use this map for decoding channelId to channelType/symbol.

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

depth is an optional parameter (depth of orderbook, which will be sent in an subscription answer).

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

`ATTENTION`: the method of channelId generation is a subject to change in future releases!!! It can become numeric in some future release, and you should not get nor currency pair symbol neither channel type from channelId! Your code must save map (channelId -> channelType/symbol) according "Subscribe" answers and use this map for decoding channelId to channelType/symbol.

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

depth is an optional parameter (depth of orderbook, which will be sent in an subscription answer).

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

`ATTENTION`: the method of channelId generation is a subject to change in future releases!!! It can become numeric in some future release, and you should not get nor currency pair symbol neither channel type from channelId! Your code must save map (channelId -> channelType/symbol) according "Subscribe" answers and use this map for decoding channelId to channelType/symbol.

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

`ATTENTION`: the method of channelId generation is a subject to change in future releases!!! It can become numeric in some future release, and you should not get nor currency pair symbol neither channel type from channelId! Your code must save map (channelId -> channelType/symbol) according "Subscribe" answers and use this map for decoding channelId to channelType/symbol.

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

