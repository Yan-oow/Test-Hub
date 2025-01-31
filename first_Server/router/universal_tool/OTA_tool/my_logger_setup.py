import logging
import os
import datetime

def setup_logger(version):
    current_path = os.path.abspath('.')
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")
    
    # # 日志目录的创建和检查
    # if not os.path.exists(os.path.join(current_path, 'logs')):
    #     os.mkdir(os.path.join(current_path, 'logs'))
    
    # 创建logger对象
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 创建用于输出到控制台的处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # # 创建用于输出到文件的处理器
    # log_filename = os.path.join(current_path, 'logs', f"log_{formatted_time}.txt")
    # file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    # file_handler.setLevel(logging.INFO)
    log_filename = 1
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message).2000s')
    
    # # 应用格式化器到处理器
    # console_handler.setFormatter(formatter)
    # file_handler.setFormatter(formatter)
    
    # # 将处理器添加到logger对象中
    # logger.addHandler(console_handler)
    # logger.addHandler(file_handler)
    
    # 记录当前版本
    logger.info(f"Current Version {version}")
    
    return logger, log_filename, formatted_time, current_path
