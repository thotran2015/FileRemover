#!/usr/bin/env python3

import os
import shutil
import time
import subprocess
import platform
from datetime import datetime
import logging
import argparse
from typing import Optional

# Configure the logging module to output to the console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

MAC_OS = "Darwin"
SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LAST_RUN_TIMESTAMP_FILE = os.path.join(SCRIPT_DIRECTORY, "last_run_ts.txt")
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SCRIPT_SCHEDULE = 7  # run script every 7 days
FILES_TO_OMIT = {".DS_Store"}


def create_dialog(title, msg):
    current_os = platform.system()
    if current_os == MAC_OS:  # macOS
        # Use AppleScript to create interactive notification for file deletion warning
        res = subprocess.run(['osascript', '-e', f'display dialog "{msg}" buttons {{"Cancel", "OK"}} default button "OK" with title "{title}"'])
        return res.returncode  # 0 means OK and 1 means Cancel
    return 1


def create_notification(title, msg):
    current_os = platform.system()
    if current_os == MAC_OS:
        subprocess.run(['osascript', '-e', f'display notification "{msg}" with title "{title}"'])


def get_last_run_timestamp() -> Optional[datetime]:
    try:
        with open(LAST_RUN_TIMESTAMP_FILE, "r") as f:
            ts_string = f.read()
            last_run_ts = datetime.strptime(ts_string, TIME_FORMAT)
            return last_run_ts
    except Exception as e:
        logging.error(f"Error occurred while reading last run timestamp file: {e}")


def trash_files(directories: list[str], days_old: int, trash_path: str):
    cur_time = datetime.now()
    last_run_ts = get_last_run_timestamp()
    if last_run_ts and (cur_time - last_run_ts).days < SCRIPT_SCHEDULE:
        logging.info(f"Already ran the cleanup script in the last {SCRIPT_SCHEDULE} for the directories: {directories}. Last run was '{last_run_ts}'")
        return
    for directory in directories:
        move_files_to_trash(directory, days_old, trash_path)

    with open(LAST_RUN_TIMESTAMP_FILE, "w") as f:
        f.write(cur_time.strftime(TIME_FORMAT))


def move_files_to_trash(directory: str, days_old: int, trash_path: str) -> bool:
    if not os.path.exists(directory):
        logging.info(f"Input directory does not exist: {directory}")
        return False

    cur_time = time.time()
    num_files_moved = 0
    try:
        for filename in os.listdir(directory):
            if filename in FILES_TO_OMIT:
                continue
            filepath = os.path.join(directory, filename)
            file_age_secs = cur_time - os.path.getatime(filepath)
            if file_age_secs/(3600*24) > days_old:
                dest_path = os.path.join(trash_path, filename)
                shutil.move(filepath, dest_path)
                num_files_moved += 1
        create_notification("Files Moved to Trash", f'{num_files_moved} files are moved from {directory} to Trash')
        logging.info(f'{num_files_moved} files are moved from {directory} to Trash')
        return True
    except Exception as e:
        logging.error(f"Error occurred while moving files to trash: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='A script to clean up directories with command-line arguments')
    parser.add_argument('--trash', '-t', help='Path to the trash folder, i.e., /home/.Trash')
    parser.add_argument('--directories', '-d', nargs='+', help='A list of directories to clean up')
    parser.add_argument('--days', '-a', type=int, help='Minimum age (days old) of files to trash')
    args = parser.parse_args()
    trash_files(args.directories, args.days, args.trash)


if __name__ == "__main__":
    main()
