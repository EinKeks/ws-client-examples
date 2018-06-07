package model.params;

import model.ChannelTypes;

public class OrderBookRawParams extends Params {

    private Integer depth;

    public OrderBookRawParams(String symbol, Integer depth) {
        super(ChannelTypes.ORDERBOOKRAW, symbol);
        this.depth = depth;
    }

    public Integer getDepth() {
        return depth;
    }

    public void setDepth(Integer depth) {
        this.depth = depth;
    }

    @Override
    public String toString() {
        return "OrderBookRawParams{" +
                super.toString() +
                ", depth=" + depth +
                "} ";
    }
}
