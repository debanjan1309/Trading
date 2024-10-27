import yfinance as yf
import pandas as pd

# To store trade stats
successful_trades = 0
failed_trades = 0
total_trades = 0

def fetch_data(stock_symbol):
    data = yf.download(stock_symbol, interval='15m', period='1d')
    return data

def mark_first_candle(data):
    if data.empty:
        return None, None, None, None, None  # Skip the stock if no data is available

    first_candle = data.iloc[0]  # Get first 15-minute candle
    high = first_candle['High']
    low = first_candle['Low']
    open_price = first_candle['Open']
    close_price = first_candle['Close']

    # Check if price is less than ₹1000
    if close_price < 1000:
        return None, None, None, None, None  # Skip the stock
    
    percentage_change = (high - low) / open_price * 100

    if percentage_change > 2:
        return None, None, None, None, None  # Skip if the first candle is > 2%

    candle_color = "green" if close_price > open_price else "red"
    
    return high, low, open_price, close_price, candle_color


def check_for_breakout_and_retest(data, high, low, open_price, candle_color):
    global successful_trades, failed_trades, total_trades

    for i in range(1, len(data)):  # Start from 2nd candle (index 1)
        candle = data.iloc[i]
        close = candle['Close']
        
        # Buy Signal Logic (only if first candle is green)
        if close > high and candle_color == "green":
            total_trades += 1
            # Buy at the high of the first 15 min candle
            buy_price = high
            stop_loss = low  # Stop-loss at the low of the first candle
            target_price = buy_price * 1.01  # 1% gain

            # Check if the next candles hit target or stop-loss
            for j in range(i+1, len(data)):
                next_candle = data.iloc[j]
                if next_candle['High'] >= target_price:
                    successful_trades += 1
                    return f"Buy Signal at {buy_price}. Trade successful."
                elif next_candle['Low'] <= stop_loss:
                    failed_trades += 1
                    return f"Buy Signal at {buy_price}. Trade failed (Stop-Loss hit)."
        
        # Sell Signal Logic (only if first candle is red)
        elif close < low and candle_color == "red":
            total_trades += 1
            # Sell at the low of the first 15 min candle
            sell_price = low
            stop_loss = high  # Stop-loss at the high of the first candle
            target_price = sell_price * 0.99  # 1% gain

            # Check if the next candles hit target or stop-loss
            for j in range(i+1, len(data)):
                next_candle = data.iloc[j]
                if next_candle['Low'] <= target_price:
                    successful_trades += 1
                    return f"Sell Signal at {sell_price}. Trade successful."
                elif next_candle['High'] >= stop_loss:
                    failed_trades += 1
                    return f"Sell Signal at {sell_price}. Trade failed (Stop-Loss hit)."
    
    return "No Trade"

def calculate_accuracy():
    if total_trades > 0:
        total = successful_trades + failed_trades
        accuracy = (successful_trades / total) * 100
        return f"Total Trades: {total}, Successful: {successful_trades}, Failed: {failed_trades}, Accuracy: {accuracy:.2f}%"
    else:
        return "No trades executed."

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

# Check each stock
for stock in indian_stocks:
    print(f"Checking stock: {stock}")
    stock_data = fetch_data(stock)
    
    # Unpack values safely
    high, low, open_price, close_price, candle_color = mark_first_candle(stock_data)

    if high is not None and low is not None:
        signal = check_for_breakout_and_retest(stock_data, high, low, open_price, candle_color)
        print(f"{stock} - Signal: {signal}")
    else:
        print(f"{stock} - Skipped due to price or large first candle.")

# Show final strategy performance
print(calculate_accuracy())
