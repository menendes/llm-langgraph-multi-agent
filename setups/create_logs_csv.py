import pandas as pd
import random
from datetime import datetime, timedelta

num_rows = 100_000
start_time = datetime(2025, 4, 1)

def random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))


usernames = ["admin", "guest", "root"] + [f"user{i}" for i in range(1, 51)]

# === Generate Log Entries ===
records = []
for _ in range(num_rows):
    timestamp = (start_time + timedelta(seconds=random.randint(0, 2592000))).strftime("%Y-%m-%d %H:%M:%S")
    ip = random_ip()
    username = random.choice(usernames)
    status = random.choices(["success", "failed"], weights=[0.7, 0.3])[0]

    # Append flat string values
    records.append((timestamp, ip, username, status))

# === Convert to DataFrame and Save ===
df = pd.DataFrame(records, columns=["timestamp", "ip_address", "username", "status"])
df.to_csv("../data/logs_large.csv", index=False)

print("Successfully generated data/logs_large.csv with", len(df), "rows")