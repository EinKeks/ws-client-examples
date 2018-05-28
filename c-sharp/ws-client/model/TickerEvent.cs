namespace ws_client.model
{
    class TickerEvent
    {
        public string ChannelId { get; set; }
        public decimal? Last { get; set; }
        public decimal? High { get; set; }
        public decimal? Low { get; set; }
        public decimal? Volume { get; set; }
        public decimal? Vwap { get; set; }
        public decimal? MaxBid { get; set; }
        public decimal? MinAsk { get; set; }
        public decimal? BestBid { get; set; }
        public decimal? BestAsk { get; set; }

        public override string ToString() => base.ToString() +
            ": {" +
                "channelId='" + ChannelId + '\'' +
                ", last=" + Last +
                ", high=" + High +
                ", low=" + Low +
                ", volume=" + Volume +
                ", vwap=" + Vwap +
                ", maxBid=" + MaxBid +
                ", minAsk=" + MinAsk +
                ", bestBid=" + BestBid +
                ", bestAsk=" + BestAsk +
                '}';
    }
}
