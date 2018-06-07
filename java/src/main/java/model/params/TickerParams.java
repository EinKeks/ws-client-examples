package model.params;

import model.ChannelTypes;

public class TickerParams extends Params {

    private Float frequency;

    public TickerParams(String symbol, Float frequency) {
        super(ChannelTypes.TICKER, symbol);
        this.frequency = frequency;
    }

    public Float getFrequency() {
        return frequency;
    }

    public void setFrequency(Float frequency) {
        this.frequency = frequency;
    }

    @Override
    public String toString() {
        return "TickerParams{" +
                super.toString() +
                ", frequency=" + frequency +
                "} ";
    }
}
