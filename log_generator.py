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
    df_anomalous = df.copy()
    new_rows = []

    # Feature pools (get unique options from the original dataset)
    ips = df["ip"].unique()
    methods = df["method"].unique()
    paths = df["path"].unique()
    statuses = df["status"].unique()
    sizes = df["size"]
    referrers = df["referrer"].unique()
    user_agents = df["user_agent"].unique()
    times = df["time"]

    size_min, size_max = sizes.min(), sizes.max()

    for _ in range(num_anomalies):
        anomaly_type = random.choice(["error_spike", "ddos", "size_anomaly", "false_positive", "cross_field", "slow_burst"])

        # Create a new base row from scratch (realistic base)
        base = {
            "ip": random.choice(ips),
            "time": random.choice(times),
            "method": random.choice(methods),
            "path": random.choice(paths),
            "status": random.choice(statuses),
            "size": random.randint(size_min, size_max),
            "referrer": random.choice(referrers),
            "user_agent": random.choice(user_agents),
            "anomalous": 1,
            "category": anomaly_type
        }

        if anomaly_type == "error_spike":
            for _ in range(random.randint(5, 10)):
                # error spike happens around same time, has lots of error codes, and small size
                base["time"] = base["time"] + timedelta(seconds=random.randint(0, 60))
                base["status"] = random.choice([301, 302, 403, 404, 500])
                base["size"] = random.randint(0, 200)
                # random choice for the rest of the fields
                base["ip"] = random.choice(ips)
                base["method"] = random.choice(methods)
                base["path"] = random.choice(paths)
                base["referrer"] = random.choice(referrers)
                base["user_agent"] = random.choice(user_agents)
                new_rows.append(base.copy())  # append the modified base to new_rows

        elif anomaly_type == "ddos":
             for _ in range(random.randint(30, 100)):
                # DDOS happens with increased activity around same time
                base["time"] = base["time"] + timedelta(milliseconds=random.randint(0, 2000))
                # random choice for the rest of the fields
                base["status"] = random.choice(statuses)
                base["size"] = random.randint(size_min, size_max)
                base["ip"] = random.choice(ips)
                base["method"] = random.choice(methods)
                base["path"] = random.choice(paths)
                base["referrer"] = random.choice(referrers)
                base["user_agent"] = random.choice(user_agents)
                new_rows.append(base.copy())  # append the modified base to new_rows

        elif anomaly_type == "size_anomaly":
            inflated = int(size_max * random.uniform(2, 5))
            base["size"] = random.randint(size_max, inflated)

        elif anomaly_type == "false_positive":
            # Looks normal, but label is anomalous
            base["anomalous"] = 1
            base["category"] = "false_positive"

        elif anomaly_type == "cross_field":
            base["referrer"], base["user_agent"] = base["user_agent"], base["referrer"]
            base["path"] = "/internal/admin/access"
            base["status"] = random.choice([200, 503])

        elif anomaly_type == "slow_burst":
            # increased activity over a longer period of time
            for _ in range(random.randint(30, 100)):
                base["time"] = base["time"] + timedelta(seconds=random.randint(60, 600))  # delayed response
                # random choice for the rest of the fields
                base["status"] = random.choice(statuses)
                base["size"] = random.randint(size_min, size_max)
                base["ip"] = random.choice(ips)
                base["method"] = random.choice(methods)
                base["path"] = random.choice(paths)
                base["referrer"] = random.choice(referrers)
                base["user_agent"] = random.choice(user_agents)
                new_rows.append(base.copy())
                
        new_rows.append(base)

    # combine and sort all
    all_anomalies = pd.DataFrame(new_rows)
    df_anomalous = pd.concat([df_anomalous, all_anomalies], ignore_index=True)
    df_anomalous = df_anomalous.sort_values(by="time")

    # save to Apache log format
    def row_to_log(row):
        return (
            f'{row["ip"]} - - [{row["time"].strftime("%d/%b/%Y:%H:%M:%S")} +0330] '
            f'"{row["method"]} {row["path"]} HTTP/1.1" {row["status"]} {row["size"]} '
            f'"{row["referrer"]}" "{row["user_agent"]}"'
        )

    with open(output_log_path, "w") as f:
        for line in df_anomalous.apply(row_to_log, axis=1):
            f.write(line + "\n")

    return df_anomalous


df_synthetic = generate_synthetic_logs(10000, input_log_path="archive/short.access.log", output_log_path="archive/synthetic_nonanomalous.access.log")
df_anomalous = inject_anomalies(df_synthetic, num_anomalies=25, output_log_path="archive/synthetic_with_anomalies.access.log")
df_anomalous.to_csv("archive/synthetic_with_anomalies_NEW.csv", index=False)
df_synthetic.to_csv("archive/synthetic_nonanomalous.csv", index=False)

# Based on research, if we are doing supervise learning, we should have about 5-10% anomalies in the dataset.
# If we are doing unsupervised learning (auto-encoders), we should have about 1-2% anomalies in the dataset.