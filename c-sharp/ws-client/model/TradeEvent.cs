namespace ws_client.model
{
    class TradeEvent
    {
        public string ChannelId { get; set; }
        public long Id { get; set; }
        public long Timestamp { get; set; }
        public decimal Price { get; set; }
        public decimal Quantity { get; set; }

        public override string ToString() => base.ToString() +
            ": {" +
                "channelId='" + ChannelId + '\'' +
                ", id=" + Id +
                ", timestamp=" + Timestamp +
                ", price=" + Price +
                ", quantity=" + Quantity +
                '}';
    }
}
