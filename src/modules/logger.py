import os
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))

def dir_exists(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_logger(log_file_path, level, name):
    dir_exists(log_file_path)

    file_handler = logging.FileHandler(log_file_path, mode='w')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    logger.setLevel(level)

    return logger

def create_main_logger():
    log_file = "../logs/main.log"
    log_file_path = os.path.join(current_dir, log_file)
    name = "logger"
    logger = create_logger(log_file_path, logging.DEBUG, name)
    return logger

def create_ozon_logger():
    log_file = "../logs/ozon.log"
    log_file_path = os.path.join(current_dir, log_file)
    name = "ozon_logger"
    ozon_logger =  create_logger(log_file_path, logging.DEBUG, name)
    return ozon_logger

def create_wb_logger():
    log_file = "../logs/wb.log"
    log_file_path = os.path.join(current_dir, log_file)
    name = "wb_logger"
    wb_logger =  create_logger(log_file_path, logging.DEBUG, name)
    return wb_logger
def create_ym_logger():
    log_file = "../logs/ym.log"
    log_file_path = os.path.join(current_dir, log_file)
    name = "ym_logger"
    ym_logger =  create_logger(log_file_path, logging.DEBUG, name)
    return ym_logger

ozon_logger = create_ozon_logger()
wb_logger = create_wb_logger()
ym_logger = create_ym_logger()
logger = create_main_logger()