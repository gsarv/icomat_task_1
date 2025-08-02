"""

This library provides utilities that are used often in several scripts

Functions:
- output_file_path: Build an output file path based on an input file.
- check_file: Validate the existence of a file.
- redirect_output: Context manager to capture stdout and stderr to a log.

"""
import os
import sys
from contextlib import contextmanager

##########################################

def output_file_path(input_file, filename):
    """
    Generates an output file path in the same directory as the input file,
    using the provided filename.

    Parameters:
        input_file (str): Path to an existing file (e.g., STEP file).
        filename (str): Filename to use for the output (e.g., log file name).

    Returns:
        str: Full path combining the directory of input_file and filename.
    """

    root, file  = os.path.split(input_file)
    output_file = os.path.join(root, filename)

    return output_file

##########################################

def check_file(path):
    """
    Checks if the given path points to an existing file.

    Parameters:
        path (str): Path to check.

    Returns:
        str: The same path if the file exists.

    Raises:
        OSError: If the file does not exist.
    """
    if not os.path.isfile(path):
        raise OSError("File does not exist: {}".format(path))
    
    return path

##########################################

@contextmanager
def redirect_output(logfile_path):
    """
    Context manager to redirect stdout and stderr to the specified log file.

    All output printed inside the context
    will be written to the log file instead of the terminal.

    Parameters:
        logfile_path (str): Path to the log file.

    Usage:
        with redirect_output("my_log.txt"):
            # code whose output you want to capture
            ...
    """
    saved_stdout_fd = os.dup(sys.stdout.fileno())
    saved_stderr_fd = os.dup(sys.stderr.fileno())

    with open(logfile_path, 'a') as log_file:
        try:
            os.dup2(log_file.fileno(), sys.stdout.fileno())
            os.dup2(log_file.fileno(), sys.stderr.fileno())
            yield
        finally:
            os.dup2(saved_stdout_fd, sys.stdout.fileno())
            os.dup2(saved_stderr_fd, sys.stderr.fileno())
            os.close(saved_stdout_fd)
            os.close(saved_stderr_fd)

##########################################

            

