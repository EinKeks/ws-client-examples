"use strict";

var socket = connect("wss://ws.api.livecoin.net/ws/beta");
socket.onopen = function() {
    console.log("Connection established.");

    subscribe(null, "t", "BTC/USD", 10.0);
    subscribe(null, "o", "BTC/USD", 1);
    subscribe(null, "r", "BTC/USD", 1);
    subscribe(null, "d", "BTC/USD", null);
    subscribe(null, "c", "BTC/USD", "1m");

    setTimeout(function () {
        unsubscribe(null,"BTC/USD", "t");
        unsubscribe(null,"BTC/USD", "r");
        unsubscribe(null,"BTC/USD", "o");
        unsubscribe(null,"BTC/USD", "d");
        unsubscribe(null,"BTC/USD", "c");
    }, 120000);
    setTimeout(disconnect, 140000)
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
        if(msg[0] === "s") {
            //subscribe action
            onSubscribe(msg);
            var events = extractEventsFromSubscribe(msg[1]);
            if(msg[1][0] === "t") {
                //ticker
                events.forEach(function(event){
                    onTicker(event)
                })
            } else if (msg[1][0] === "r") {
                //orderbookraw
                events.forEach(function(event){
                    onOrderBookRaw(event)
                })
            } else if (msg[1][0] === "o") {
                //orderbook
                events.forEach(function(event){
                    onOrderBook(event)
                })
            } else if (msg[1][0] === "d") {
                //trade
                events.forEach(function(event){
                    onTrade(event)
                })
            } else if (msg[1][0] === "c") {
                //candle
                events.forEach(function(event){
                    onCandle(event)
                })
            }
        } else if (msg[0] === "u") {
            //unsubscribe action
            onUnsubscribe(msg)
        } else if (msg[0] === "e") {
            //error event
            onError(msg)
        } else {
            //channel event
            events = exctractEvent(msg[1]);
            if(msg[1] === "t") {
                //ticker
                events.forEach(function(event){
                    onTicker(event)
                })
            } else if (msg[1] === "r") {
                //orderbookraw
                events.forEach(function(event){
                    onOrderBookRaw(event)
                })
            } else if (msg[1] === "o") {
                //orderbook
                events.forEach(function(event){
                    onOrderBook(event)
                })
            } else if (msg[1] === "d") {
                //trade
                events.forEach(function(event){
                    onTrade(event)
                })
            } else if (msg[1] === "c") {
                //candle
                events.forEach(function(event){
                    onCandle(event)
                })
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


function onError(msg) {
    console.log("Error: " + "\ntext: " + msg[1][0] + "\ncode: " + msg[1][1] + "\nmessage: " + msg[1][2])
    //here you can make your trade decision
}

function onSubscribe(msg) {

    console.log("channel subscribed: " + channelFromCode(msg[1][0]) + '_' + msg[1][1])
    //here you can make your trade decision
}

function onUnsubscribe(msg) {
    console.log("channel unsubscribed: " + channelFromCode(msg[1][0]) + '_' + msg[1][1])
    //here you can make your trade decision
}

function subscribe(token, code, currencyPair, param) {
    socket.send(JSON.stringify([token,"s", code, currencyPair, param]))
}

function unsubscribe(token, currencyPair, channelId) {
    socket.send(JSON.stringify([token, "u", channelId, currencyPair]))
}

function connect(path) {
    return  new WebSocket(path);
}

function disconnect() {
    socket.close();
    console.log("Connection closed")
}

function channelFromCode(code) {
    var channel;
    if(code === "t") {
        channel = "ticker";
    } else if (code === "r") {
        channel = "orderbookraw";
    } else if (code === "o") {
        channel = "orderbook";
    } else if (code === "d") {
        channel = "trade";
    } else if (code === "c") {
        channel = "candle"
    }
    return channel;
}
function extractEventsFromSubscribe(msg) {
    var result = [];
    var length = msg.length;
    if( length > 3) {
        for(var i = 3; i < length - 1; i++) {
            result.push(msg[i])
        }
    }
    return result
}
function exctractEvent(msg) {
    var result = [];
    var length = msg.length;
    if( length > 2) {
        for(var i = 2; i < length - 1; i++) {
            result.push(msg[i])
        }
    }
    return result
}
