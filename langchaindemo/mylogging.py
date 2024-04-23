import os
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logging():
    # ��鲢������־�ļ���
    log_folder = 'syslog'
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # ������־��¼��
    logger_info = logging.getLogger('info_logger')
    logger_error = logging.getLogger('error_logger')
    logger_debug = logging.getLogger('error_debug')

    # ������־����
    logger_info.setLevel(logging.INFO)
    logger_error.setLevel(logging.ERROR)
    logger_debug.setLevel(logging.DEBUG)
    # �����ļ�����������ڴ��� info ����� error �������־
    info_handler = TimedRotatingFileHandler(os.path.join(log_folder, 'info.log'), when='midnight', interval=1, backupCount=30)
    error_handler = TimedRotatingFileHandler(os.path.join(log_folder, 'error.log'), when='midnight', interval=1, backupCount=30)
    debug_handler = TimedRotatingFileHandler(os.path.join(log_folder, 'debug.log'), when='midnight', interval=1, backupCount=30)

    # ������־��ʽ
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    info_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    debug_handler.setFormatter(formatter)

    # �����������ӵ���־��¼��
    logger_info.addHandler(info_handler)
    logger_error.addHandler(error_handler)
    logger_debug.addHandler(debug_handler)

    return logger_info, logger_error,logger_debug

if __name__ == "__main__":
    logger_info, logger_error,logger_debug = setup_logging()
    # ʾ����־��¼
    logger_info.info('This is an info message')
    logger_error.error('This is an error message')
    logger_debug.info('This is an debug message')
