namespace ws_client.model.events
{
    class OrderBookEvent
    {
        public string ChannelId { get; set; }
        public decimal Price { get; set; }
        public decimal Quantity { get; set; }

        public override string ToString() => base.ToString() +
                ": {" +
                    "channelId='" + this.ChannelId + '\'' +
                    ", price=" + this.Price +
                    ", quantity=" + this.Quantity +
                    '}';
    }
}
