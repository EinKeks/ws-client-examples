package serializers;

import com.google.gson.JsonArray;
import com.google.gson.JsonSerializer;
import model.params.*;

public class CustomSerializers {

    public static JsonSerializer<TickerParams> ticker = (src, typeOfSrc, context) -> {
        JsonArray result = new JsonArray();
        result.add((String)null);
        result.add("s");
        result.add("t");
        result.add(src.getSymbol());
        result.add(src.getFrequency());
        return result;
    };

    public static JsonSerializer<OrderBookRawParams> orderBookRaw = (src, typeOfSrc, context) -> {
        JsonArray result = new JsonArray();
        result.add((String)null);
        result.add("s");
        result.add("r");
        result.add(src.getSymbol());
        result.add(src.getDepth());
        return result;
    };

    public static  JsonSerializer<OrderBookParams> orderBook = (src, typeOfSrc, context) -> {
        JsonArray result = new JsonArray();
        result.add((String)null);
        result.add("s");
        result.add("o");
        result.add(src.getSymbol());
        result.add(src.getDepth());
        return result;
    };

    public static  JsonSerializer<TradeParams> trade = (src, typeOfSrc, context) -> {
        JsonArray result = new JsonArray();
        result.add((String)null);
        result.add("s");
        result.add("d");
        result.add(src.getSymbol());
        return result;
    };

    public static  JsonSerializer<CandleParams> candle = (src, typeOfSrc, context) -> {
        JsonArray result = new JsonArray();
        result.add((String)null);
        result.add("s");
        result.add("c");
        result.add(src.getSymbol());
        result.add(src.getInterval());
        return result;
    };

    public static JsonSerializer<UnsubscribeParams> unsubscribe = (src, typeOfSrc, context) -> {
        JsonArray result = new JsonArray();
        result.add((String)null);
        result.add("u");
        result.add(ChannelCodes.channelTypesToCodes(src.getChannelType()));
        result.add(src.getSymbol());
        return result;
    };
}
