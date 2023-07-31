"""This is an extract copy of the original Folder_sync.py file with the additional methods stop_sync_thread() and start_sync_thread(), 
so the folder synchronization can be controlled by a separate thread."""

import argparse
from datetime import datetime
import os
import time
import signal
import sys
import hashlib
import shutil

from Logger import SingletonLogger

sync_on = True

def get_md5sum_of_file_list(file_list, foldername):
    """Return a dictionary from the given list of files, where the file path is the key and md5sum is the value."""
    file_dictionary = {}
    sync_logger = SingletonLogger()
    for filename in file_list:
        filepath = os.path.join(foldername, filename)
        try:
            file_dictionary[filepath] = hashlib.md5(open(filepath, "rb").read()).hexdigest()
        except Exception as e:
            sync_logger.logger.info(f"Error calculating md5sum of the file {filename}: {e}")
    return file_dictionary


def check_file_with_same_md5sum(check_file_path, check_md5sum, list_of_files):
    """ Check the given file md5sum found in list of files with different name."""
    for file_path, md5sum in list_of_files.items():
        if (
            os.path.basename(file_path) != os.path.basename(check_file_path)
            and md5sum == check_md5sum
        ):
            return True, file_path
    return False, ""


def check_file_exist(check_file_path, check_md5sum, list_of_files):
    """ Check the given file with same md5sum found in the list of files."""
    for file_path, md5sum in list_of_files.items():
        if (
            os.path.basename(file_path) == os.path.basename(check_file_path)
            and md5sum == check_md5sum
        ):
            return True
    return False


def check_and_delete_extra_files(list_source_files, list_replica_files):
    """Delete all the files from the replica folder file list if not found in the source folder file list."""
    sync_logger = SingletonLogger()
    for replica_file_path, replica_md5sum in list_replica_files.items():
        if not check_file_exist(replica_file_path, replica_md5sum, list_source_files):
            try:
                os.remove(replica_file_path)
                sync_logger.logger.info(
                    f"File '{replica_file_path}' has been deleted successfully."
                )
            except FileNotFoundError:
                sync_logger.logger.info(
                    f"File '{replica_file_path}' not found. Unable to delete."
                )
            except PermissionError:
                sync_logger.logger.info(
                    f"Permission denied. Unable to delete file '{replica_file_path}'."
                )
            except Exception as e:
                sync_logger.logger.info(
                    f"An error occurred while deleting the file '{replica_file_path}': {e}"
                )


def create_folder_and_get_contents(folder_path, create_new_folder=True):
    """
    Check if the folder exists, create the folder if it doesn't exist and return the content list of the folder
    """
    sync_logger = SingletonLogger()
    if not os.path.exists(folder_path) and create_new_folder:
        try:
            os.makedirs(folder_path)
            sync_logger.logger.info(f"Directory '{folder_path}' successfully created.")
        except Exception as e:
            sync_logger.logger.info(f"Error creating directory: {e}")

    content_list = os.listdir(folder_path)
    files_only = [
        item for item in content_list if os.path.isfile(os.path.join(folder_path, item))
    ]
    return files_only


def sync_folder_by_copy_and_delete_files(
    source_files_dict, replica_files_dict, replica_folder
):
    """"Synchronize source folder content with replica folder content."""
    sync_logger = SingletonLogger()
    for file, md5sum in source_files_dict.items():
        # Copy the file in the replica folder if it is not found.
        file_exist = check_file_exist(file, md5sum, replica_files_dict)
        if not file_exist:
            try:
                shutil.copy(file, replica_folder + "/" + os.path.basename(file))
                sync_logger.logger.info(f"File '{file}' has been copied successfully.")
            except FileNotFoundError:
                sync_logger.logger.info(f"File '{file}' not found. Unable to copy.")
            except PermissionError:
                sync_logger.logger.info(
                    f"Permission denied. Unable to copy file '{file}'."
                )
            except Exception as e:
                sync_logger.logger.info(
                    f"An error occurred while copying the file '{file}': {e}"
                )

    # Delete all the files from the replica folder if not found in the source folder
    check_and_delete_extra_files(source_files_dict, replica_files_dict)


def get_all_subfolders(root_folder):
    """ Fetch and return the sub-folder list of the given root folder."""
    sub_folder_list = []
    for foldername, subfolders, _ in os.walk(root_folder):
        for subfolder in subfolders:
            subfolder_path = os.path.relpath(
                os.path.join(foldername, subfolder), root_folder
            )
            sub_folder_list.append(subfolder_path)
    return sub_folder_list


