import sys
import pandas as pd
import numpy as np
import time
import multiprocessing
import os
import subprocess

def upload_file(file_path: str, url: str, user: str, password: str, org="default", stream="default"):
    upload_url = f"{url}/api/{org}/{stream}/_json"
    command = [
        "curl",
        "-u", f"{user}:{password}",
        "-k",
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "--data-binary", f"@{file_path}",
        upload_url
    ]
    print(f"Uploading {file_path} to {upload_url}...")

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
        print(f"Uploading successful for {file_path}. Response: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"Error uploading {file_path}: Reason: {e.returncode}\nMessage: {e.stdout}\nError: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print(f"Timed out while uploading {file_path}")
        return False

    return True

def timestamp_range_generator(start, end, num):
    for ts in np.linspace(start, end, num):
        yield ts

def table_generator(dest_dir, start, end, upload_conf=None):
    df = pd.DataFrame(
        [[ts, "Logmessage at %s time" % ts] for ts in timestamp_range_generator(start, end, 1000)],
        columns=["timestamp", "message"]
    )
    start_time = time.localtime(start)
    year = time.strftime("%Y", start_time)
    month = time.strftime("%m", start_time)
    day = time.strftime("%d", start_time)

    file_dir = os.path.join(dest_dir, year, month, day)
    os.makedirs(file_dir, exist_ok=True)

    start_time_str = time.strftime("%Y%m%d_%H%M%S", start_time)
    file_path = f"{file_dir}/{start_time_str}.json"

    df.to_json(file_path, orient='records')
    print(f"Generated {file_path}")

    if upload_conf:
        upload_file(file_path, **upload_conf)

    return True

if __name__ == "__main__":
    dest_dir = sys.argv[1]
    num_files = int(sys.argv[2])

    now = time.time()

    upload_conf = {
        "url": os.getenv("ZO_BASE_URL", "http://localhost:5080"),
        "user": os.getenv("ZO_ROOT_USER_EMAIL", "root@example.com"),
        "password": os.getenv("ZO_ROOT_USER_PASSWORD", "Complexpass#123")
    }

    should_upload = "--upload" in sys.argv

    num_proc = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_proc)

    tasks = []
    SECONDS_IN_DAY = 24 * 60 * 60
    for i in range(num_files):
        end_time = now - (i * SECONDS_IN_DAY)
        start_time = end_time - SECONDS_IN_DAY
        task_args = (dest_dir, start_time, end_time)
        task_args += (upload_conf,) if should_upload else (None, )
        tasks.append(task_args)

    results = []
    for i, task in enumerate(tasks):
        result = pool.apply_async(table_generator, args=task, callback=lambda m: print(f"Completed {i+1}/{num_files} file processing "))
        results.append(result)

    [res.get() for res in results]
    pool.close()
    pool.join()
    print("Done! Done! Done!")
