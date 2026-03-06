# join_data.py
import pandas as pd

# Load
df_lastfm = pd.read_csv("data/artists_lastfm.csv")
df_events = pd.read_csv("data/ticketmaster_events.csv")

# Join artist_name
df = df_events.merge(df_lastfm, left_on="artist_name", right_on="name", how="left")

# Calculate tour size per artist
tour_size = df.groupby("artist_name")["event_id"].count().reset_index()
tour_size.columns = ["artist_name", "total_events"]

df = df.merge(tour_size, on="artist_name", how="left")

# Save
df.to_csv("data/final_dataset.csv", index=False)

print("Finales Dataset gespeichert → data/final_dataset.csv")
print(f"   Rows: {len(df)}")
print(f"   Columns: {list(df.columns)}")
print("\nBeispiel:")
print(df[["artist_name", "listeners", "playcount", "total_events",
          "event_date", "city", "country", "is_capital",
          "is_weekend", "lead_time_days", "status"]].head(10).to_string())
