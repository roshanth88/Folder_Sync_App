import sys
sys.path.append('.//')
# from Folder_sync import *
from Folder_sync_test_version import *
import unittest
import os
import threading


TEST_FOLDER_01 = "test_source_1"
TEST_FOLDER_02 = "test_source_2"
TEST_FOLDER_03 = "test_source_3"
REPLICA_FOLDER_01 = "replica1"
REPLICA_FOLDER_02 = "replica2"
REPLICA_FOLDER_03 = "replica3"
LOG_FOLDER = "logs/"

def get_full_path(relative_path):
    """Construct the full path from the relative path."""
    script_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_directory, relative_path)


def get_folder_content(directory_path):
    """"Return the list of all folder contents."""
    folder_content_list = []
    for root, directories, files in os.walk(directory_path):
        for dir_name in directories:
            dir_path = os.path.join(root, dir_name)
            folder_content_list.append(dir_path)

        for filename in files:
            file_path = os.path.join(root, filename)
            folder_content_list.append(file_path)
    return folder_content_list


def delete_folder_content(folder_path):
    """Delete all the contents of the given folder."""
    if os.path.exists(get_full_path(folder_path)) and os.path.isdir(get_full_path(folder_path)):
        try:
            for root, directories, files in os.walk(get_full_path(folder_path), topdown=False):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    os.remove(file_path)
                for dir_name in directories:
                    dir_path = os.path.join(root, dir_name)
                    shutil.rmtree(dir_path)
            print(f"Contents of {get_full_path(folder_path)} deleted successfully.")
        except Exception as e:
            print(f"Error deleting contents of {get_full_path(folder_path)}: {e}")
        else:
            print("Folder does not exist or is not a directory.")


class Test_folder_sync(unittest.TestCase):

    def setUp(self) -> None:
        """Clear the replica folders and turn on the thread controller."""
        delete_folder_content(REPLICA_FOLDER_01)
        delete_folder_content(REPLICA_FOLDER_02)
        delete_folder_content(REPLICA_FOLDER_03)
        start_sync_thread()


    def test_01(self):
        """Test case for synchronize few filess."""
        source_folder = get_full_path(TEST_FOLDER_01)
        replica_folder = get_full_path(REPLICA_FOLDER_01)
        log_file_path = get_full_path(LOG_FOLDER)
        sync_interval = 5
        thread = threading.Thread(target=folder_sync_main, args=(source_folder, replica_folder, log_file_path, sync_interval))
        thread.start()
        time.sleep(10)
        stop_sync_thread()
        source_folder_content_list = get_folder_content(get_full_path(TEST_FOLDER_01))
        replica_folder_content_list = get_folder_content(get_full_path(REPLICA_FOLDER_01))
        self.assertEqual(len(source_folder_content_list), len(replica_folder_content_list))


    def test_02(self):
        """Test case for synchronize large number of files ~6000."""
        source_folder = get_full_path(TEST_FOLDER_02)
        replica_folder = get_full_path(REPLICA_FOLDER_02)
        log_file_path = get_full_path(LOG_FOLDER)
        sync_interval = 15
        thread = threading.Thread(target=folder_sync_main, args=(source_folder, replica_folder, log_file_path, sync_interval))
        thread.start()
        time.sleep(40)
        stop_sync_thread()
        source_folder_content_list = get_folder_content(get_full_path(TEST_FOLDER_02))
        replica_folder_content_list = get_folder_content(get_full_path(REPLICA_FOLDER_02))
        self.assertEqual(len(source_folder_content_list), len(replica_folder_content_list))


    def test_03(self):
        """Test case for synchronize empty folder."""
        source_folder = get_full_path(TEST_FOLDER_03)
        replica_folder = get_full_path(REPLICA_FOLDER_03)
        log_file_path = get_full_path(LOG_FOLDER)
        sync_interval = 5
        thread = threading.Thread(target=folder_sync_main, args=(source_folder, replica_folder, log_file_path, sync_interval))
        thread.start()
        time.sleep(10)
        stop_sync_thread()
        source_folder_content_list = get_folder_content(get_full_path(TEST_FOLDER_03))
        self.assertEqual(len(source_folder_content_list), 0)


if __name__ == "__main__":
    unittest.main()