package model.params;

import model.ChannelTypes;

public class OrderBookParams extends Params {

    private Integer depth;

    public OrderBookParams(String symbol, Integer depth) {
        super(ChannelTypes.ORDERBOOK, symbol);
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
        return "OrderBookParams{" +
                super.toString() +
                ", depth=" + depth +
                "} ";
    }
}
