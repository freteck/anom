import pandas as pd
import random
import re
from datetime import datetime, timedelta

def generate_synthetic_logs(num_synthetic_entries: int, input_log_path="archive/short.access.log", output_log_path="archive/synthetic.access.log"):
    # Load log file
    with open(input_log_path, "r") as f:
        log_lines = f.readlines()

    # Regex pattern to parse all fields
    log_pattern = re.compile(
        r'(?P<ip>\S+) \S+ \S+ '
        r'\[(?P<time>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<path>[^"]+?) \S+" '
        r'(?P<status>\d{3}) '
        r'(?P<size>\d+|-) '
        r'"(?P<referrer>[^"]*)" '
        r'"(?P<user_agent>[^"]*)"'
    )

    # Parse logs
    parsed_logs = []
    for line in log_lines:
        match = log_pattern.match(line)
        if match:
            data = match.groupdict()
            data['time'] = datetime.strptime(data['time'].split()[0], "%d/%b/%Y:%H:%M:%S")
            data['status'] = int(data['status'])
            data['size'] = int(data['size'])
            parsed_logs.append(data)

    # Convert to DataFrame
    df_logs = pd.DataFrame(parsed_logs)

    # Extract field distributions
    unique_ips = df_logs['ip'].unique()
    unique_paths = df_logs['path'].unique()
    status_codes = df_logs['status'].unique()
    referrers = df_logs['referrer'].unique()
    user_agents = df_logs['user_agent'].unique()
    method_probs = df_logs['method'].value_counts(normalize=True)
    size_min, size_max = df_logs['size'].min(), df_logs['size'].max()
    last_timestamp = df_logs['time'].max()

    # Generate synthetic logs
    synthetic_logs = []
    synthetic_rows = []
    current_time = last_timestamp + timedelta(milliseconds=0)

    for i in range(num_synthetic_entries):
        delta = timedelta(milliseconds=random.randint(100, 500))
        current_time += delta

        ip = random.choice(unique_ips)
        method = random.choices(method_probs.index, weights=method_probs.values)[0]
        path = random.choice(unique_paths)
        status = random.choice(status_codes)
        size = random.randint(size_min, size_max)
        referrer = random.choice(referrers)
        user_agent = random.choice(user_agents)

        log_entry = (
            f'{ip} - - [{current_time.strftime("%d/%b/%Y:%H:%M:%S")} +0330] '
            f'"{method} {path} HTTP/1.1" {status} {size} "{referrer}" "{user_agent}"'
        )
        synthetic_logs.append(log_entry)

        # Store structured data for DataFrame
        synthetic_rows.append({
            "ip": ip,
            "time": current_time,
            "method": method,
            "path": path,
            "status": status,
            "size": size,
            "referrer": referrer,
            "user_agent": user_agent,
            "anomalous": 0,
            "category": "not anomalous"
        })

    # Save synthetic logs to file
    with open(output_log_path, "w") as f:
        for line in synthetic_logs:
            f.write(line + "\n")

    return pd.DataFrame(synthetic_rows)


def inject_anomalies(df, num_anomalies=1000, output_log_path="archive/synthetic_with_anomalies.access.log"):
    # Three major types of anomalies:
    # 1. (Error Codes) Spike in error codes in a short time window 
    # 2. (DDOS) Unusual request rate from one IP  
    # 3. (Size Anomaly) sudden content-length explosion 
    
    # use switch cases to execute each time of anomaly
    df_anomalous = df.copy()
    new_rows = []

    for _ in range(num_anomalies):
        anomaly_type = random.choice(["error_spike", "ddos", "size_anomaly"])
        base_row = df.sample(1).iloc[0].copy()

        if anomaly_type == "error_spike":
            error_codes = [500, 502, 503, 504]
            burst_count = random.randint(10, 30)
            for i in range(burst_count):
                row = base_row.copy()
                row["time"] += timedelta(milliseconds=i * random.randint(10, 50))
                row["status"] = random.choice(error_codes)
                row["size"] = random.randint(0, 200)
                row["category"] = "error_spike"
                row["anomalous"] = 1
                new_rows.append(row)

        elif anomaly_type == "ddos":
            target_ip = base_row["ip"]
            target_path = base_row["path"]
            target_method = base_row["method"]
            flood_time = base_row["time"]

            request_count = random.randint(100, 200)
            for _ in range(request_count):
                row = base_row.copy()
                row["ip"] = target_ip
                row["path"] = target_path
                row["method"] = target_method
                row["time"] = flood_time  # same timestamp for all requests
                row["referrer"] = random.choice(df["referrer"].unique())
                row["user_agent"] = random.choice(df["user_agent"].unique())
                row["category"] = "ddos"
                row["anomalous"] = 1
                new_rows.append(row)

        elif anomaly_type == "size_anomaly":
            row = base_row.copy()
            row["size"] = base_row["size"] * random.randint(10, 50)
            row["category"] = "size_anomaly"
            row["anomalous"] = 1
            new_rows.append(row)

    # combine and sort
    df_anomalous = pd.concat([df_anomalous, pd.DataFrame(new_rows)], ignore_index=True)
    df_anomalous = df_anomalous.sort_values(by="time")

    # Output to Apache-style log file
    def row_to_log(row):
        return (
            f'{row["ip"]} - - [{row["time"].strftime("%d/%b/%Y:%H:%M:%S")} +0330] '
            f'"{row["method"]} {row["path"]} HTTP/1.1" {row["status"]} {row["size"]} '
            f'"{row["referrer"]}" "{row["user_agent"]}"'
        )

    log_lines = df_anomalous.apply(row_to_log, axis=1)

    with open(output_log_path, "w") as f:
        for line in log_lines:
            f.write(line + "\n")

    return df_anomalous
 
df_synthetic = generate_synthetic_logs(10000, input_log_path="archive/short.access.log", output_log_path="archive/synthetic_nonanomalous.access.log")
df_anomalous = inject_anomalies(df_synthetic, num_anomalies=16, output_log_path="archive/synthetic_with_anomalies.access.log")
df_anomalous.to_csv("archive/synthetic_with_anomalies.csv", index=False)
df_synthetic.to_csv("archive/synthetic_nonanomalous.csv", index=False)

# Based on research, if we are doing supervise learning, we should have about 5-10% anomalies in the dataset.
# If we are doing unsupervised learning (auto-encoders), we should have about 1-2% anomalies in the dataset.