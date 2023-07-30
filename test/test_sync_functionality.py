import sys
sys.path.append('.//')
from Folder_sync import *
import unittest
import os

TEST_FOLDER_01 = "./test_source_1"
TEST_FOLDER_02 = "./test_source_2"
TEST_FOLDER_03 = "./test_source_3"
REPLICA_FOLDER = "./replica"
LOG_FOLDER = "./log"

def get_full_path(relative_path):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_directory, relative_path)

class Test_folder_sync(unittest.TestCase):

    # def clear_test_folder(folder_path):
    #     if os.path.exists(folder_path) and os.path.isdir(folder_path):
    #         try:
    #             shutil.rmtree(folder_path)
    #             print(f"Contents of {folder_path} deleted successfully.")
    #         except Exception as e:
    #             print(f"Error deleting contents of {folder_path}: {e}")
    #         else:
    #             print("Folder does not exist or is not a directory.")


    def setUp(self) -> None:
        """Clear the replica folder"""
        if os.path.exists(REPLICA_FOLDER) and os.path.isdir(REPLICA_FOLDER):
            try:
                shutil.rmtree(REPLICA_FOLDER)
                print(f"Contents of {REPLICA_FOLDER} deleted successfully.")
            except Exception as e:
                print(f"Error deleting contents of {REPLICA_FOLDER}: {e}")
            else:
                print("Folder does not exist or is not a directory.")


    def test_01(self):
        folder_sync_main(source_folder=get_full_path(TEST_FOLDER_01), 
                         replica_folder=get_full_path(REPLICA_FOLDER), log_file_path=get_full_path(LOG_FOLDER),
                         sync_interval=5)


    def test_02(self):
        # self.assertEqual(self.return_list, ["unit0"])
        pass


    def test_03(self):
        pass


    def test_04(self):
        pass


if __name__ == "__main__":
    unittest.main()