import os
import shutil
import time
import subprocess
import platform

MAC_OS = "Darwin"


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


def move_files_to_trash(directory: str, days_old: int, trash_path: str):
    if not os.path.exists(directory):
        print(f"directory does not exist: {directory}")
        return
    cur_time = time.time()
    num_files_moved = 0
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        file_age_secs = cur_time - os.path.getatime(filepath)
        if file_age_secs/(3600*24) > days_old:
            shutil.move(filepath, trash_path)
            num_files_moved += 1
    create_notification("Files Moved to Trash", f'{num_files_moved} files are moved from {directory} to trash')


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
    home_directory = os.path.expanduser('~')
    trash_path = os.path.join(home_directory, ".Trash")
    download_directory = os.path.join(home_directory, "Downloads")
    desktop_directory = os.path.join(home_directory, "Desktop")
    days_threshold = 7
    # delete_old_files(download_directory, days_threshold)
    move_files_to_trash(download_directory, days_threshold, trash_path)
    move_files_to_trash(desktop_directory, days_threshold, trash_path)


if __name__ == "__main__":
    main()
