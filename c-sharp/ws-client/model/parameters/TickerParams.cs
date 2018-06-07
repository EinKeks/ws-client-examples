using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ws_client.model.parameters
{
    class TickerParams : Params
    {
        public TickerParams(string symbol, float frequency) : base(ChannelTypes.TICKER, symbol)
        {
            this.frequency = frequency;
        }

        public float frequency { set; get; }
    }
}
