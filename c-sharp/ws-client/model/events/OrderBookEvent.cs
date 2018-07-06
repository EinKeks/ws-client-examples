namespace ws_client.model.events
{
    class OrderBookEvent
    {
        public string ChannelId { get; set; }
        public long Changed { get; set; }
        public decimal Price { get; set; }
        public decimal Quantity { get; set; }

        public override string ToString() => base.ToString() +
                ": {" +
                    "channelId='" + ChannelId + '\'' +
                    ", changed=" + Changed +
                    ", price=" + Price +
                    ", quantity=" + Quantity +
                    '}';
    }
}
