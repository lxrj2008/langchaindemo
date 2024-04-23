import os
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logging():
    # 检查并创建日志文件夹
    log_folder = 'syslog'
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # 创建日志记录器
    logger_info = logging.getLogger('info_logger')
    logger_error = logging.getLogger('error_logger')

    # 设置日志级别
    logger_info.setLevel(logging.INFO)
    logger_error.setLevel(logging.ERROR)

    # 创建文件处理程序，用于处理 info 级别和 error 级别的日志
    info_handler = TimedRotatingFileHandler(os.path.join(log_folder, 'info.log'), when='midnight', interval=1, backupCount=7)
    error_handler = TimedRotatingFileHandler(os.path.join(log_folder, 'error.log'), when='midnight', interval=1, backupCount=7)

    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    info_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    # 将处理程序添加到日志记录器
    logger_info.addHandler(info_handler)
    logger_error.addHandler(error_handler)

    return logger_info, logger_error

if __name__ == "__main__":
    logger_info, logger_error = setup_logging()
    # 示例日志记录
    logger_info.info('This is an info message')
    logger_error.error('This is an error message')
