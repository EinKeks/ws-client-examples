"use strict";

var socket = connect("wss://ws.api.livecoin.net/ws/beta");
socket.onopen = function() {
    console.log("Connection established.");


    subscribe({
        "channelType": "ticker",
        "symbol": "BTC/USD",
        "frequency": 10.0
    });
    subscribe({
        "channelType": "orderbook",
        "symbol": "BTC/USD",
        "depth":1
    });
    subscribe({
        "channelType": "orderbookraw",
        "symbol": "BTC/USD",
        "depth":1
    });
    subscribe({
        "channelType": "trade",
        "symbol": "BTC/USD"
    });
    subscribe({
        "channelType": "candle",
        "symbol": "BTC/USD",
        "interval": "1m"
    });
    setTimeout(function () {
        unsubscribe("BTC/USD_ticker");
        unsubscribe("BTC/USD_orderbook");
        unsubscribe("BTC/USD_orderbookraw");
        unsubscribe("BTC/USD_trade");
        unsubscribe("BTC/USD_candle");
    }, 10000);
    setTimeout(disconnect, 30000)
    //here you can make your trade decision
};

socket.onclose = function(event) {
    if (event.wasClean) {
        console.log('The connection is closed cleanly');
    } else {
        console.log('Connection failure'); // например, "убит" процесс сервера
    }
    console.log('Code: ' + event.code + ' reason: ' + event.reason);
};

socket.onmessage = function(event) {
    // console.log("data received " + event.data);
    if(event.data !== '') {
        var msg = JSON.parse(event.data);
        var type;
        if (msg.hasOwnProperty('Error')) {
            onError(msg)
        } else if (msg.hasOwnProperty("operation")) {
            if (msg.operation.hasOwnProperty("Subscribe")) {
                onSubscribe(msg.channelId);
                if (msg.hasOwnProperty("data")) {
                    type = msg.channelId.split('_')[1];
                    msg.data.forEach(function (item) {
                        if (type === 'orderbook') {
                            onOrderBook(item)
                        } else if (type === 'orderbookraw') {
                            onOrderBookRaw(item)
                        } else if(type === 'candle') {
                            onCandle(event)
                        }
                    })

                }
            } else if (msg.operation.hasOwnProperty("Unsubscribe")) {
                onUnsubscribe(msg.channelId)
            } else {
                console.log("Unsupported operation")
            }
        } else {
            type = msg.channelId.split('_')[1];
            if (type === 'ticker') {
                onTicker(msg)
            } else if (type === 'orderbook') {
                onOrderBook(msg)
            } else if (type === 'orderbookraw') {
                onOrderBookRaw(msg)
            } else if (type === 'trade') {
                onTrade(msg)
            } else if (type === 'candle') {
                onCandle(msg)
            }
        }
    }
};

socket.onerror = function(error) {
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


function onError(event) {
    console.log("Server error: " + JSON.stringify(event))
    //here you can make your trade decision
}

function onSubscribe(channelId) {
    console.log("channel subscribed: " + channelId)
    //here you can make your trade decision
}

function onUnsubscribe(channelId) {
    console.log("channel unsubscribed: " + channelId)
    //here you can make your trade decision
}

function subscribe(params) {
    socket.send(JSON.stringify({"Subscribe":params}))
}

function unsubscribe(channelId) {
    socket.send(JSON.stringify({
        "Unsubscribe": {
            "channelId":channelId
        }
    }))
}

function connect(path) {
    return  new WebSocket(path);
}

function disconnect() {
    socket.close();
    console.log("Connection closed")
}
