import com.google.gson.*;
import com.neovisionaries.ws.client.WebSocket;
import com.neovisionaries.ws.client.WebSocketAdapter;
import com.neovisionaries.ws.client.WebSocketException;
import com.neovisionaries.ws.client.WebSocketFactory;
import model.ChannelTypes;
import model.events.*;
import model.params.*;
import serializers.ChannelCodes;
import serializers.CustomSerializers;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class WsClientExample {
    private WebSocket webSocket;
    private Gson mapper;

    public WsClientExample() throws IOException {
        mapper = new GsonBuilder()
                .registerTypeAdapter(TickerParams.class, CustomSerializers.ticker)
                .registerTypeAdapter(OrderBookRawParams.class, CustomSerializers.orderBookRaw)
                .registerTypeAdapter(OrderBookParams.class, CustomSerializers.orderBook)
                .registerTypeAdapter(TradeParams.class, CustomSerializers.trade)
                .registerTypeAdapter(CandleParams.class, CustomSerializers.candle)
                .registerTypeAdapter(UnsubscribeParams.class, CustomSerializers.unsubscribe)
                .create();

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
            subscribeTicker("BTC/USD", null);
            subscribeTicker("BTC/USD", 10f);
            subscribeOrderBook("BTC/USD", 1);
            unsubscribeOrderBook("BTC/USD");
            subscribeOrderBook("BTC/USD", 10);
            subscribeOrderBookRaw("BTC/USD", 10);
            subscribeTrade("BTC/USD");
            subscribeCandle("BTC/USD", "1m");

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

    private void onCandle(CandleEvent candleEvent) {
        System.out.println(candleEvent);
        //here you can make your trade decision
    }

    private void onError(String errorName, String badRequest) {
        System.out.println("Error: \"" + errorName + "\",text:\"" + badRequest + "\"");
        //here you can make your trade decision
    }

    private void onSubscribe(String channelId) {
        System.out.println("Channel subscribed: " + channelId);
        //here you can make your trade decision
    }

    private void onUnsubscribe(String channelId) {
        System.out.println("Channel unSubscribed: " + channelId);
        //here you can make your trade decision
    }

    private void stop() {
        webSocket.disconnect();
        System.exit(0);
    }

    private void subscribeTicker(String symbol, Float frequency) {
        subscribe(mapper.toJson(new TickerParams(symbol, frequency)));
    }

    private void subscribeOrderBook(String symbol, Integer depth) {
        subscribe(mapper.toJson(new OrderBookParams(symbol, depth)));
    }

    private void subscribeOrderBookRaw(String symbol, Integer depth) {
        subscribe(mapper.toJson(new OrderBookRawParams(symbol, depth)));
    }

    private void subscribeTrade(String symbol) {
        subscribe(mapper.toJson(new TradeParams(symbol)));
    }

    private void subscribeCandle(String symbol, String interval) {
        subscribe(mapper.toJson(new CandleParams(symbol, interval)));
    }

    private void subscribe(String request) {
        System.out.println("Send: " +request);
        webSocket.sendText(request);
    }

    private void unsubscribeTicker(String symbol) {
        unsubscribeChannel(new UnsubscribeParams(symbol, ChannelTypes.TICKER));
    }

    private void unsubscribeOrderBook(String symbol) {
        unsubscribeChannel(new UnsubscribeParams(symbol, ChannelTypes.ORDERBOOK));
    }

    private void unsubscribeOrderBookRaw(String symbol) {
        unsubscribeChannel(new UnsubscribeParams(symbol, ChannelTypes.ORDERBOOKRAW));
    }

    private void unsubscribeTrade(String symbol) {
        unsubscribeChannel(new UnsubscribeParams(symbol,ChannelTypes.TRADE));
    }

    private void unsubscribeCandle(String symbol) {
        unsubscribeChannel(new UnsubscribeParams(symbol, ChannelTypes.CANDLE));
    }

    private void unsubscribeChannel(UnsubscribeParams params) {
        System.out.println("Send: " + mapper.toJson(params));
        webSocket.sendText(mapper.toJson(params));
    }

    private void parseMessage(String message) {
        JsonParser parser = new JsonParser();
        JsonArray values = parser.parse(message).getAsJsonArray();
        if(values.get(0).getAsString().equals("s")) {
            //subscribe channel
            onSubscribe(ChannelCodes.channelCodesToTypes(values.get(2).getAsJsonArray().get(0).getAsString()) + "_" + values.get(2).getAsJsonArray().get(1).getAsString());
            processEvents(values);
        } else if (values.get(0).getAsString().equals("u")) {
            //unsubscribe channel
            onSubscribe(ChannelCodes.channelCodesToTypes(values.get(2).getAsJsonArray().get(0).getAsString()) + "_" + values.get(2).getAsJsonArray().get(1).getAsString());
        } else if(values.get(0).getAsString().equals("e")) {
            onError(values.get(1).getAsJsonArray().get(0).getAsString(),values.get(1).getAsJsonArray().get(2).getAsString());
            //error
        } else {
            //event notify
            processEvents(values);
        }
    }

    private void processEvents(JsonArray array) {
        int size = arraySize(array);
        String channelCode = extractChannelCode(array);
        String channelType = ChannelCodes.channelCodesToTypes(channelCode);
        String currencyPair = array.get(2).getAsJsonArray().get(1).getAsString();
        String channelId = String.format("%s_%s",channelType,currencyPair);
        if (size > 2) {
            for (int i = 2; i < size; i++) {
                processEvent(channelType, channelId, array.get(2).getAsJsonArray().get(i).getAsJsonArray());
            }
        }

    }

    private String extractChannelCode(JsonArray array) {
        return array.get(2).getAsJsonArray().get(0).getAsString();
    }

    private Integer arraySize(JsonArray array) {
        return array.get(2).getAsJsonArray().size();
    }

    private void processEvent(String channelType, String channelId,JsonArray srcEvent) {
        if(ChannelTypes.TICKER.equals(channelType)) {
            TickerEvent event = jsonToTickerEvent(srcEvent);
            event.setChannelId(channelId);
            onTicker(event);
        } else if(ChannelTypes.ORDERBOOKRAW.equals(channelType)) {
            OrderBookRawEvent event = jsonToOrderBookRawEvent(srcEvent);
            event.setChannelId(channelId);
            onOrderBookRaw(event);
        } else if (ChannelTypes.ORDERBOOK.equals(channelType)) {
            OrderBookEvent event = jsonToOrderBookEvent(srcEvent);
            event.setChannelId(channelId);
            onOrderBook(event);
        } else if (ChannelTypes.TRADE.equals(channelType)) {
            TradeEvent event = jsonToTradeEvent(srcEvent);
            event.setChannelId(channelId);
            onTrade(event);
        } else if (ChannelTypes.CANDLE.equals(channelType)) {
            CandleEvent event = jsonToCandleEvent(srcEvent);
            event.setChannelId(channelId);
            onCandle(event);
        }
    }

    private TickerEvent jsonToTickerEvent(JsonArray json) {
        TickerEvent event = new TickerEvent();
        event.setChanged(json.get(0).getAsLong());
        event.setLast(json.get(1).getAsBigDecimal());
        event.setHigh(json.get(2).getAsBigDecimal());
        event.setLow(json.get(3).getAsBigDecimal());
        event.setVolume(json.get(4).getAsBigDecimal());
        event.setVwap(json.get(5).getAsBigDecimal());
        event.setMaxBid(json.get(6).getAsBigDecimal());
        event.setMinAsk(json.get(7).getAsBigDecimal());
        event.setBestBid(json.get(8).getAsBigDecimal());
        event.setBestAsk(json.get(8).getAsBigDecimal());
        return event;
    }

    private OrderBookEvent jsonToOrderBookEvent(JsonArray json) {
        OrderBookEvent event = new OrderBookEvent();
        event.setChanged(json.get(0).getAsLong());
        event.setPrice(json.get(1).getAsBigDecimal());
        event.setQuantity(json.get(2).getAsBigDecimal());
        return event;
    }

    private OrderBookRawEvent jsonToOrderBookRawEvent(JsonArray json) {
        OrderBookRawEvent event = new OrderBookRawEvent();
        event.setId(json.get(0).getAsLong());
        event.setChanged(json.get(1).getAsLong());
        event.setPrice(json.get(2).getAsBigDecimal());
        event.setQuantity(json.get(3).getAsBigDecimal());
        return event;
    }

    private TradeEvent jsonToTradeEvent(JsonArray json) {
        TradeEvent event = new TradeEvent();
        event.setId(json.get(0).getAsLong());
        event.setTimestamp(json.get(1).getAsLong());
        event.setPrice(json.get(2).getAsBigDecimal());
        event.setQuantity(json.get(3).getAsBigDecimal());
        return event;
    }

    private CandleEvent jsonToCandleEvent(JsonArray json) {
        CandleEvent event = new CandleEvent();
        event.setT(json.get(0).getAsLong());
        event.setO(json.get(1).getAsBigDecimal());
        event.setC(json.get(2).getAsBigDecimal());
        event.setH(json.get(3).getAsBigDecimal());
        event.setL(json.get(4).getAsBigDecimal());
        event.setV(json.get(5).getAsBigDecimal());
        event.setQ(json.get(6).getAsBigDecimal());
        return event;
    }
}
