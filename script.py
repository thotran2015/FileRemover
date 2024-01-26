#!/usr/bin/env python3

import os
import shutil
import time
import subprocess
import platform
from datetime import datetime
import logging
import argparse

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


def trash_files(directories: list[str], days_old: int, trash_path: str):
    cur_time = datetime.now()
    if os.path.exists(LAST_RUN_TIMESTAMP_FILE):
        with open(LAST_RUN_TIMESTAMP_FILE, "r") as f:
            ts_string = f.read()
            last_run_ts = datetime.strptime(ts_string, TIME_FORMAT)
            if (cur_time - last_run_ts).days < SCRIPT_SCHEDULE:
                logging.info(f"Already ran the cleanup script this week for the directories: {directories}. Last run was '{last_run_ts}'")
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


def delete_old_files(directory: str, days_old: int):
    if not os.path.exists(directory):
        print(f"directory does not exist: {directory}")
        return
    files_to_delete = []
    directories_to_delete = []
    cur_time = time.time()
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        file_age_secs = cur_time - os.path.getatime(filepath)
        if file_age_secs / (3600 * 24) > days_old:
            if os.path.isfile(filepath):
                files_to_delete.append(filepath)
            elif os.path.isdir(filepath):
                directories_to_delete.append(filepath)

    # Notify users before delete files
    title = f"Warning: About to delete {len(files_to_delete)} files in {directory}"
    msg = f"Do you want to delete files {files_to_delete}?"
    user_res = create_dialog(title, msg)
    if user_res == 0:
        print(f"Deleting files {files_to_delete}")
        for file in files_to_delete:
            os.remove(file)
            print(f"Deleted file {file}")

    # Notify users before delete directories
    title = f"Warning: About to delete {len(directories_to_delete)} subdirectories in {directory}"
    msg = f"Do you want to delete directories {directories_to_delete}?"
    user_res = create_dialog(title, msg)
    if user_res == 0:
        print(f"Deleting directories {directories_to_delete}")
        for d in directories_to_delete:
            shutil.rmtree(d)
            print(f"Deleted directory {d}")


def main():
    parser = argparse.ArgumentParser(description='A script to clean up directories with command-line arguments')
    parser.add_argument('--trash', '-t', help='Path to the trash folder, i.e., /home/.Trash')
    parser.add_argument('--directories', '-d', nargs='+', help='A list of directories to clean up')
    parser.add_argument('--days', '-a', type=int, help='Minimum age (days old) of files to trash')
    args = parser.parse_args()
    trash_files(args.directories, args.days, args.trash)


if __name__ == "__main__":
    main()
