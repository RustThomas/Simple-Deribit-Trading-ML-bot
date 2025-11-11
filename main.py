import asyncio
import os

import websockets
import json
from darts import timeseries, TimeSeries
import pandas as pd
import time
from darts.models import XGBModel

from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
instrument_name = os.getenv("INSTRUMENT_NAME")

msgauth = \
{"id":9929,"jsonrpc":"2.0","method":"public/auth","params":{"client_id":client_id,"client_secret":client_secret,"grant_type":"client_credentials",
                                                            "scope":"session:name"}}

async def call_api_nologic(msgorder):
   async with websockets.connect('wss://www.deribit.com/ws/api/v2') as websocket:
       ###############
       # Before sending message, make sure that your connection
       # is authenticated (use public/auth call before)
       ###############
       await websocket.send(msgorder)
       while websocket.state == 1:
           response = await websocket.recv()
           # do something with the response...
           print(response)
           return response
           #return asyncio.get_event_loop().create_future()


#Different resolutions may lead to better results
msg = \
{
  "method": "public/get_tradingview_chart_data",
  "params": {
    "instrument_name": instrument_name,
    "start_timestamp": int(round( (time.time()-43200) * 1000)) ,
    "end_timestamp": int(round(time.time() * 1000)),
    "resolution": 1
  },
  "jsonrpc": "2.0",
  "id": 1
}


async def call_api(msg):
   async with websockets.connect('wss://www.deribit.com/ws/api/v2') as websocket:
       await websocket.send(msg)
       while websocket.state == 1:
           response = await websocket.recv()
           series = json.loads(response)
           #print(series)
           time_series = TimeSeries(times = pd.Index(series["result"]["ticks"]), values=series["result"]["close"])

           #Example covariates. Different combinations and User defined variables may lead to better results
           #e.g. support/resistance data, rsi...
           past_covariates = TimeSeries(times = pd.Index(series["result"]["ticks"]), values=series["result"]["high"])
           past_covariates = past_covariates.stack(TimeSeries(times = pd.Index(series["result"]["ticks"]), values=series["result"]["low"]))


           z = 7
           # reaches 70% of mean directional accuracy on specific test data with parameters. Very likely to need
           # different parameters over time. Different model may lead to better result - e.g. tuned DLinear model.
           xgb_covar_model = XGBModel(
               max_depth=5,
               tree_method="exact",
               reg_lambda=1.1,
               reg_alpha=1.1,
               lags=z,
               lags_past_covariates=z,
               output_chunk_length=1,
               output_chunk_shift=0)

           xgb_covar_model.fit(time_series,
                                   past_covariates=past_covariates)


           pred = xgb_covar_model.predict(
               series=time_series[-8:],
               past_covariates=past_covariates[-8:],
               n=1,
           )

           print(pred.first_value())


           _token = await call_api_nologic(json.dumps(msgauth))
           print(_token)
           access_token = json.loads(_token)["result"]["access_token"]
           msgorder = \
               {"id": 8, "jsonrpc": "2.0", "method": "private/get_open_orders_by_instrument",
                "params": {"access_token": access_token, "instrument_name": instrument_name, "type":"all"}}

           _order = await call_api_nologic(json.dumps(msgorder))
           order_status = json.loads(_order)["result"]

           #Example order logic. Likely needs more extensive order management for long term.
           if order_status==[]:
               print("no active order")
               #get available funds
               msgfund ={"id": 2515, "jsonrpc": "2.0", "method": "private/get_account_summary",
                "params": {"access_token": access_token, "currency": "BTC", "extended": False}}
               _funds = await call_api_nologic(json.dumps(msgfund))

               available_fund = json.loads(_funds)["result"]["available_funds"]
               print(available_fund)

               #fixed usdc amount that will be traded. Can fetch whole balance instead.
               #harcoded open/close percentage value likely needs optimization.
               amount = 100
               if pred.first_value()>time_series.last_value():
                   msgbuylimit = \
                       {"id": 5275, "jsonrpc": "2.0", "method": "private/buy",
                        "params": {"access_token": access_token,"amount":amount , "instrument_name": instrument_name, "price":
                            (time_series.last_value()*1.001)-(time_series.last_value()*1.001)%2.5 +2.5,
                                   "valid_until": int(round(time.time() * 1000) +5000),
                                   "linked_order_type" : "one_triggers_one_cancels_other",
                                   "trigger_fill_condition": "complete_fill",
                                   "otoco_config": [
                                       {
                                           "amount": amount,
                                           "direction": "sell",
                                           "type": "stop_market",
                                           "trigger_price" : (time_series.last_value()*0.996)-(time_series.last_value()*0.996)%2.5 -2.5,
                                       #    "price": (time_series.last_value()*0.9996)-(time_series.last_value()*0.9996)%2.5 -2.5,
                                           "trigger": "last_price"
                                       },
                                       {
                                           "amount": amount,
                                           "direction": "sell",
                                           "price": (pred.first_value()*1.005)-(pred.first_value()*1.005)%2.5 +2.5,
                                           "trigger": "mark_price"
                                       }
                                   ],
                                   "type": "limit"}}

                   await call_api_nologic(json.dumps(msgbuylimit))



               elif pred.first_value()<time_series.last_value():
                   msgbuylimit = \
                       {"id": 5274, "jsonrpc": "2.0", "method": "private/sell",
                        "params": {"access_token": access_token,"amount":amount , "instrument_name": instrument_name, "price":
                            (time_series.last_value()*0.999)-(time_series.last_value()*0.999)%2.5 -2.5,
                                   "valid_until": int(round(time.time() * 1000)+5000),
                                   "linked_order_type": "one_triggers_one_cancels_other",
                                   "trigger_fill_condition": "complete_fill",
                                   "otoco_config": [
                                       {
                                           "amount": amount,
                                           "direction": "buy",
                                           "type": "stop_market",
                                           "trigger_price":  (time_series.last_value()*1.004)-(time_series.last_value()*1.004)%2.5 +2.5,
                                           "trigger": "last_price"
                                       },
                                       {
                                           "amount": amount,
                                           "direction": "buy",
                                           "price":   (pred.first_value()*0.995)-(pred.first_value()*0.995)%2.5 -2.5,
                                           "trigger": "mark_price"
                                       }
                                   ],
                                   "type": "limit"}}

                   await call_api_nologic(json.dumps(msgbuylimit))


           return asyncio.get_event_loop().create_future()



while True :
    asyncio.get_event_loop().run_until_complete(call_api(json.dumps(msg)))
    #29 seconds chosen arbitrarily
    time.sleep(29)
