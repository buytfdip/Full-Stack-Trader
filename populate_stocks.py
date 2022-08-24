from datetime import datetime as time
import sqlite3, config
import alpaca_trade_api as tradeapi

date = time.now()

api = tradeapi.REST(config.API_KEY, config.API_SECRET, config.BASE_URL)

assets = api.list_assets()

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row


cursor = connection.cursor()

cursor.execute("""
SELECT symbol, name FROM stock
""")
rows = cursor.fetchall()


symbols = [row['symbol'] for row in rows]


for asset in assets:
    try:
        if asset.status == 'active' and asset.exchange != 'FTXU' and asset.tradable and asset.symbol not in symbols:
            cursor.execute("INSERT INTO stock (symbol, name, exchange) VALUES(?,?,?)", (asset.symbol, asset.name, asset.exchange))
            print(f"Added a new stock: {asset.symbol} {asset.name}.")
    except Exception as e:
        print(f'An error occured while adding: {asset.symbol}')

connection.commit()

print(f'Asset Name database was updated at: {date}')