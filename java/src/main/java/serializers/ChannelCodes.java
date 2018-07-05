package serializers;

import model.ChannelTypes;

public class ChannelCodes {
    final public static String TRADE = "d";
    final public static String TICKER = "t";
    final public static String ORDERBOOK = "o";
    final public static String ORDERBOOKRAW = "r";
    final public static String CANDLE = "c";

    final public static String channelTypesToCodes(String channelType) {
        String result = null;
        if(channelType.equals(ChannelTypes.TRADE)) {
            result = ChannelCodes.TRADE;
        } else if(channelType.equals(ChannelTypes.TICKER)) {
            result = ChannelCodes.TICKER;
        } else if(channelType.equals(ChannelTypes.ORDERBOOK)) {
            result = ChannelCodes.ORDERBOOK;
        } else if(channelType.equals(ChannelTypes.ORDERBOOKRAW)) {
            result = ChannelCodes.ORDERBOOKRAW;
        } else if(channelType.equals(ChannelTypes.CANDLE)) {
            result = ChannelCodes.CANDLE;
        }
        return result;
    }

    final public static String channelCodesToTypes(String channelCode) {
        String result = null;
        if(channelCode.equals(ChannelCodes.TRADE)) {
            result = ChannelTypes.TRADE;
        } else if(channelCode.equals(ChannelCodes.TICKER)) {
            result = ChannelTypes.TICKER;
        } else if(channelCode.equals(ChannelCodes.ORDERBOOK)) {
            result = ChannelTypes.ORDERBOOK;
        } else if(channelCode.equals(ChannelCodes.ORDERBOOKRAW)) {
            result = ChannelTypes.ORDERBOOKRAW;
        } else if(channelCode.equals(ChannelCodes.CANDLE)) {
            result = ChannelTypes.CANDLE;
        }
        return result;
    }
}
