using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ws_client.model.parameters
{
    class OrderBookParams : Params
    {
        public OrderBookParams(string symbol, int? depth) : base(ChannelTypes.ORDERBOOK, symbol)
        {
            this.depth = depth;
        }

        public int? depth { get; set; }
    }
}
