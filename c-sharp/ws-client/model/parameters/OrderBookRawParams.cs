using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ws_client.model.parameters
{
    class OrderBookRawParams : Params
    {
        public OrderBookRawParams(string symbol, int? depth) : base(ChannelTypes.ORDERBOOKRAW, symbol)
        {
            this.depth = depth;
        }

        public int? depth { get; set; }
    }
}
