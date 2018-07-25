"use strict";

window.onload = function() {

    // require('protobufjs')
    protobuf.load("js/wsApi.proto", function (err, root) {
        // var socket = connect("wss://ws.api.livecoin.net/ws/beta");
        var socket = connect("ws://localhost:9161/ws/beta");
        socket.onopen = function () {
            console.log("Connection established.");
            // tickerSubscribe("token","BTC/USD", null);
            // orderBookSubscribe("token1", "BTC/USD", 1);
            // rawOrderBookSubscribe("token2", "BTC/USD", 1);
            // tradeSubscribe("token3", "BTC/USD");
            candleSubscribe("token4", "BTC/USD", "1m", 0)
            // subscribe(null, "t", "BTC/USD", 10.0);
            // subscribe(null, "o", "BTC/USD", 1);
            // subscribe(null, "r", "BTC/USD", 1);
            // subscribe(null, "d", "BTC/USD", null);
            // subscribe(null, "c", "BTC/USD", "1m");
            //
            setTimeout(function () {
                var UnsubscribeRequest = root.lookupType("protobuf.ws.UnsubscribeRequest");
                unsubscribe("token5",UnsubscribeRequest.ChannelType.CANDLE,"BTC/USD")
            //     unsubscribe(null, "BTC/USD", "t");
            //     unsubscribe(null, "BTC/USD", "r");
            //     unsubscribe(null, "BTC/USD", "o");
            //     unsubscribe(null, "BTC/USD", "d");
            //     unsubscribe(null, "BTC/USD", "c");
            }, 30000);
            setTimeout(disconnect, 140000)
            //here you can make your trade decision
        };

        var doMessage = function(token, subscriptionPayload, lookupTypeValue, msgType) {
            var Subscription = root.lookupType(lookupTypeValue);
            var subscriptionError = Subscription.verify(subscriptionPayload);
            if(subscriptionError) {
                console.log(subscriptionError);
                throw Error(subscriptionError);
            }
            var subscriptionMessage = Subscription.create(subscriptionPayload);
            var subscriptionBuffer = Subscription.encode(subscriptionMessage).finish();


            var WsRequestMeta = root.lookupType("protobuf.ws.WsRequestMetaData");
            var metaPayload = {
                requestType: msgType,
                token: token,
                sign: null
            };
            var metaError = WsRequestMeta.verify(metaPayload);
            if (metaError) {
                console.log(metaError);
                throw Error(metaError);
            }
            var metaMessage = WsRequestMeta.create(metaPayload);

            var WsRequest = root.lookupType("protobuf.ws.WsRequest");
            var requestPayload = {
                meta: metaMessage,
                msg: subscriptionBuffer
            };
            var requestError = WsRequest.verify(requestPayload);
            if (requestError) {
                console.log(requestError);
                throw Error(requestError);
            }
            var requestMessage = WsRequest.create(requestPayload);
            var request = WsRequest.encode(requestMessage).finish();
            socket.send(request);
        };

        var tickerSubscribe = function (token, cp, frequency) {
            var subscriptionPayload = {
                currencyPair: cp,
                frequency: frequency
            };
            var WsRequestMeta = root.lookupType("protobuf.ws.WsRequestMetaData");

            doMessage(token, subscriptionPayload, "protobuf.ws.SubscribeTickerChannelRequest", WsRequestMeta.WsRequestMsgType.SUBSCRIBE_TICKER)
        };

        var orderBookSubscribe = function (token, cp, depth) {
            var WsRequestMeta = root.lookupType("protobuf.ws.WsRequestMetaData");
            var subscriptionPayload = {
                currencyPair: cp,
                frequency: depth
            };
            doMessage(token, subscriptionPayload, "protobuf.ws.SubscribeOrderBookChannelRequest", WsRequestMeta.WsRequestMsgType.SUBSCRIBE_ORDER_BOOK);
        };
        var rawOrderBookSubscribe = function (token, cp, depth) {
            var WsRequestMeta = root.lookupType("protobuf.ws.WsRequestMetaData");
            var subscriptionPayload = {
                currencyPair: cp,
                frequency: depth
            };
            doMessage(token, subscriptionPayload, "protobuf.ws.SubscribeOrderBookRawChannelRequest", WsRequestMeta.WsRequestMsgType.SUBSCRIBE_ORDER_BOOK_RAW);
        };
        var tradeSubscribe = function (token, cp) {
            var WsRequestMeta = root.lookupType("protobuf.ws.WsRequestMetaData");
            var subscriptionPayload = {
                currencyPair: cp
            };
            doMessage(token, subscriptionPayload, "protobuf.ws.SubscribeTradeChannelRequest", WsRequestMeta.WsRequestMsgType.SUBSCRIBE_TRADE);
        };
        var candleSubscribe = function(token, cp, interval, depth) {
            var WsRequestMeta = root.lookupType("protobuf.ws.WsRequestMetaData");
            var CandleChannelRequest = root.lookupType("protobuf.ws.SubscribeCandleChannelRequest");
            var subscriptionPayload = {
                currencyPair: cp,
                interval: CandleChannelRequest.CandleInterval.CANDLE_1_MINUTE,
                depth: depth === null ? depth : 0
            };
            doMessage(token, subscriptionPayload, "protobuf.ws.SubscribeCandleChannelRequest", WsRequestMeta.WsRequestMsgType.SUBSCRIBE_CANDLE);
        };
        var unsubscribe = function(token, channelType, cp) {
            var WsRequestMeta = root.lookupType("protobuf.ws.WsRequestMetaData");
            var subscriptionPayload = {
                channelType: channelType,
                currencyPair: cp
            };
            doMessage(token, subscriptionPayload, "protobuf.ws.UnsubscribeRequest", WsRequestMeta.WsRequestMsgType.UNSUBSCRIBE);
        };

        socket.onclose = function (event) {
            if (event.wasClean) {
                console.log('The connection is closed cleanly');
            } else {
                console.log('Connection failure'); // например, "убит" процесс сервера
            }
            console.log('Code: ' + event.code + ' reason: ' + event.reason);
        };

        socket.onmessage = function (event) {
            console.log("data received ");
            var WsResponse = root.lookupType("protobuf.ws.WsResponse");
            var wsMessageBuffer = event.data;
            if ((wsMessageBuffer) !== "") {
                var wsResponseMessage = WsResponse.decode(new Uint8Array(wsMessageBuffer));
                var WsResponseMeta = root.lookupType("protobuf.ws.WsResponseMetaData");
                var MessageClass;
                var message;
                if (wsResponseMessage.meta.responseType === WsResponseMeta.WsResponseMsgType.TICKER_CHANNEL_SUBSCRIBED) {
                    MessageClass = root.lookupType("protobuf.ws.TickerChannelSubscribedResponse");
                    message = MessageClass.decode(wsResponseMessage.msg);
                    onSubscribe({ channelType: "tiker", currencyPair: message.currencyPair})
                    if(message.data.length > 0) {
                        message.data.forEach(function(event){
                            onTicker({currencyPair:message.currencyPair, data:event})
                        })
                    }
                } else if (wsResponseMessage.meta.responseType === WsResponseMeta.WsResponseMsgType.ORDER_BOOK_RAW_CHANNEL_SUBSCRIBED) {
                    MessageClass = root.lookupType("protobuf.ws.OrderBookRawChannelSubscribedResponse");
                    message = MessageClass.decode(wsResponseMessage.msg);
                    onSubscribe({ channelType: "orderbookraw", currencyPair: message.currencyPair});
                    if(message.data.length > 0) {
                        message.data.forEach(function(event){
                            onOrderBookRaw({currencyPair:message.currencyPair, data:event})
                        })
                    }
                } else if (wsResponseMessage.meta.responseType === WsResponseMeta.WsResponseMsgType.ORDER_BOOK_CHANNEL_SUBSCRIBED) {
                    MessageClass = root.lookupType("protobuf.ws.OrderBookChannelSubscribedResponse");
                    message = MessageClass.decode(wsResponseMessage.msg);
                    onSubscribe({ channelType: "orderbook", currencyPair: message.currencyPair});
                    if(message.data.length > 0) {
                        message.data.forEach(function(event){
                            onOrderBook({currencyPair:message.currencyPair, data:event})
                        })
                    }
                } else if (wsResponseMessage.meta.responseType === WsResponseMeta.WsResponseMsgType.TRADE_CHANNEL_SUBSCRIBED) {
                    MessageClass = root.lookupType("protobuf.ws.TradeChannelSubscribedResponse");
                    message = MessageClass.decode(wsResponseMessage.msg);
                    onSubscribe({ channelType: "trade", currencyPair: message.currencyPair});
                    if(message.data.length > 0) {
                        message.data.forEach(function(event){
                            onTrade({currencyPair:message.currencyPair, data:event})
                        })
                    }
                }  else if (wsResponseMessage.meta.responseType === WsResponseMeta.WsResponseMsgType.CANDLE_CHANNEL_SUBSCRIBED) {
                    MessageClass = root.lookupType("protobuf.ws.CandleChannelSubscribedResponse");
                    message = MessageClass.decode(wsResponseMessage.msg);
                    onSubscribe({ channelType: "candle", currencyPair: message.currencyPair});
                    if(message.data.length > 0) {
                        message.data.forEach(function(event){
                            onCandle({currencyPair:message.currencyPair, interval: message.interval, data:event})
                        })
                    }
                } else if (wsResponseMessage.meta.responseType === WsResponseMeta.WsResponseMsgType.CHANNEL_UNSUBSCRIBED) {
                    MessageClass = root.lookupType("protobuf.ws.ChannelUnsubscribedResponse");
                    message = MessageClass.decode(wsResponseMessage.msg);
                    var UnsubscribeRequest = root.lookupType("protobuf.ws.UnsubscribeRequest");
                    var channelType;
                    if(UnsubscribeRequest.ChannelType.TICKER === message.type) {
                        channelType = "ticker"
                    } else if (UnsubscribeRequest.ChannelType.ORDER_BOOK_RAW === message.type) {
                        channelType = "orderbookraw"
                    } else if (UnsubscribeRequest.ChannelType.ORDER_BOOK === message.type) {
                        channelType = "orderbook"
                    } else if (UnsubscribeRequest.ChannelType.TRADE === message.type) {
                        channelType = "trade"
                    } else if (UnsubscribeRequest.ChannelType.CANDLE === message.type) {
                        channelType = "candle"
                    }
                    onUnsubscribe({ channelType: channelType, currencyPair: message.currencyPair});
                } else if (wsResponseMessage.meta.responseType === WsResponseMeta.WsResponseMsgType.ERROR) {
                    MessageClass = root.lookupType("protobuf.ws.ErrorResponse");
                    message = MessageClass.decode(wsResponseMessage.msg);
                    onError(message);
                } else if (wsResponseMessage.meta.responseType === WsResponseMeta.WsResponseMsgType.TICKER_NOTIFY) {
                    MessageClass = root.lookupType("protobuf.ws.TickerNotification");
                    message = MessageClass.decode(wsResponseMessage.msg);
                    onTicker(message)
                } else if (wsResponseMessage.meta.responseType === WsResponseMeta.WsResponseMsgType.ORDER_BOOK_RAW_NOTIFY) {
                    MessageClass = root.lookupType("protobuf.ws.OrderBookRawNotification");
                    message = MessageClass.decode(wsResponseMessage.msg);
                    onOrderBookRaw(message)
                } else if (wsResponseMessage.meta.responseType === WsResponseMeta.WsResponseMsgType.ORDER_BOOK_NOTIFY) {
                    MessageClass = root.lookupType("protobuf.ws.OrderBookNotification");
                    message = MessageClass.decode(wsResponseMessage.msg);
                    onOrderBook(message)
                } else if (wsResponseMessage.meta.responseType === WsResponseMeta.WsResponseMsgType.TRADE_NOTIFY) {
                    MessageClass = root.lookupType("protobuf.ws.TradeNotification");
                    message = MessageClass.decode(wsResponseMessage.msg);
                    onTrade(message)
                } else if (wsResponseMessage.meta.responseType === WsResponseMeta.WsResponseMsgType.CandleNotification) {
                    MessageClass = root.lookupType("protobuf.ws.TradeNotification");
                    message = MessageClass.decode(wsResponseMessage.msg);
                    onCandle(message)
                }
            }
        };

        socket.onerror = function (error) {
            console.log("Websocket error " + error.message);
            //here you can make your trade decision
        };

        function onTicker(event) {
            console.log("ticker: " + JSON.stringify(event))
            //here you can make your trade decision
        }

        function onOrderBook(event) {
            console.log("orderbook: " + JSON.stringify(event))
            //here you can make your trade decision
        }

        function onOrderBookRaw(event) {
            console.log("orderbookraw: " + JSON.stringify(event))
            //here you can make your trade decision
        }

        function onTrade(event) {
            console.log("trade: " + JSON.stringify(event))
            //here you can make your trade decision
        }

        function onCandle(event) {
            console.log("candle: " + JSON.stringify(event))
        }


        function onError(msg) {
            console.log("Error: "  + JSON.stringify(msg))
            //here you can make your trade decision
        }

        function onSubscribe(msg) {

            console.log("channel subscribed: " + JSON.stringify(msg));
            //here you can make your trade decision
        }

        function onUnsubscribe(msg) {
            console.log("channel unsubscribed: " + JSON.stringify(msg))
            //here you can make your trade decision
        }

        function connect(path) {
            var connection = new WebSocket(path);
            connection.binaryType = 'arraybuffer';
            return connection;
        }

        function disconnect() {
            socket.close();
            console.log("Connection closed")
        }
    });
}