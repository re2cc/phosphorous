import chatController

from loguru import logger
import logging
from datetime import datetime, UTC

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
setup = logger.level("SETUP", no=26, color="<magenta>", icon="💻")
conv = logger.level("CONV", no=27, color="\u001b[30;1m", icon="💬")
utctime = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
logger.add("log/" + utctime + "/debug_" + utctime + ".log",
           format="{time} {level} {message}", level="DEBUG")
logger.add("log/" + utctime + "/info_" + utctime + ".log",
           format="{time} {level} {message}", level="INFO")
logger.add("log/" + utctime + "/conv_" + utctime + ".log",
           format="{level} {message}", level="SETUP")

#El msg del sistema es ese que dice "You ansewer shortly", el numero 0
c = chatController.ChatController("sk-proj-vfjH4tydJOk1A9tdxqQKT3BlbkFJWOVNXRpawSijxmRszr8H", "You ansewer shortly")
#El msg del usuario es "What is 5 + 5?", el numero 1
answer = c.answer_request("What is 5 + 5?")
#El msg de chatgpt es el contenido de answer, el numero 2
#El msg del usuario es "And 6 + 6?", el numero 1, el numero 3
answer = c.answer_request("And 6 + 6?")
#El msg de chatgpt es el contenido de answer, el numero 4