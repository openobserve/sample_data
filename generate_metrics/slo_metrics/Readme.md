# SLO Metrics Data Generator

This folder contains sample data generation scripts for synthetic SLO (Service Level Objective) metrics.  
These scripts can be used to produce realistic metric datasets for testing dashboards, alerting rules, or observability pipelines using tools like OpenObserve.

## 📄 Available Scripts

### 1. `disk_utilization_datageneration.py` → `slo_metrics_data.json`

Generates mock **disk utilization** metrics for multiple hosts and mount points, sampled every 10 seconds over the past 5 minutes.

- **Metric Name:** `disk_utilization`
- **Metric Type:** `gauge`
- **Hosts:** `db1`, `db2`  
- **Mounts:** `/`, `/data`  
- **Timestamps:** Generated in IST (UTC+5:30) and stored as UTC epoch milliseconds
- **Spike Simulation:** Every 7th point simulates a high-utilization value (85–95%), others range between 40–60%

#### Run:
```bash
python generate_slo_metrics_data.py
````

### 2. `generate_login_latency_p99_data.py` → `slo_login_latency_data.json`

Generates synthetic **P99 login latency** metrics for two services over a 5-minute window, sampled every 10 seconds.

* **Metric Name:** `login_latency_p99`
* **Metric Type:** `gauge`
* **Services:** `auth-service`, `login-service`
* **Percentile:** `p99`
* **Timestamps:** Generated in IST (UTC+5:30) and stored as UTC epoch milliseconds
* **Spike Simulation:** Every 8th point exceeds the 1-second SLO threshold (1.2–1.8s), others range from 0.3–0.9s

#### Run:

```bash
python generate_login_latency_p99_data.py
```

## 📤 Ingesting to OpenObserve

After running a script, use the following `curl` command to ingest the data into OpenObserve:

```bash
curl -X POST "http://<your-openobserve-host>:5080/api/default/ingest/metrics/_json" \
  -H "Authorization: Basic <base64-creds>" \
  -H "Content-Type: application/json" \
  --data-binary @<output_file.json>
```

Replace:

* `<your-openobserve-host>` with your OpenObserve instance URL
* `<base64-creds>` with your Base64-encoded credentials (`username:password`)
* `<output_file.json>` with either `slo_metrics_data.json` or `slo_login_latency_data.json`

## ✅ Use Cases

These scripts help teams:

* Simulate realistic load and performance behavior
* Validate SLO-based alerting rules (e.g., sustained 5-minute violations)
* Build dashboards with real-looking time series data

---

Feel free to fork, extend, or add new metric generators (e.g., for API error rates, memory usage, etc.).

