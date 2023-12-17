import os
import time
import subprocess


def notify(title, msg):
    subprocess.run(['osascript', '-e', f'display dialog "{msg}" buttons {{"Cancel", "OK"}} default button "OK" with title "{title}"'])


def delete_old_files(directory: str, days_old: int):
    files_to_delete = []
    cur_time = time.time()
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            file_age_secs = cur_time - os.path.getatime(filepath)
            if file_age_secs/(3600*24) > days_old:
                files_to_delete.append(filepath)

    # Notify users before delete files
    title = f"Warning: About to delete {len(files_to_delete)} files in {directory}"
    msg = f"Do you want to delete files {files_to_delete}?"
    notify(title, msg)

    for file in files_to_delete:
        os.remove(file)
        print(f"Deleted {file}")


def main():
    download_directory = "/Users/thotran/Downloads"
    days_threshold = 14
    delete_old_files(download_directory, days_threshold)


if __name__ == "__main__":
    main()
