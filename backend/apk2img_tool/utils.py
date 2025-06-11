import os
import shutil

def create_directories(dirs):
    """
    Creates directories if they don't exist.

    Args:
        dirs (list): List of directory paths to create.
    """
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

def cleanup_directories(dirs):
    """
    Removes directories.

    Args:
        dirs (list): List of directory paths to remove.
    """
    for dir_path in dirs:
        shutil.rmtree(dir_path, ignore_errors=True)

def cleanup_files(files):
    """
    Removes files.

    Args:
        files (list): List of file paths to remove.
    """
    for file_path in files:
        if os.path.exists(file_path):
            os.remove(file_path)