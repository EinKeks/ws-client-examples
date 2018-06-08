using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ws_client.model.events
{
    class CandleEvent
    {
        public string ChannelId { get; set; }
        public long T { get; set; }
        public decimal O { get; set; }
        public decimal C { get; set; }
        public decimal H { get; set; }
        public decimal L { get; set; }
        public decimal V { get; set; }
        public decimal Q { get; set; }

        public override string ToString() => base.ToString() +
            ": {" +
                "channelId='" + ChannelId + '\'' +
                ", t=" + T +
                ", o=" + O +
                ", c=" + C +
                ", h=" + H +
                ", l=" + L +
                ", v=" + V +
                ", q=" + Q +
                '}';
    }
}
