import shutil
import unittest
import tempfile
import os
from datetime import datetime, timedelta
from script import delete_old_files, notify, MAC_OS
from unittest.mock import patch
import platform


class TestFileRemoverMethods(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def create_test_file(self, filename, days_old):
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, 'w') as file:
            file.write('Test content')
        mod_time = datetime.now() - timedelta(days=days_old)
        os.utime(filepath, (mod_time.timestamp(), mod_time.timestamp()))
        return filepath

    @patch('subprocess.run')
    def test_notify(self, mock_subprocess_run):
        if platform.system() == MAC_OS:
            title = "Warning: File Deletion in 10s",
            msg = f"About to delete file2.txt",
            notify(title, msg)
            expected_cmd = ['osascript', '-e', f'display dialog "{msg}" buttons {{"Cancel", "OK"}} default button "OK" with title "{title}"']
            mock_subprocess_run.assert_called_once_with(expected_cmd)

    @patch('script.notify')
    def test_delete_old_files(self, mock_notify):
        file1 = self.create_test_file("file1.txt", 5)
        file2 = self.create_test_file("file2.txt", 8)
        delete_old_files(self.test_dir, days_old=7)

        if platform.system() == MAC_OS:
            title = f"Warning: About to delete 1 files in {self.test_dir}"
            msg = f"Do you want to delete files {[file2]}?"
            mock_notify.assert_called_with(title, msg)

        # Make sure file1 is not deleted but file2 is
        self.assertTrue(os.path.exists(file1))
        self.assertFalse(os.path.exists(file2))


if __name__ == "__main__":
    unittest.main()
