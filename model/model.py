import os
import pandas as pd
from datetime import datetime, timedelta

def load_data(file_path):
    """Load the news CSV file into a DataFrame."""
    return pd.read_csv(file_path)

def convert_time(time_str):
    """Convert time string to datetime object."""
    if time_str.lower() == 'all day':
        return None
    try:
        return datetime.strptime(time_str, '%I:%M%p')
    except ValueError:
        return None

def filter_high_impact_events(df):
    """Filter the DataFrame to find high-impact news events that meet criteria."""
    df = df[df["impact"] == "High"]
    df["time"] = df["time"].apply(convert_time)
    
    filtered_dates = []
    grouped = df.groupby("date")
    
    for date, events in grouped:
        events = events.sort_values(by="time")
        valid_event_found = False
        
        for i, row in events.iterrows():
            if row["time"] is None:
                continue
            
            # Check if there is another event within 15 minutes afterward
            future_events = events[events["time"].notnull() & (events["time"] > row["time"])]
            if any(future_events["time"].apply(lambda x: (x - row["time"]).total_seconds() <= 900)):
                continue
            
            # Check if another high-impact "All Day" event exists
            if any(events["time"].isnull()):
                continue
            
            filtered_dates.append(date)
            valid_event_found = True
            break  # Only need one valid event per date
    
    return filtered_dates

def main():
    file_path = os.path.join(os.path.dirname(__file__), "../data/news.csv")
    df = load_data(file_path)
    high_impact_days = filter_high_impact_events(df)
    
    print("Days with qualifying high-impact news events:")
    for day in high_impact_days:
        print(day)

if __name__ == "__main__":
    main()
