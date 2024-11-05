from flask import Flask, jsonify, render_template, send_from_directory
import yfinance as yf
import pandas as pd
from threading import Lock
import time

app = Flask(__name__)
signals_lock = Lock()
buy_signals = []
sell_signals = []
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Fetch data from yfinance
def fetch_data(stock_symbol):
    data = yf.download(stock_symbol, interval='15m', period='1d')
    return data

# Mark first candle and check if it meets criteria
def mark_first_candle(data):
    first_candle = data.iloc[0]
    high = first_candle['High']
    low = first_candle['Low']
    open_price = first_candle['Open']
    close_price = first_candle['Close']
    percentage_change = (high - low) / open_price * 100
    price_check = close_price >= 1000
    candle_color = "green" if close_price > open_price else "red"

    if percentage_change > 1 or not price_check:
        return None, None, None
    return high, low, candle_color

# Check for breakout and retest conditions
def check_for_breakout_and_retest(data, high, low, candle_color):
    for i in range(1, len(data)):
        candle = data.iloc[i]
        close = candle['Close']
        
        # Buy Signal Logic (only if first candle is green)
        if close > high and candle_color == "green":
            if i + 1 < len(data):
                retest_candle = data.iloc[i + 1]
                if retest_candle['Low'] <= high:
                    return "Buy", high
        
        # Sell Signal Logic (only if first candle is red)
        elif close < low and candle_color == "red":
            if i + 1 < len(data):
                retest_candle = data.iloc[i + 1]
                if retest_candle['High'] >= low:
                    return "Sell", low
    return None, None

# List of Indian stocks
indian_stocks = ["RELIANCE.NS", "TATAMOTORS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "ABB.NS", "ACC.NS", "AUBANK.NS", "AARTIIND.NS", "ABBOTINDIA.NS", 
                 "ADANIENT.NS", "ADANIPORTS.NS", "ABCAPITAL.NS", "ABFRL.NS", "ALKEM.NS", "AMBUJACEM.NS", "APOLLOHOSP.NS", "APOLLOTYRE.NS", "ASHOKLEY.NS", 
                 "ASIANPAINT.NS", "ASTRAL.NS", "ATUL.NS", "AUROPHARMA.NS", "AXISBANK.NS", "BSOFT.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", 
                 "BALKRISIND.NS", "BALRAMCHIN.NS", "BANDHANBNK.NS", "BANKBARODA.NS", "BATAINDIA.NS", "BERGEPAINT.NS", "BEL.NS", "BHARATFORG.NS", "BHEL.NS", 
                 "BPCL.NS", "BHARTIARTL.NS", "BIOCON.NS", "BOSCHLTD.NS", "BRITANNIA.NS", "CANFINHOME.NS", "CANBK.NS", "CHAMBLFERT.NS", "CHOLAFIN.NS", "CIPLA.NS", 
                 "CUB.NS", "COALINDIA.NS", "COFORGE.NS", "COLPAL.NS", "CONCOR.NS", "COROMANDEL.NS", "CROMPTON.NS", "CUMMINSIND.NS", "DLF.NS", "DABUR.NS", "DALBHARAT.NS",
                 "DEEPAKNTR.NS", "DIVISLAB.NS", "DIXON.NS", "LALPATHLAB.NS", "DRREDDY.NS", "EICHERMOT.NS", "ESCORTS.NS", "EXIDEIND.NS", "GAIL.NS", "GMRINFRA.NS", "GLENMARK.NS", 
                 "GODREJCP.NS", "GODREJPROP.NS", "GRANULES.NS", "GRASIM.NS", "GUJGASLTD.NS", "GNFC.NS", "HCLTECH.NS", "HDFCAMC.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HAVELLS.NS", 
                 "HEROMOTOCO.NS", "HINDALCO.NS", "HAL.NS", "HINDCOPPER.NS", "HINDPETRO.NS", "HINDUNILVR.NS", "ICICIGI.NS", "ICICIPRULI.NS", "IDFCFIRSTB.NS", "IPCALAB.NS", 
                 "ITC.NS", "INDIAMART.NS", "IEX.NS", "IOC.NS", "IRCTC.NS", "IGL.NS", "INDUSTOWER.NS", "INDUSINDBK.NS", "NAUKRI.NS", "INFY.NS", "INDIGO.NS", "JKCEMENT.NS", 
                 "JSWSTEEL.NS", "JINDALSTEL.NS", "JUBLFOOD.NS", "KOTAKBANK.NS", "LTF.NS", "LTTS.NS", "LICHSGFIN.NS", "LTIM.NS", "LT.NS", "LAURUSLABS.NS", "LUPIN.NS", "MRF.NS", 
                 "MGL.NS", "M&MFIN.NS", "M&M.NS", "MANAPPURAM.NS", "MARICO.NS", "MARUTI.NS", "MFSL.NS", "METROPOLIS.NS", "MPHASIS.NS", "MCX.NS", "MUTHOOTFIN.NS", "NMDC.NS", 
                 "NTPC.NS", "NATIONALUM.NS", "NAVINFLUOR.NS", "NESTLEIND.NS", "OBEROIRLTY.NS", "ONGC.NS", "OFSS.NS", "PIIND.NS", "PVRINOX.NS", "PAGEIND.NS", "PERSISTENT.NS", 
                 "PETRONET.NS", "PIDILITIND.NS", "PEL.NS", "POLYCAB.NS", "PFC.NS", "POWERGRID.NS", "PNB.NS", "RBLBANK.NS", "RECLTD.NS", "SBICARD.NS", "SBILIFE.NS", "SHREECEM.NS", 
                 "SRF.NS", "MOTHERSON.NS", "SHRIRAMFIN.NS", "SIEMENS.NS", "SBIN.NS", "SAIL.NS", "SUNPHARMA.NS", "SUNTV.NS", "SYNGENE.NS", "TATACONSUM.NS", "TVSMOTOR.NS", 
                 "TATACHEM.NS", "TATACOMM.NS", "TCS.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TECHM.NS", "FEDERALBNK.NS", "INDHOTEL.NS", "RAMCOCEM.NS", "TITAN.NS", 
                 "TORNTPHARM.NS", "TRENT.NS", "UPL.NS", "ULTRACEMCO.NS", "UBL.NS", "UNITDSPR.NS", "VEDL.NS", "IDEA.NS", "VOLTAS.NS", "WIPRO.NS", "ZYDUSLIFE.NS"]

# Fetch and update signals
def update_signals():
    global buy_signals, sell_signals
    with signals_lock:
        buy_signals.clear()
        sell_signals.clear()
        for stock in indian_stocks:
            stock_data = fetch_data(stock)
            high, low, candle_color = mark_first_candle(stock_data)
            if high is not None and low is not None:
                signal, price = check_for_breakout_and_retest(stock_data, high, low, candle_color)
                if signal == "Buy":
                    buy_signals.append({"stock": stock, "price": price})
                elif signal == "Sell":
                    sell_signals.append({"stock": stock, "price": price})

# Homepage route
@app.route("/")
def index():
    return render_template("index.html")

# API route to get signals
@app.route("/signals")
def signals():
    with signals_lock:
        return jsonify({"buy_signals": buy_signals, "sell_signals": sell_signals})

# Background task to update signals every 5 minutes
def start_update_task():
    while True:
        update_signals()
        time.sleep(300)

# Run background task in a separate thread
import threading
threading.Thread(target=start_update_task, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)
