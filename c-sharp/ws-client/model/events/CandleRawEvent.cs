using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ws_client.model.events
{
    class CandleRawEvent
    {
        public string ChannelId { get; set; }
        public long Timestamp { get; set; }
        public decimal Open { get; set; }
        public decimal Close { get; set; }
        public decimal High { get; set; }
        public decimal Low { get; set; }
        public decimal Volume { get; set; }
        public decimal Quantity { get; set; }

        public override string ToString() => base.ToString() +
            ": {" +
                "channelId='" + ChannelId + '\'' +
                ", timestamp=" + Timestamp +
                ", open=" + Open +
                ", close=" + Close +
                ", high=" + High +
                ", low=" + Low +
                ", volume=" + Volume +
                ", quantity=" + Quantity +
                '}';
    }
}
