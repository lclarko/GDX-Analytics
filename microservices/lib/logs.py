# ref: https://github.com/acschaefer/duallog

import inspect
import logging
import os

# Define the default logging message formats.
FILE_FORMAT = '%(levelname)s:%(name)s:%(asctime)s:%(message)s'
CONS_FORMAT = '%(message)s'


def setup(dir='logs', minLevel=logging.INFO):
    """ Set up dual logging to console and to logfile.
    """

    # Create the root logger.
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create the log filename based on caller filename
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    file_name = module.__file__.replace('.py', '.log')

    # Validate the given directory.
    dir = os.path.normpath(dir)

    # Create a folder for the logfiles.
    if not os.path.exists(dir):
        os.makedirs(dir)

    # Construct the name of the logfile.
    file_path = os.path.join(dir, file_name)

    # Set up logging to the logfile.
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(FILE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Set up logging to the console.
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(minLevel)
    stream_formatter = logging.Formatter(CONS_FORMAT)
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