def delete_non_existing_sub_folders(
    replica_sub_folder_list, source_sub_folder_list, replica_folder
):
    """Compare the replica sub-folder list with the source sub-folder list and 
    delete any non-existing sub-folders from the replica folder.  
    """
    sync_logger = SingletonLogger()
    for sub_dir in replica_sub_folder_list:
        if sub_dir not in source_sub_folder_list:
            try:
                sub_dir_full_path = os.path.join(replica_folder, sub_dir)
                shutil.rmtree(sub_dir_full_path)
                sync_logger.logger.info(
                    f"Directory '{sub_dir_full_path}' successfully deleted."
                )
            except Exception as e:
                sync_logger.logger.info(f"Error deleting directory: {e}")


def sync_folder(source_folder, replica_folder):
    """
    Start synchronizing source root folder and then each sub folders inside it.
    Delete any sub-folders from replica directory if not exist in the source directory.
    """
    source_folder_subdirectories = []

    # Synchronize the root folder
    source_file_list = create_folder_and_get_contents(source_folder, False)
    replica_file_list = create_folder_and_get_contents(replica_folder, False)
    source_files_dictionary = get_md5sum_of_file_list(
        file_list=source_file_list, foldername=source_folder
    )
    replica_files_dictionary = get_md5sum_of_file_list(
        file_list=replica_file_list, foldername=replica_folder
    )
    sync_folder_by_copy_and_delete_files(
        source_files_dictionary, replica_files_dictionary, replica_folder
    )

    # Synchronize the sub-folders
    for foldername, subfolders, filenames in os.walk(source_folder):
        for subfolder in subfolders:
            subfolder_path = os.path.relpath(
                os.path.join(foldername, subfolder), source_folder
            )
            source_folder_subdirectories.append(subfolder_path)
            source_sub_folder = os.path.join(source_folder, subfolder_path)
            replica_sub_folder = os.path.join(replica_folder, subfolder_path)
            source_file_list = create_folder_and_get_contents(source_sub_folder)
            replica_file_list = create_folder_and_get_contents(replica_sub_folder)
            source_files_dictionary = get_md5sum_of_file_list(
                file_list=source_file_list, foldername=source_sub_folder
            )
            replica_files_dictionary = get_md5sum_of_file_list(
                file_list=replica_file_list, foldername=replica_sub_folder
            )
            sync_folder_by_copy_and_delete_files(
                source_files_dictionary, replica_files_dictionary, replica_sub_folder
            )

    # Delete the replica folder subfolders if not exist in the source folder
    replica_sub_folder_list = get_all_subfolders(replica_folder)
    delete_non_existing_sub_folders(
        replica_sub_folder_list, source_folder_subdirectories, replica_folder
    )


# def signal_handler(sig, frame):
#     """
#     Print exit message when stop signal received.
#     """
#     print("Folder synchronization stopped....")
#     exit(0)


def check_for_valid_dir(directory_path, dir_name):
    """Check the given path is a valid directory if not exit the program with message."""
    sync_logger = SingletonLogger()
    if not (os.path.exists(directory_path) and os.path.isdir(directory_path)):
        sync_logger.logger.info(f"{dir_name} folder {directory_path} does not exist")
        sync_logger.logger.info("Synchronization stopped...")
        exit(0)


def argument_parser():
    """"Parse the command line arguments and start folder synchronization."""
    arg_parser = argparse.ArgumentParser("Folder sync arguments")
    arg_parser.add_argument(
        "source_folder", type=str, help="full path to the source folder"
    )
    arg_parser.add_argument(
        "replica_folder", type=str, help="full path to the replica folder"
    )
    arg_parser.add_argument(
        "log_file_path", type=str, help="full path to store the log files"
    )
    arg_parser.add_argument("sync_interval", type=int, help="synchronization interval in seconds")

    args = arg_parser.parse_args()
    folder_sync_main(args.source_folder, args.replica_folder, args.log_file_path, args.sync_interval)


def folder_sync_main(source_folder, replica_folder, log_file_path, sync_interval):
    """
    Validate the command line arguments and start and run the folder synchronization in the given
    interval.
    """
    # signal.signal(signal.SIGINT, signal_handler)
    sync_logger = SingletonLogger(log_file_path)

    check_for_valid_dir(source_folder, "Source")
    check_for_valid_dir(replica_folder, "Replica")

    global sync_on
    sync_logger.logger.info(f"Source synchronization folder {source_folder}")
    sync_logger.logger.info(f"Replica Synchronization folder {replica_folder}")
    sync_logger.logger.info(f"Log file location {log_file_path}")
    sync_logger.logger.info(f"Synchronization interval {sync_interval}")
    sync_logger.logger.info("Press Ctrl + C to stop Synchronization")
    while sync_on:
        sync_logger.logger.info(
            f"Folder synchronization started on {datetime.now().strftime('%H:%M %d_%m_%Y')}"
        )
        sync_folder(source_folder, replica_folder)
        time.sleep(sync_interval)


def stop_sync_thread():
    global sync_on
    sync_on = False


def start_sync_thread():
    global sync_on
    sync_on = True


if __name__ == "__main__":
    argument_parser()
