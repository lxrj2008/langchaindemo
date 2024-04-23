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

    # ������־����
    logger_info.setLevel(logging.INFO)
    logger_error.setLevel(logging.ERROR)

    # �����ļ�����������ڴ��� info ����� error �������־
    info_handler = TimedRotatingFileHandler(os.path.join(log_folder, 'info.log'), when='midnight', interval=1, backupCount=7)
    error_handler = TimedRotatingFileHandler(os.path.join(log_folder, 'error.log'), when='midnight', interval=1, backupCount=7)

    # ������־��ʽ
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    info_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    # �����������ӵ���־��¼��
    logger_info.addHandler(info_handler)
    logger_error.addHandler(error_handler)

    return logger_info, logger_error

if __name__ == "__main__":
    logger_info, logger_error = setup_logging()
    # ʾ����־��¼
    logger_info.info('This is an info message')
    logger_error.error('This is an error message')
