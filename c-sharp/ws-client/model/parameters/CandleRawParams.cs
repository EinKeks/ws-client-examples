using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ws_client.model.parameters
{
    class CandleRawParams : Params
    {
        public CandleRawParams(string symbol, string interval) : base(ChannelTypes.CANDLE, symbol)
        {
            this.interval = interval;
        }

        public string interval { get; set; }
    }
}
