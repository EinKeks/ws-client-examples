package model.events;

import java.math.BigDecimal;

public class TradeEvent {
    private String channelId;
    private Long id;
    private Long timestamp;
    private BigDecimal price;
    private BigDecimal quantity;

    public String getChannelId() {
        return channelId;
    }

    public void setChannelId(String channelId) {
        this.channelId = channelId;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(Long timestamp) {
        this.timestamp = timestamp;
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
        return "TradeEvent{" +
                "channelId='" + channelId + '\'' +
                ", id=" + id +
                ", timestamp=" + timestamp +
                ", price=" + price +
                ", quantity=" + quantity +
                '}';
    }
}
