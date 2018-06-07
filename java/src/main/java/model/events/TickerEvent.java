package model.events;

import java.math.BigDecimal;

public class TickerEvent {
    private String channelId;
    private BigDecimal last;
    private BigDecimal high;
    private BigDecimal low;
    private BigDecimal volume;
    private BigDecimal vwap;
    private BigDecimal maxBid;
    private BigDecimal minAsk;
    private BigDecimal bestBid;
    private BigDecimal bestAsk;

    public String getChannelId() {
        return channelId;
    }

    public void setChannelId(String channelId) {
        this.channelId = channelId;
    }

    public BigDecimal getLast() {
        return last;
    }

    public void setLast(BigDecimal last) {
        this.last = last;
    }

    public BigDecimal getHigh() {
        return high;
    }

    public void setHigh(BigDecimal high) {
        this.high = high;
    }

    public BigDecimal getLow() {
        return low;
    }

    public void setLow(BigDecimal low) {
        this.low = low;
    }

    public BigDecimal getVolume() {
        return volume;
    }

    public void setVolume(BigDecimal volume) {
        this.volume = volume;
    }

    public BigDecimal getVwap() {
        return vwap;
    }

    public void setVwap(BigDecimal vwap) {
        this.vwap = vwap;
    }

    public BigDecimal getMaxBid() {
        return maxBid;
    }

    public void setMaxBid(BigDecimal maxBid) {
        this.maxBid = maxBid;
    }

    public BigDecimal getMinAsk() {
        return minAsk;
    }

    public void setMinAsk(BigDecimal minAsk) {
        this.minAsk = minAsk;
    }

    public BigDecimal getBestBid() {
        return bestBid;
    }

    public void setBestBid(BigDecimal bestBid) {
        this.bestBid = bestBid;
    }

    public BigDecimal getBestAsk() {
        return bestAsk;
    }

    public void setBestAsk(BigDecimal bestAsk) {
        this.bestAsk = bestAsk;
    }

    @Override
    public String toString() {
        return "Ticker{" +
                "channelId='" + channelId + '\'' +
                ", last=" + last +
                ", high=" + high +
                ", low=" + low +
                ", volume=" + volume +
                ", vwap=" + vwap +
                ", maxBid=" + maxBid +
                ", minAsk=" + minAsk +
                ", bestBid=" + bestBid +
                ", bestAsk=" + bestAsk +
                '}';
    }
}
