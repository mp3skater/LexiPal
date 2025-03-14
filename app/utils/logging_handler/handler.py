import logging
from functools import wraps
from datetime import datetime


class QuestionLogger:
    def __init__(self, enabled=False, log_file=None, console_logging=False):
        self.enabled = enabled
        self.log_file = log_file
        self.console_logging = console_logging

        if self.enabled:
            # Create logger
            self.logger = logging.getLogger('question_logger')
            self.logger.setLevel(logging.INFO)

            # Create formatter
            formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

            # Add file handler if log_file is specified
            if self.log_file:
                file_handler = logging.FileHandler(self.log_file)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)

            # Add console handler if console_logging is True
            if self.console_logging:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)

    def log_questions(self, func):
        @wraps(func)
        def wrapper(questions, api_key, *args, **kwargs):
            if self.enabled:
                timestamp = datetime.now().isoformat()
                log_message = f"\n=== Questions at {timestamp} ===\n" + \
                              "\n".join(f"{i + 1}. {q}" for i, q in enumerate(questions))
                self.logger.info(log_message)

            answers, raw_response = func(questions, api_key, *args, **kwargs)

            if self.enabled:
                timestamp = datetime.now().isoformat()
                log_message = f"\n=== Answers at {timestamp} ===\n" + \
                              "\n".join(f"{i + 1}. {a}" for i, a in enumerate(answers))
                self.logger.info(log_message)
                self.logger.info(f"\n=== Raw Response ===\n{raw_response}\n")

            return answers, raw_response

        return wrapper


# Global configuration
LOGGING_ENABLED = True  # Change this to enable/disable logging
LOG_TO_FILE = False  # Set to True to log to file
LOG_TO_CONSOLE = True  # Set to True to log to console
LOG_FILE = 'app.log' if LOG_TO_FILE else None

logger = QuestionLogger(
    enabled=LOGGING_ENABLED,
    log_file=LOG_FILE,
    console_logging=LOG_TO_CONSOLE
)