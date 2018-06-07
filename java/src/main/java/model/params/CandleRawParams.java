package model.params;

import model.ChannelTypes;

public class CandleRawParams extends Params {

    private String interval;

    public CandleRawParams(String symbol, String interval) {
        super(ChannelTypes.CANDLERAW, symbol);
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
        return "CandleRawParams{" +
                super.toString() +
                ", interval=" + interval +
                "} ";
    }
}
