#!/usr/bin/env python3
import yfinance as yf
import math
import datetime

def get_vix_volatility():
    """
    Fetches the latest VIX data from yfinance and computes:
      - current VIX (annualized)
      - predicted daily volatility for the next trading day (VIX/sqrt(252))
    
    Returns:
        current_date (datetime.date): The date for which the VIX was fetched.
        current_vix (float): The current VIX value (annualized).
        next_date (datetime.date): The next trading day.
        predicted_daily_vol (float): The predicted daily volatility.
    """
    ticker = "^VIX"
    # Fetch the most recent day of data.
    data = yf.Ticker(ticker).history(period="1d")
    if data.empty:
        raise Exception("No data fetched for VIX. Check your connection or ticker symbol.")
    
    # Use the most recent closing price
    current_vix = data['Close'].iloc[-1]
    current_date = datetime.datetime.now().date()

    # Determine the next trading day:
    # (For simplicity, we assume the next day is the trading day unless it's weekend)
    next_date = current_date + datetime.timedelta(days=1)
    if next_date.weekday() >= 5:  # Saturday (5) or Sunday (6)
        days_to_add = 7 - next_date.weekday()
        next_date = current_date + datetime.timedelta(days=days_to_add)

    # Predicted daily volatility using VIX divided by sqrt(252)
    predicted_daily_vol = current_vix / math.sqrt(252)
    
    return current_date, current_vix, next_date, predicted_daily_vol

def print_volatility():
    """
    Retrieves the VIX data and prints the current annualized volatility and 
    the predicted daily volatility for the next trading day.
    """
    try:
        current_date, current_vix, next_date, predicted_vol = get_vix_volatility()
        print(f"Current VIX (annualized) on {current_date}: {current_vix:.2f}")
        print(f"Predicted daily volatility for {next_date}: {predicted_vol:.2f}")
    except Exception as e:
        print(f"Error fetching VIX data: {e}")

