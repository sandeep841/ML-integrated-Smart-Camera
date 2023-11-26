import pandas as pd

events_df = pd.DataFrame(columns=["Timestamp", "Event"])

def log_event(event_text):
    global events_df
    timestamp = pd.Timestamp.now()
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Format timestamp as a string

    events_df = pd.concat([
        events_df,
        pd.DataFrame({
            "Timestamp": [timestamp_str],
            "Event": [event_text]
        })
    ], ignore_index=True)
    events_df.to_excel("events_log.xlsx", index=False)
