package model.events;

import java.math.BigDecimal;

public class OrderBookEvent {
    private String channelId;
    private Long changed;
    private BigDecimal price;
    private BigDecimal quantity;

    public String getChannelId() {
        return channelId;
    }

    public void setChannelId(String channelId) {
        this.channelId = channelId;
    }

    public Long getChanged() {
        return changed;
    }

    public void setChanged(Long changed) {
        this.changed = changed;
    }

    public BigDecimal getPrice() {
        return price;
    }

    public void setPrice(BigDecimal price) {
        this.price = price;
    }

    public BigDecimal getQuantity() {
        return quantity;
    }

    public void setQuantity(BigDecimal quantity) {
        this.quantity = quantity;
    }

    @Override
    public String toString() {
        return "OrderBook{" +
                "channelId='" + channelId + '\'' +
                ", changed=" + changed +
                ", price=" + price +
                ", quantity=" + quantity +
                '}';
    }
}
