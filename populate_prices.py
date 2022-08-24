import pandas as pd
from datetime import datetime as time
import sqlite3, config
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST, TimeFrame

#timestamp variable
date = time.now()

#alpaca api config
api = tradeapi.REST(config.API_KEY, config.API_SECRET, config.BASE_URL)
assets = api.list_assets()

#sql connection (specify sql return objects not tuples)
connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

#sql command to fetch stock data from stock table
cursor.execute("""
SELECT id, symbol, name FROM stock
""")

rows = cursor.fetchall()

#populate list of symbols
symbols = [row['symbol'] for row in rows]
# creat key/value pair of #'s and symbols
stock_dict = {}
for row in rows:
    symbol = row['symbol']
    symbols.append(symbol)
    stock_dict[symbol] = row['id']

#chunk data to keep from overlaoding api req
chunk_size = 200

for i in range(0, len(symbols), chunk_size):
    symbol_chunk = symbols[i:i+chunk_size]
    
    #data fetch for bar ohlc
    barsets = api.get_bars(symbol_chunk,TimeFrame.Day,"2021-08-31", "2022-08-19")._raw
    
    #loop over all bar data
    for bar in barsets:
        symbol = bar["S"]
        print(f"processing symbol {symbol}")
        stock_id = stock_dict[bar["S"]]
        cursor.execute("""
        INSERT INTO stock_price (stock_id, date, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (stock_id, bar["t"], bar["o"], bar["h"], bar["l"], bar["c"], bar["v"]))

connection.commit()

print(f'Asset Price database was updated at: {date}')