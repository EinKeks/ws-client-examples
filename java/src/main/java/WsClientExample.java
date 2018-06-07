import com.google.gson.*;
import com.neovisionaries.ws.client.WebSocket;
import com.neovisionaries.ws.client.WebSocketAdapter;
import com.neovisionaries.ws.client.WebSocketException;
import com.neovisionaries.ws.client.WebSocketFactory;
import model.ChannelTypes;
import model.events.*;
import model.params.*;
import sun.reflect.generics.reflectiveObjects.NotImplementedException;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class WsClientExample {
    private WebSocket webSocket;
    private Gson mapper = new Gson();

    public WsClientExample() throws IOException {
        webSocket = new WebSocketFactory()
                .createSocket("wss://ws.api.livecoin.net/ws/beta")
                .addListener(new WebSocketAdapter() {
                    @Override
                    public void onTextMessage(WebSocket ws, String message) {
                        if (message != null) {
                            parseMessage(message);
                        }
                    }
                });
    }

    public static void main(String[] args) throws IOException, InterruptedException {

        WsClientExample app = new WsClientExample();
        app.run();
    }

    private void run() throws IOException, InterruptedException {
        try {
            webSocket.connect();
            subscribeTicker("BTC/USD",null);
            subscribeTicker("BTC/USD",10f);
            subscribeOrderBook("BTC/USD",1);
            unsubscribeOrderBook("BTC/USD");
            subscribeOrderBook("BTC/USD",10);
            subscribeOrderBookRaw("BTC/USD",10);
            subscribeTrade("BTC/USD");
            subscribeCandleRaw("BTC/USD","1m");

        } catch (WebSocketException e) {
            e.printStackTrace();
        }
        if (webSocket != null) {
            BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
            System.out.print("Press Enter to exit\n");
            br.readLine();
            unsubscribeTicker("BTC/USD");
            unsubscribeOrderBook("BTC/USD");
            unsubscribeOrderBookRaw("BTC/USD");
            unsubscribeTrade("BTC/USD");
            unsubscribeCandle("BTC/USD");
            Thread.sleep(5000);
            stop();

        }
    }

    private void onTicker(TickerEvent tickerEvent) {
        System.out.print(tickerEvent);
        //here you can make your trade decision
    }

    private void onOrderBook(OrderBookEvent orderBookEvent) {
        System.out.println(orderBookEvent);
        //here you can make your trade decision
    }

    private void onOrderBookRaw(OrderBookRawEvent orderBookRawEvent) {
        System.out.println(orderBookRawEvent);
        //here you can make your trade decision
    }

    private void onTrade(TradeEvent tradeEvent) {
        System.out.println(tradeEvent);
        //here you can make your trade decision
    }

    private void onCandleRaw(CandleRawEvent candleRawEvent) {
        System.out.println(candleRawEvent);
        //here you can make your trade decision
    }

    private void onError(String errorName, String badRequest) {
        System.out.println("Error: \"" + errorName + "\",text:\""+badRequest+"\"");
        //here you can make your trade decision
    }

    private void onSubscribe(String channelId) {
        System.out.println("Channel subscribed: "+ channelId);
        //here you can make your trade decision
    }

    private void onUnsubscribe(String channelId) {
        System.out.println("Channel unSubscribed: "+ channelId);
        //here you can make your trade decision
    }

    private void stop() {
        webSocket.disconnect();
        System.exit(0);
    }

    private void subscribeTicker(String symbol, Float frequency) {
        subscribe(new TickerParams(symbol,frequency));
    }

    private void subscribeOrderBook(String symbol, Integer depth) {
        subscribe(new OrderBookParams(symbol, depth));
    }
    private void subscribeOrderBookRaw(String symbol, Integer depth) {
        subscribe(new OrderBookRawParams(symbol, depth));
    }
    private void subscribeTrade(String symbol) {
        subscribe(new TradeParams(symbol));
    }

    private void subscribeCandleRaw(String symbol, String interval) {
        subscribe(new CandleRawParams(symbol, interval));
    }

    private void subscribe(Params params) {
        webSocket.sendText(String.format("{\"Subscribe\":%s}",mapper.toJson(params)));
    }

    private void unsubscribeTicker(String symbol) {
        unsubscribeChannel(String.format("%s_%s",symbol,ChannelTypes.TICKER));
    }
    private void unsubscribeOrderBook(String symbol) {
        unsubscribeChannel(String.format("%s_%s",symbol,ChannelTypes.ORDERBOOK));
    }
    private void unsubscribeOrderBookRaw(String symbol) {
        unsubscribeChannel(String.format("%s_%s",symbol,ChannelTypes.ORDERBOOKRAW));
    }
    private void unsubscribeTrade(String symbol) {
        unsubscribeChannel(String.format("%s_%s",symbol,ChannelTypes.TRADE));
    }
    private void unsubscribeCandle(String symbol) {
        unsubscribeChannel(String.format("%s_%s",symbol,ChannelTypes.CANDLERAW));
    }
    private void unsubscribeChannel(String channelId) {
        webSocket.sendText(String.format("{\"Unsubscribe\":{\"channelId\":\"%s\"}}",channelId));
    }

    private void parseMessage(String message){
        JsonParser parser = new JsonParser();
        JsonObject mainObject = parser.parse(message).getAsJsonObject();
        if (mainObject.has("Error")) {
            String errorName = mainObject.get("Error").getAsString();
            String badRequest = mainObject.get("text").getAsString();
            onError(errorName,badRequest);
        } else if(mainObject.has("operation")) {
            String channelId = mainObject.get("channelId").getAsString();
            String type = channelId.split("_")[1];
            JsonObject operation = mainObject.getAsJsonObject("operation");
            if(operation.has("Subscribe")) {
                onSubscribe(channelId);
                if(mainObject.has("data") &&! mainObject.get("data").isJsonNull()) {
                    JsonArray data = mainObject.getAsJsonArray("data");
                    data.forEach((JsonElement t) -> {
                        if (type.equals(ChannelTypes.ORDERBOOK)) {
                            OrderBookEvent orderBookEvent = jsonToOrderBookEvent(t.getAsJsonObject());
                            orderBookEvent.setChannelId(channelId);
                            onOrderBook(orderBookEvent);
                        } else if (type.equals(ChannelTypes.ORDERBOOKRAW)) {
                            OrderBookRawEvent orderBookRawEvent = jsonToOrderBookRawEvent(t.getAsJsonObject());
                            orderBookRawEvent.setChannelId(channelId);
                            onOrderBookRaw(orderBookRawEvent);
                        } else if (type.equals(ChannelTypes.CANDLERAW)) {
                            CandleRawEvent candleRawEvent = jsonToCandleRawEvent(t.getAsJsonObject());
                            candleRawEvent.setChannelId(channelId);
                            onCandleRaw(candleRawEvent);
                        } else throw new UnsupportedOperationException();;
                    });
                }
            } else if (operation.has("Unsubscribe")) {
                onUnsubscribe(channelId);
            } else {
                throw new UnsupportedOperationException();
            }
        } else {
            String channelId = mainObject.get("channelId").getAsString();
            String type = channelId.split("_")[1];
            if(type.equals(ChannelTypes.TICKER)) {
                onTicker(jsonToTickerEvent(mainObject));
            } else if (type.equals(ChannelTypes.ORDERBOOK)) {
                onOrderBook(jsonToOrderBookEvent(mainObject));
            } else if (type.equals(ChannelTypes.ORDERBOOKRAW)) {
                onOrderBookRaw(jsonToOrderBookRawEvent(mainObject));
            } else if (type.equals(ChannelTypes.TRADE)) {
                onTrade(jsonToTradeEvent(mainObject));
            } else if (type.equals(ChannelTypes.CANDLERAW)) {
                onCandleRaw(jsonToCandleRawEvent(mainObject));
            }
            else throw new UnsupportedOperationException();;
        }
    }

    private TickerEvent jsonToTickerEvent(JsonObject json) {
        TickerEvent event = new TickerEvent();
        if(json.has("channelId")) {
            event.setChannelId(json.get("channelId").getAsString());
        }
        if(json.has("last")) {
            event.setLast(json.get("last").getAsBigDecimal());
        }
        if(json.has("high")) {
            event.setHigh(json.get("high").getAsBigDecimal());
        }
        if(json.has("low")) {
            event.setLow(json.get("low").getAsBigDecimal());
        }
        if(json.has("volume")) {
            event.setVolume(json.get("volume").getAsBigDecimal());
        }
        if(json.has("vwap")) {
            event.setVwap(json.get("vwap").getAsBigDecimal());
        }
        if(json.has("maxBid")) {
            event.setMaxBid(json.get("maxBid").getAsBigDecimal());
        }
        if(json.has("minAsk")) {
            event.setMinAsk(json.get("minAsk").getAsBigDecimal());
        }
        if(json.has("bestBid")) {
            event.setBestBid(json.get("bestBid").getAsBigDecimal());
        }
        if(json.has("bestAsk")) {
            event.setBestAsk(json.get("bestAsk").getAsBigDecimal());
        }
        return event;
    }

    private OrderBookEvent jsonToOrderBookEvent(JsonObject json) {
        OrderBookEvent event = new OrderBookEvent();

        if(json.has("channelId")) {
            event.setChannelId(json.get("channelId").getAsString());
        }
        if(json.has("price")) {
            event.setPrice(json.get("price").getAsBigDecimal());
        }
        if(json.has("quantity")) {
            event.setQuantity(json.get("quantity").getAsBigDecimal());
        }
        return event;
    }

    private OrderBookRawEvent jsonToOrderBookRawEvent(JsonObject json) {
        OrderBookRawEvent event = new OrderBookRawEvent();
        if(json.has("channelId")) {
            event.setChannelId(json.get("channelId").getAsString());
        }
        if(json.has("id")) {
            event.setId(json.get("id").getAsLong());
        }
        if(json.has("price")) {
            event.setPrice(json.get("price").getAsBigDecimal());
        }
        if(json.has("quantity")) {
            event.setQuantity(json.get("quantity").getAsBigDecimal());
        }
        return event;
    }

    private TradeEvent jsonToTradeEvent(JsonObject json) {
        TradeEvent event = new TradeEvent();
        if(json.has("channelId")) {
            event.setChannelId(json.get("channelId").getAsString());
        }
        if(json.has("id")) {
            event.setId(json.get("id").getAsLong());
        }
        if(json.has("timestamp")) {
            event.setTimestamp(json.get("timestamp").getAsLong());
        }
        if(json.has("price")) {
            event.setPrice(json.get("price").getAsBigDecimal());
        }
        if(json.has("quantity")) {
            event.setQuantity(json.get("quantity").getAsBigDecimal());
        }
        return  event;
    }

    private CandleRawEvent jsonToCandleRawEvent(JsonObject json) {
        CandleRawEvent event = new CandleRawEvent();
        if(json.has("channelId")) {
            event.setChannelId(json.get("channelId").getAsString());
        }
        if(json.has("timestamp")) {
            event.setTimestamp(json.get("timestamp").getAsLong());
        }
        if(json.has("open")) {
            event.setOpen(json.get("open").getAsBigDecimal());
        }
        if(json.has("close")) {
            event.setClose(json.get("close").getAsBigDecimal());
        }
        if(json.has("high")) {
            event.setHigh(json.get("high").getAsBigDecimal());
        }
        if(json.has("low")) {
            event.setLow(json.get("low").getAsBigDecimal());
        }
        if(json.has("volume")) {
            event.setVolume(json.get("volume").getAsBigDecimal());
        }
        if(json.has("quantity")) {
            event.setQuantity(json.get("price").getAsBigDecimal());
        }
        return event;
    }
}
