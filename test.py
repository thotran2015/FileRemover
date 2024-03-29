import shutil
import unittest
import tempfile
import os
from datetime import datetime, timedelta
from script import create_dialog, MAC_OS, move_files_to_trash
from unittest import mock
import platform


class TestScript(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_trash = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.test_trash):
            shutil.rmtree(self.test_trash)

    def create_test_file(self, filename, days_old):
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, 'w') as file:
            file.write('Test content')
        mod_time = datetime.now() - timedelta(days=days_old)
        os.utime(filepath, (mod_time.timestamp(), mod_time.timestamp()))
        return filepath

    @mock.patch('subprocess.run')
    def test_dialog(self, mock_subprocess_run):
        if platform.system() == MAC_OS:
            title = "Warning: File Deletion in 10s",
            msg = f"About to delete file2.txt",
            create_dialog(title, msg)
            expected_cmd = ['osascript', '-e', f'display dialog "{msg}" buttons {{"Cancel", "OK"}} default button "OK" with title "{title}"']
            mock_subprocess_run.assert_called_once_with(expected_cmd)


    @mock.patch('script.create_notification')
    @mock.patch('shutil.move')
    def test_move_files_to_trash(self, mock_move, mock_create_notification):
        file1 = self.create_test_file("file1.txt", 5)
        file2 = self.create_test_file("file2.txt", 8)
        home_directory = os.path.expanduser('~')
        trash_path = os.path.join(home_directory, ".Trash")
        move_files_to_trash(self.test_dir, 7, trash_path)
        mock_move.assert_called_once_with(file2, os.path.join(trash_path, os.path.basename(file2)))

        if platform.system() == MAC_OS:
            title = "Files Moved to Trash"
            msg = f'1 files are moved from {self.test_dir} to Trash'
            mock_create_notification.assert_called_once_with(title, msg)
        # make sure only file 2 is moved
        self.assertTrue(os.path.exists(file1))


if __name__ == "__main__":
    unittest.main()
