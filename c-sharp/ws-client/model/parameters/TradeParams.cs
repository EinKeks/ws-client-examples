using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ws_client.model.parameters
{
    class TradeParams : Params
    {
        public TradeParams(string symbol) : base(ChannelTypes.TRADE, symbol)
        {
        }
    }
}
