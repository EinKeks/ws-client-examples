package model;

import java.math.BigDecimal;

public class OrderBookEvent {
    private String channelId;
    private Long version;
    private BigDecimal price;
    private BigDecimal quantity;

    public String getChannelId() {
        return channelId;
    }

    public void setChannelId(String channelId) {
        this.channelId = channelId;
    }

    public Long getVersion() {
        return version;
    }

    public void setVersion(Long version) {
        this.version = version;
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
                ", version=" + version +
                ", price=" + price +
                ", quantity=" + quantity +
                '}';
    }
}
