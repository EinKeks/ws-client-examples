namespace ws_client.model.events
{
    class OrderBookRawEvent
    {
        public string ChannelId { get; set; }
        public long Id { get; set; }
        public decimal? Price { get; set; }
        public decimal Quantity { get; set; }

        public override string ToString() => base.ToString() +
            ": {" +
                "channelId='" + ChannelId + '\'' +
                ", id=" + Id +
                ", price=" + Price +
                ", quantity=" + Quantity +
                '}';
    }
}
