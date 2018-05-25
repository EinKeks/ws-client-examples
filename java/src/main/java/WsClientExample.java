import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.neovisionaries.ws.client.WebSocket;
import com.neovisionaries.ws.client.WebSocketAdapter;
import com.neovisionaries.ws.client.WebSocketException;
import com.neovisionaries.ws.client.WebSocketFactory;
import model.OrderBookEvent;
import model.OrderBookRawEvent;
import model.TickerEvent;
import model.TradeEvent;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Locale;

public class WsClientExample {
    private WebSocket webSocket;

    public WsClientExample() throws IOException {
        webSocket = new WebSocketFactory()
                .createSocket("ws://ws.api.livecoin.net/ws/beta")
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
            subscribeOrderBook("BTC/USD",null);
            unsubscribeOrderBook("BTC/USD");
            subscribeOrderBook("BTC/USD",10);
            subscribeOrderBookRaw("BTC/USD",10);
            subscribeTrade("BTC/USD");

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
        subscribe("ticker",symbol,frequency,null);
    }

    private void subscribeOrderBook(String symbol, Integer depth) {
        subscribe("orderbook",symbol,null, depth);
    }
    private void subscribeOrderBookRaw(String symbol, Integer depth) {
        subscribe("orderbookraw", symbol, null, depth);
    }
    private void subscribeTrade(String symbol) {
        subscribe("trade",symbol, null, null);
    }

    private void subscribe(String type, String symbol, Float frequency, Integer depth) {
        webSocket.sendText(String.format("{\"Subscribe\":{\"channelType\":\"%s\",\"symbol\":\"%s\"%s%s}}",
                type,
                symbol,
                frequency == null?"":String.format(Locale.US,",\"frequency\":%f",frequency),
                depth == null ? "": String.format(",\"depth\":%d",depth)
                ));
    }
    private void unsubscribeTicker(String symbol) {
        unsubscribeChannel(String.format("%s_%s",symbol,"ticker"));
    }
    private void unsubscribeOrderBook(String symbol) {
        unsubscribeChannel(String.format("%s_%s",symbol,"orderbook"));
    }
    private void unsubscribeOrderBookRaw(String symbol) {
        unsubscribeChannel(String.format("%s_%s",symbol,"orderbookraw"));
    }
    private void unsubscribeTrade(String symbol) {
        unsubscribeChannel(String.format("%s_%s",symbol,"trade"));
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
                        if (type.equals("orderbook")) {
                            OrderBookEvent orderBookEvent = jsonToOrderBookEvent(t.getAsJsonObject());
                            orderBookEvent.setChannelId(channelId);
                            onOrderBook(orderBookEvent);
                        } else {
                            OrderBookRawEvent orderBookRawEvent = jsonToOrderBookRawEvent(t.getAsJsonObject());
                            orderBookRawEvent.setChannelId(channelId);
                            onOrderBookRaw(orderBookRawEvent);
                        }
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
            if(type.equals("ticker")) {
                onTicker(jsonToTickerEvent(mainObject));
            } else if (type.equals("orderbook")) {
                onOrderBook(jsonToOrderBookEvent(mainObject));
            } else if (type.equals("orderbookraw")) {
                onOrderBookRaw(jsonToOrderBookRawEvent(mainObject));
            } else if (type.equals("trade")) {
                onTrade(jsonToTradeEvent(mainObject));
            }
        }
    }

    private TickerEvent jsonToTickerEvent(JsonObject json) {
        TickerEvent event = new TickerEvent();
        if(json.has("channelId")) {
            event.setChannelId(json.get("channelId").getAsString());
        }
        if(json.has("version")) {
            event.setVersion(json.get("version").getAsLong());
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
        if(json.has("version")) {
            event.setVersion(json.get("version").getAsLong());
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
        if(json.has("version")) {
            event.setVersion(json.get("version").getAsLong());
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
        if(json.has("version")) {
            event.setVersion(json.get("version").getAsLong());
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
}
