using System;
using WebSocketSharp;
using System.Threading;
using ws_client.model.events;
using ws_client.model.parameters;
using ws_client.model;
using Newtonsoft.Json.Linq;
using System.Collections.Concurrent;


namespace ws_client
{
    class WsClientExample : IDisposable
    {
        private WebSocket ws;

        public WsClientExample(String url)
        {
            this.ws = new WebSocket(url);
        }

        static void Main(string[] args)
        {
            using (var wsclient = new WsClientExample("ws://ws.api.livecoin.net/ws/beta"))
            {
                wsclient.run();
                Console.WriteLine("Press Enter to exit");
                Console.ReadKey(true);
                //Thread.Sleep(500);
            }
        }

        private void run()
        {
            ws.OnOpen += Ws_OnOpen;
            ws.OnMessage += Ws_OnMessage;
            ws.OnError += Ws_OnError;
            ws.OnClose += Ws_OnClose;
            ws.Connect();
        }

        private void Ws_OnError(object sender, ErrorEventArgs e)
        {
            Console.WriteLine("Error: " + e.Message);
        }

        private void Ws_OnMessage(object sender, MessageEventArgs e)
        {
            if (!e.Data.Equals(""))
            {
                ProcessMessage(e.Data);
            }
        }

        private void Ws_OnOpen(object sender, EventArgs e)
        {
            Console.WriteLine("Status: Connected");
            WsClient_Subscribe(new TickerParams("BTC/USD",1.1f));
            WsClient_Subscribe(new OrderBookParams("BTC/USD", 1));
            WsClient_Subscribe(new OrderBookRawParams("BTC/USD", 1));
            WsClient_Subscribe(new TradeParams("BTC/USD"));
            WsClient_Subscribe(new CandleRawParams("BTC/USD", "1m"));
            //here you can make your trade decision
        }

        private void Ws_OnClose(object sender, CloseEventArgs e)
        {
            Console.WriteLine("Status: Disconnected");
            //here you can make your trade decision
        }

        private void WsClient_OnTicker(TickerEvent tickerEvent)
        {
            Console.WriteLine(tickerEvent);
            //here you can make your trade decision
        }

        private void WsClient_OnOrderBook(OrderBookEvent orderBookEvent)
        {
            Console.WriteLine(orderBookEvent);
            //here you can make your trade decision
        }

        private void WsClient_OnOrderBookRaw(OrderBookRawEvent orderBookRawEvent)
        {
            Console.WriteLine(orderBookRawEvent);
            //here you can make your trade decision
        }

        private void WsClient_OnTrade(TradeEvent tradeEvent)
        {
            Console.WriteLine(tradeEvent);
            //here you can make your trade decision
        }

        private void WsClient_OnCandleRaw(CandleEvent candleRawEvent)
        {
            Console.WriteLine(candleRawEvent);
            //here you can make your trade decision
        }

        private void WsClient_OnError(String message, String badRequest)
        {
            Console.WriteLine("Error: \"" + message + "\",text:\"" + badRequest + "\"");
            //here you can make your trade decision
        }

        private void WsClient_OnSubscribe(String channelId)
        {
            Console.WriteLine("Channel subscribed: " + channelId);
            //here you can make your trade decision
        }

        private void WsClient_OnUnsubscribe(String channelId)
        {
            Console.WriteLine("Channel unSubscribed: " + channelId);
            //here you can make your trade decision
        }

