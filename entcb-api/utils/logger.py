import logging


class LoggingService:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def log_error(self, message):
        logging.error(message)


logger = LoggingService()
