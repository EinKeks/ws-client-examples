package model.params;

import model.ChannelTypes;

public class TradeParams extends Params {

    public TradeParams(String symbol) {
        super(ChannelTypes.TRADE, symbol);
    }

    @Override
    public String toString() {
        return "TickerParams{" +
                super.toString() +
                "} ";
    }
}