        private void WsClient_Subscribe(Params param)
        {
            String query = "";

            if (param is TickerParams)
            {
                query = new JArray(new JValue(""), new JValue("s"), new JValue("t"), new JValue(param.symbol), new JValue(((TickerParams)param).frequency)).ToString();
            }
            else if (param is OrderBookParams)
            {
                query = new JArray(new JValue(""), new JValue("s"), new JValue("o"), new JValue(param.symbol), new JValue(((OrderBookParams)param).depth)).ToString();
            }
            else if (param is OrderBookRawParams)
            {
                query = new JArray(new JValue(""), new JValue("s"), new JValue("r"), new JValue(param.symbol), new JValue(((OrderBookRawParams)param).depth)).ToString();
            }
            else if (param is TradeParams)
            {
                query = new JArray(new JValue(""), new JValue("s"), new JValue("d"), new JValue(param.symbol)).ToString();
            }
            else if (param is CandleRawParams)
            {
                query = new JArray(new JValue(""), new JValue("s"), new JValue("c"), new JValue(param.symbol), new JValue(((CandleRawParams)param).interval)).ToString();
            }
            //JObject query = new JObject(new JProperty("Subscribe", content: JObject.FromObject(param)));
            ws.Send(query);
        }

        private void WsClient_Unsubscribe(String currencyPair, String channelCode)
        {
            JArray query = new JArray(new JValue(""), new JValue("u"), new JValue(channelCode), new JValue(currencyPair));
            ws.Send(query.ToString());
        }

        public void Dispose()
        {
            if (ws != null)
            {
                WsClient_Unsubscribe("BTC/USD", "t");
                WsClient_Unsubscribe("BTC/USD", "r");
                WsClient_Unsubscribe("BTC/USD", "o");
                WsClient_Unsubscribe("BTC/USD", "d");
                WsClient_Unsubscribe("BTC/USD", "c");
                Thread.Sleep(2000);
                ws.Close();
            }
        }

        private void ProcessMessage(String receivedData)
        {
            JArray msg = JArray.Parse(receivedData);
            IJEnumerable<JToken> values = msg.Values();
            JToken operation = msg.First;
            if (operation.ToObject<String>().Equals("s"))
            {
                //JEnumerable<JToken> body = msg.Next.Next;
                WsClient_OnSubscribe(ChannelCodeToType(msg.Last.First.ToObject<String>()) + "_" + msg.Last.First.Next.ToObject<String>());
                ProcessEvents(msg.Last);
                //subscribe notification

            } else if (operation.ToObject<String>().Equals("u"))
            {
                //unsubbscribe notification
                WsClient_OnUnsubscribe(ChannelCodeToType(msg.Last.First.ToObject<String>()) + "_" + msg.Last.First.Next.ToObject<String>());

            } else if (operation.ToObject<String>().Equals("e"))
            {
                //error notification
                Console.WriteLine("Error: " + msg.Last.Last.ToObject<String>());
            } else
            {
                //events notification
                ProcessEvents(msg.Last);
            }
        }

        private string ChannelTypeToCode(string type)
        {
            string result = "";
            if (type.Equals("ticker"))
            {
                result = "t";
            } else if (type.Equals("orderbookraw"))
            {
                result = "r";
            } else if (type.Equals("orderbook"))
            {
                result = "o";
            } else if (type.Equals("trade"))
            {
                result = "d";
            } else if (type.Equals("candle"))
            {
                result = "c";
            }
            return result;
        }

        private string ChannelCodeToType(string code)
        {
            string result = "";
            if (code.Equals("t"))
            {
                result = "ticker";
            } else if (code.Equals("r"))
            {
                result = "orderbookraw";
            } else if (code.Equals("o"))
            {
                result = "orderbook";
            } else if (code.Equals("d"))
            {
                result = "trade";
            } else if (code.Equals("c"))
            {
                result = "candle";
            }
            return result;
        }

