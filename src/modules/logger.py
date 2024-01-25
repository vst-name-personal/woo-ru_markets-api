import os
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))

def dir_exists(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_logger(log_file_path, level):
    dir_exists(log_file_path)

    file_handler = logging.FileHandler(log_file_path, mode='w')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger = logging.getLogger('my_logger')
    logger.addHandler(file_handler)
    logger.setLevel(level)

    return logger

def create_main_logger():
    log_file = "../logs/main.log"
    log_file_path = os.path.join(current_dir, log_file)
    logger = create_logger(log_file_path, logging.DEBUG)
    return logger

def create_ozon_logger():
    log_file = "../logs/ozon.log"
    log_file_path = os.path.join(current_dir, log_file)
    ozon_logger =  create_logger(log_file_path, logging.DEBUG)
    return ozon_logger

logger = create_main_logger()
ozon_logger = create_ozon_logger()