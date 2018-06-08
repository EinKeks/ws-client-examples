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
        private ConcurrentDictionary<string, string> subscribedChannels = new ConcurrentDictionary<string, string>();

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
                processMessage(e.Data);
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
            subscribedChannels.TryAdd(channelId, channelId);
            //here you can make your trade decision
        }

        private void WsClient_OnUnsubscribe(String channelId)
        {
            Console.WriteLine("Channel unSubscribed: " + channelId);
            string item;
            subscribedChannels.TryRemove(channelId,out item);
            //here you can make your trade decision
        }

        private void WsClient_Subscribe(Params param)
        {
            JObject query = new JObject(new JProperty("Subscribe", content: JObject.FromObject(param)));
            ws.Send(query.ToString());
        }

        private void WsClient_Unsubscribe(String channelId)
        {
            JObject query = new JObject(new JProperty("Unsubscribe", content: new JObject(new JProperty("channelId", content: channelId))));
            ws.Send(query.ToString());
        }

        public void Dispose()
        {
            if (ws != null)
            {
                foreach(var chid in subscribedChannels.Values)
                {
                    WsClient_Unsubscribe(chid);
                }
                Thread.Sleep(2000);
                ws.Close();
            }
        }

        private void processMessage(String receivedData)
        {
            dynamic msg = JObject.Parse(receivedData);
            if (msg.ContainsKey("Error"))
            {
                String message = msg.Error;
                String badQuery = msg.text;
                WsClient_OnError(message, badQuery);

            }
            else if (msg.ContainsKey("operation"))
            {
                String channelId = msg.channelId;
                String type = channelId.Split('_')[1];
                dynamic operation = msg.operation;
                if (operation.ContainsKey("Subscribe"))
                {
                    WsClient_OnSubscribe(channelId);
                    if (msg.ContainsKey("data"))
                    {
                        foreach (var item in msg.data)
                        {
                            if (type.Equals(ChannelTypes.ORDERBOOK))
                            {
                                OrderBookEvent orderbookEvent = jsonToOrderBookEvent(item);
                                orderbookEvent.ChannelId = channelId;
                                WsClient_OnOrderBook(orderbookEvent);
                            }
                            else if(type.Equals(ChannelTypes.ORDERBOOKRAW))
                            {
                                OrderBookRawEvent orderBookRawEvent = jsonToOrderBookRawEvent(item);
                                orderBookRawEvent.ChannelId = channelId;
                                WsClient_OnOrderBookRaw(orderBookRawEvent);
                            }
                            else if (type.Equals(ChannelTypes.CANDLE))
                            {
                                CandleEvent candleRawEvent = jsonToCandleEvent(item);
                                candleRawEvent.ChannelId = channelId;
                                WsClient_OnCandleRaw(candleRawEvent);
                            }
                        }
                    }
                }
                else if (operation.ContainsKey("Unsubscribe"))
                {
                    WsClient_OnUnsubscribe(channelId);
                } else
                {
                    throw new NotImplementedException();
                }
            }
            else
            {
                String channelId = msg.channelId;
                String type = channelId.Split('_')[1];
                if(type.Equals(ChannelTypes.TICKER))
                {
                    WsClient_OnTicker(jsonToTickerEvent(msg));
                }
                else if(type.Equals(ChannelTypes.ORDERBOOK))
                {
                    WsClient_OnOrderBook(jsonToOrderBookEvent(msg));
                }
                else if(type.Equals(ChannelTypes.ORDERBOOKRAW))
                {
                    WsClient_OnOrderBookRaw(jsonToOrderBookRawEvent(msg));
                }
                else if(type.Equals(ChannelTypes.TRADE))
                {
                    WsClient_OnTrade(jsonToTradeEvent(msg));
                }
                else if(type.Equals(ChannelTypes.CANDLE))
                {
                    WsClient_OnCandleRaw(jsonToCandleEvent(msg));
                }
            }
        }

        private TickerEvent jsonToTickerEvent(dynamic json)
        {
            TickerEvent result = new TickerEvent();
            if (json.ContainsKey("channelId"))
            {
                result.ChannelId = json.channelId;
            }
            if (json.ContainsKey("last"))
            {
                result.Last = json.last;
            }
            if (json.ContainsKey("high"))
            {
                result.High = json.high;
            }
            if (json.ContainsKey("low"))
            {
                result.Low = json.low;
            }
            if (json.ContainsKey("volume"))
            {
                result.Volume = json.volume;
            }
            if (json.ContainsKey("vwap"))
            {
                result.Vwap = json.vwap;
            }
            if (json.ContainsKey("maxBid"))
            {
                result.MaxBid = json.maxBid;
            }
            if (json.ContainsKey("minAsk"))
            {
                result.MinAsk = json.minAsk;
            }
            if (json.ContainsKey("bestBid"))
            {
                result.BestBid = json.bestBid;
            }
            if (json.ContainsKey("bestAsk"))
            {
                result.BestAsk = json.bestAsk;
            }

            return result;
        }
        private OrderBookEvent jsonToOrderBookEvent(dynamic json)
        {
            OrderBookEvent result = new OrderBookEvent();
            if (json.ContainsKey("channelId"))
            {
                result.ChannelId = json.channelId;
            }
            if (json.ContainsKey("price"))
            {
                result.Price = json.price;
            }
            if (json.ContainsKey("quantity"))
            {
                result.Quantity = json.quantity;
            }
            return result;
        }
        private OrderBookRawEvent jsonToOrderBookRawEvent(dynamic json)
        {
            OrderBookRawEvent result = new OrderBookRawEvent();
            if (json.ContainsKey("channelId"))
            {
                result.ChannelId = json.channelId;
            }
            if (json.ContainsKey("id"))
            {
                result.Id = json.id;
            }
            if (json.ContainsKey("price"))
            {
                result.Price = json.price;
            }
            if (json.ContainsKey("quantity"))
            {
                result.Quantity = json.quantity;
            }
            return result;
        }
        private TradeEvent jsonToTradeEvent(dynamic json)
        {
            TradeEvent result = new TradeEvent();
            if (json.ContainsKey("channelId"))
            {
                result.ChannelId = json.channelId;
            }
            if (json.ContainsKey("timestamp"))
            {
                result.Timestamp = json.timestamp;
            }
            if (json.ContainsKey("price"))
            {
                result.Price = json.price;
            }
            if (json.ContainsKey("quantity"))
            {
                result.Quantity = json.quantity;
            }
            return result;
        }
        private CandleEvent jsonToCandleEvent(dynamic json)
        {
            CandleEvent result = new CandleEvent();
            if (json.ContainsKey("channelId"))
            {
                result.ChannelId = json.channelId;
            }
            if (json.ContainsKey("t"))
            {
                result.T = json.t;
            }
            if (json.ContainsKey("o"))
            {
                result.O = json.o;
            }
            if (json.ContainsKey("c"))
            {
                result.C = json.c;
            }
            if (json.ContainsKey("h"))
            {
                result.H = json.h;
            }
            if (json.ContainsKey("l"))
            {
                result.L = json.l;
            }
            if (json.ContainsKey("v"))
            {
                result.V = json.v;
            }
            if (json.ContainsKey("q"))
            {
                result.Q = json.q;
            }
            return result;
        }
    }
}