        private void ProcessEvents(JToken values)
        {
            JToken channelCode = values.First;
            var channelType = ChannelCodeToType(channelCode.ToObject<String>());
            var currencyPair = channelCode.Next.ToObject<String>();
            var channelId = channelType + "_" + currencyPair;


            foreach (JToken item in values.Children())
            {
                if(item.Type.Equals(JTokenType.Array))
                {
                    if (channelType.Equals(ChannelTypes.TICKER))
                    {
                        TickerEvent e = jsonToTickerEvent(item);
                        e.ChannelId = channelId;
                        WsClient_OnTicker(e);
                    } else if (channelType.Equals(ChannelTypes.ORDERBOOK))
                    {
                        OrderBookEvent e = jsonToOrderBookEvent(item);
                        e.ChannelId = channelId;
                        WsClient_OnOrderBook(e);
                    }  else if (channelType.Equals(ChannelTypes.ORDERBOOKRAW))
                    {
                        OrderBookRawEvent e = jsonToOrderBookRawEvent(item);
                        e.ChannelId = channelId;
                        WsClient_OnOrderBookRaw(e);
                    } else if (channelType.Equals(ChannelTypes.TRADE))
                    {
                        TradeEvent e = jsonToTradeEvent(item);
                        e.ChannelId = channelId;
                        WsClient_OnTrade(e);
                    } else if (channelType.Equals(ChannelTypes.CANDLE))
                    {
                        CandleEvent e = jsonToCandleEvent(item);
                        e.ChannelId = channelId;
                        WsClient_OnCandleRaw(e);
                    }

                }
            }
        }

        private TickerEvent jsonToTickerEvent(JToken json)
        {
            TickerEvent result = new TickerEvent();
            JToken changed = json.First;
            result.Changed = changed.ToObject<long>();
            JToken last = changed.Next;
            result.Last = last.ToObject<decimal?>();
            JToken high = last.Next;
            result.High = high.ToObject<decimal?>();
            JToken low = high.Next;
            result.Low = low.ToObject<decimal?>();
            JToken volume = low.Next;
            result.Volume = volume.ToObject<decimal?>();
            JToken vwap = volume.Next;
            result.Vwap = vwap.ToObject<decimal?>();
            JToken maxBid = vwap.Next;
            result.MaxBid = maxBid.ToObject<decimal?>();
            JToken minAsk = maxBid.Next;
            result.MinAsk = minAsk.ToObject<decimal?>();
            JToken bestBid = minAsk.Next;
            result.BestBid = bestBid.ToObject<decimal?>();
            JToken bestAsk = bestBid.Next;
            result.BestAsk = bestAsk.ToObject<decimal?>();
            return result;
        }
        private OrderBookEvent jsonToOrderBookEvent(JToken json)
        {
            OrderBookEvent result = new OrderBookEvent();
            JToken changed = json.First;
            result.Changed = changed.ToObject<long>();
            JToken price = changed.Next;
            result.Price = price.ToObject<decimal>();
            JToken quantity = price.Next;
            result.Quantity = quantity.ToObject<decimal>();
            return result;
        }
        private OrderBookRawEvent jsonToOrderBookRawEvent(JToken json)
        {
            OrderBookRawEvent result = new OrderBookRawEvent();
            JToken id = json.First;
            result.Id = id.ToObject<long>();
            JToken changed = id.Next;
            result.Changed = changed.ToObject<long>();
            JToken price = changed.Next;
            result.Price = price.ToObject<decimal>();
            JToken quantity = price.Next;
            result.Quantity = quantity.ToObject<decimal>();
            return result;
        }
        private TradeEvent jsonToTradeEvent(JToken json)
        {
            TradeEvent result = new TradeEvent();
            JToken id = json.First;
            result.Id = id.ToObject<long>();
            JToken timestamp = id.Next;
            result.Timestamp = timestamp.ToObject<long>();
            JToken price = timestamp.Next;
            result.Price = price.ToObject<decimal>();
            JToken quantity = price.Next;
            result.Quantity = quantity.ToObject<decimal>();
            return result;
        }
        private CandleEvent jsonToCandleEvent(JToken json)
        {
            CandleEvent result = new CandleEvent();
            JToken t = json.First;
            result.T = t.ToObject<long>();
            JToken o = t.Next;
            result.O = o.ToObject<decimal>();
            JToken c = o.Next;
            result.C = c.ToObject<decimal>();
            JToken h = c.Next;
            result.H = h.ToObject<decimal>();
            JToken l = h.Next;
            result.L = l.ToObject<decimal>();
            JToken v = l.Next;
            result.V = v.ToObject<decimal>();
            JToken q = v.Next;
            result.Q = q.ToObject<decimal>();
            return result;
        }
    }
}
