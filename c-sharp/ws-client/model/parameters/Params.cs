using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ws_client.model.parameters
{
    abstract class Params
    {
        protected Params(string channelType, string symbol)
        {
            this.channelType = channelType;
            this.symbol = symbol;
        }

        public string channelType { get; set; }
        public string symbol { get; set; }

    }
}
