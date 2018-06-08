package model.params;

import model.ChannelTypes;

public class CandleParams extends Params {

    private String interval;

    public CandleParams(String symbol, String interval) {
        super(ChannelTypes.CANDLE, symbol);
        this.interval = interval;
    }

    public String getInterval() {
        return interval;
    }

    public void setInterval(String interval) {
        this.interval = interval;
    }

    @Override
    public String toString() {
        return "CandleParams{" +
                super.toString() +
                ", interval=" + interval +
                "} ";
    }
}
