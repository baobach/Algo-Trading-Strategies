import os
import sys
from fyers_apiv3 import fyersModel

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Add the parent directory to the system path
sys.path.append(os.path.join(script_dir, '..'))
import pandas as pd
import numpy as np
import datetime as dt

from apis.fyers import BrokerConnection
from apis.config import Settings

# Instantiate the credential
settings = Settings()
access_token = BrokerConnection(settings.client_id, settings.secret_key, settings.user_name, settings.totp_key, settings.pin1, settings.pin2, settings.pin3, settings.pin4).connect()

# Initialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(
    client_id=settings.client_id, is_async=False, token=access_token, log_path=""
)


def fetchOHLC(ticker, interval, duration):
    """extract historical data and outputs in the form of dataframe"""
    instrument = ticker
    data = {
        "symbol": instrument,
        "resolution": interval,
        "date_format": "1",
        "range_from": dt.date.today() - dt.timedelta(duration),
        "range_to": dt.date.today(),
        "cong_flag": "1",
    }
    sdata = fyers.history(data)
    sdata = pd.DataFrame(sdata["candles"])
    sdata.columns = ["date", "open", "high", "low", "close", "volume"]  # Corrected here
    sdata["date"] = pd.to_datetime(sdata["date"], unit="s")
    sdata["date"] = sdata["date"].dt.tz_localize("UTC").dt.tz_convert("Asia/Kolkata")
    sdata = sdata.set_index("date")
    return sdata


ticker = "NSE:NIFTY50-INDEX"
data = fetchOHLC(ticker, "1", 60)
print(data)


def gethistory(symbol1, type, duration):
    symbol = "NSE:" + symbol1 + "-" + type
    start = dt.date.today() - dt.timedelta(duration)
    end = dt.date.today() - dt.timedelta()
    sdata = pd.DataFrame()
    while start <= end:
        end2 = start + dt.timedelta(60)
        data = {
            "symbol": symbol,
            "resolution": "1",
            "date_format": "1",
            "range_from": start,
            "range_to": end2,
            "cont_flag": "1",
        }
        s = fyers.history(data)
        s = pd.DataFrame(s["candles"])
        sdata = pd.concat([sdata, s], ignore_index=True)
        start = end2 + dt.timedelta(1)
    sdata.columns = ["date", "open", "high", "low", "close", "volume"]
    sdata["date"] = pd.to_datetime(sdata["date"], unit="s")
    sdata.date = sdata.date.dt.tz_localize("UTC").dt.tz_convert("Asia/Kolkata")
    sdata["date"] = sdata["date"].dt.tz_localize(None)
    sdata = sdata.set_index("date")
    return sdata


data = gethistory("NIFTYBANK", "INDEX", 3000)

print(data)
data.to_csv("nifty50.csv")
