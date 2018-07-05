package model.params;

import model.ChannelTypes;

public class UnsubscribeParams extends Params {

    public UnsubscribeParams(String symbol, String channelType) {
        super(channelType, symbol);
    }

    @Override
    public String toString() {
        return "UnsubscribeParams{" +
                super.toString() +
                "} ";
    }
}
