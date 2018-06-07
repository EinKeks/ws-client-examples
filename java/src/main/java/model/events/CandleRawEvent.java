package model.events;

import java.math.BigDecimal;

public class CandleRawEvent {
    private String channelId;
    private Long timestamp;
    private BigDecimal open;
    private BigDecimal close;
    private BigDecimal high;
    private BigDecimal low;
    private BigDecimal volume;
    private BigDecimal quantity;

    public String getChannelId() {
        return channelId;
    }

    public void setChannelId(String channelId) {
        this.channelId = channelId;
    }

    public Long getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(Long timestamp) {
        this.timestamp = timestamp;
    }

    public BigDecimal getOpen() {
        return open;
    }

    public void setOpen(BigDecimal open) {
        this.open = open;
    }

    public BigDecimal getClose() {
        return close;
    }

    public void setClose(BigDecimal close) {
        this.close = close;
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

    public BigDecimal getQuantity() {
        return quantity;
    }

    public void setQuantity(BigDecimal quantity) {
        this.quantity = quantity;
    }

    @Override
    public String toString() {
        return "CandleEvent{" +
                "channelId='" + channelId + '\'' +
                ", timestamp=" + timestamp +
                ", open=" + open +
                ", close=" + close +
                ", high=" + high +
                ", low=" + low +
                ", volume=" + volume +
                ", quantity=" + quantity +
                '}';
    }
}
