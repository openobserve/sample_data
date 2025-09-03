"""
Generates sample log files in JSON format and optionally uploads them.

This script creates a specified number of log files, each containing a set of
JSON records with a timestamp and a log message. The files are organized into
a directory structure of 'YYYY/MM/DD'.

It can run in parallel using multiple processes to speed up file generation.
It can also upload the generated files to a ZincObserve-compatible API endpoint.

Usage:
    python generate_basic.py <destination_directory> <num_files> [--upload]

Example:
    # Generate 10 files in the 'data' directory
    python generate_basic.py ./data 10

    # Generate 5 files and upload them
    python generate_basic.py ./data 5 --upload

Environment Variables for Uploading:
    - ZO_BASE_URL: The base URL of the ZincObserve instance (default: http://localhost:5080).
    - ZO_ROOT_USER_EMAIL: The user email for authentication (default: root@example.com).
    - ZO_ROOT_USER_PASSWORD: The user password for authentication (default: Complexpass#123).
"""
import sys
import pandas as pd
import numpy as np
import time
import multiprocessing
import os
import argparse
from pathlib import Path

def upload_file(file_path: str, url: str, user: str, password: str, org="default", stream="default"):
    """
    Uploads a file to the specified ZincObserve-compatible API endpoint using requests.

    Args:
        file_path: The path to the JSON file to upload.
        url: The base URL of the API.
        user: The username for authentication.
        password: The password for authentication.
        org: The organization name.
        stream: The stream name.

    Returns:
        True if upload is successful, False otherwise.
    """
    # This function requires the 'requests' library.
    import requests

    upload_url = f"{url}/api/{org}/{stream}/_json"
    print(f"Uploading {file_path} to {upload_url}...")

    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                upload_url,
                auth=(user, password),
                headers={"Content-Type": "application/json"},
                data=f,
                # Corresponds to curl's -k. In production, consider using a valid certificate.
                verify=False,
                timeout=30
            )
            # Raises HTTPError for bad responses (4xx or 5xx)
            response.raise_for_status()
        print(f"Uploading successful for {file_path}. Response: {response.text.strip()}")
    except requests.exceptions.RequestException as e:
        print(f"Error uploading {file_path}: {e}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}", file=sys.stderr)
        return False

    return True

def timestamp_range_generator(start: float, end: float, num: int):
    """Yields a specified number of evenly spaced timestamps within a range."""
    for ts in np.linspace(start, end, num):
        yield ts

def table_generator(dest_dir: str, start: float, end: float, num_records: int, upload_conf: dict | None = None):
    """
    Generates a single JSON log file with a pandas DataFrame.

    The DataFrame contains 'timestamp' and 'message' columns. The file is
    saved to a directory structure based on the start date (YYYY/MM/DD).
    Optionally, it uploads the file after generation.

    Args:
        dest_dir: The base directory to save the file.
        start: The start timestamp for the log records.
        end: The end timestamp for the log records.
        num_records: The number of records to generate in the file.
        upload_conf: A dictionary with upload configuration, or None to skip upload.

    Returns:
        True on success.
    """
    df = pd.DataFrame(
        [[ts, f"Log message at {ts} time"] for ts in timestamp_range_generator(start, end, num_records)],
        columns=["timestamp", "message"]
    )
    start_time_local = time.localtime(start)

    # Use pathlib for cleaner path manipulation
    file_dir = Path(dest_dir) / time.strftime("%Y/%m/%d", start_time_local)
    file_dir.mkdir(parents=True, exist_ok=True)

    start_time_str = time.strftime("%Y%m%d_%H%M%S", start_time_local)
    file_path = file_dir / f"{start_time_str}.json"

    df.to_json(file_path, orient='records')
    print(f"Generated {file_path}")

    if upload_conf:
        upload_file(str(file_path), **upload_conf)

    return True

def main():
    """
    Main function to parse arguments and generate log files in parallel.
    """
    parser = argparse.ArgumentParser(description="Generate and optionally upload log files.")
    parser.add_argument("dest_dir", help="The destination directory for generated files.")
    parser.add_argument("num_files", type=int, help="The number of log files to generate.")
    parser.add_argument("--records-per-file", type=int, default=1000, help="Number of log records per file.")
    parser.add_argument("--upload", action="store_true", help="Upload files after generation.")
    parser.add_argument("--processes", type=int, default=multiprocessing.cpu_count(), help="Number of parallel processes to use.")
    args = parser.parse_args()

    upload_conf = None
    if args.upload:
        try:
            import requests
        except ImportError:
            print("The 'requests' library is required for uploading. Please install it using 'pip install requests'.", file=sys.stderr)
            sys.exit(1)

        upload_conf = {
            "url": os.getenv("ZO_BASE_URL", "http://localhost:5080"),
            "user": os.getenv("ZO_ROOT_USER_EMAIL", "root@example.com"),
            "password": os.getenv("ZO_ROOT_USER_PASSWORD", "Complexpass#123")
        }

    tasks = []
    now = time.time()
    SECONDS_IN_DAY = 24 * 60 * 60
    for i in range(args.num_files):
        end_time = now - (i * SECONDS_IN_DAY)
        start_time = end_time - SECONDS_IN_DAY
        tasks.append((args.dest_dir, start_time, end_time, args.records_per_file, upload_conf))

    print(f"Generating {args.num_files} files using {args.processes} processes...")
    with multiprocessing.Pool(processes=args.processes) as pool:
        # Use starmap for a simpler, blocking parallel execution
        results = pool.starmap(table_generator, tasks)

    successful_tasks = sum(1 for r in results if r)
    print(f"\nDone! Successfully processed {successful_tasks}/{args.num_files} files.")

if __name__ == "__main__":
    main()
