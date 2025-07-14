import json
import random
from datetime import datetime, timedelta, timezone

# Output file name
output_file = "slo_login_latency_data.json"

# Define IST timezone offset (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Convert IST datetime to milliseconds since epoch (UTC-based)
def to_millis_utc(dt_ist):
    dt_utc = dt_ist.astimezone(timezone.utc)
    return int(dt_utc.timestamp() * 1000)

# Current time in IST
now_ist = datetime.now(IST)
start_time_ist = now_ist - timedelta(minutes=5)

data_points = []
services = ["auth-service", "login-service"]
interval = 10  # every 10 seconds
n_points = int((5 * 60) / interval)

for i in range(n_points):
    ts_ist = start_time_ist + timedelta(seconds=i * interval)
    for service in services:
        # Simulate high latency every few points to trigger SLO breach
        value = random.uniform(1.2, 1.8) if i % 8 == 0 else random.uniform(0.3, 0.9)
        point = {
            "__name__": "login_latency_p99",
            "__type__": "gauge",
            "service": service,
            "percentile": "p99",
            "_timestamp": to_millis_utc(ts_ist),
            "value": round(value, 3)
        }
        data_points.append(point)

# Save to file
with open(output_file, "w") as f:
    json.dump(data_points, f, indent=2)
