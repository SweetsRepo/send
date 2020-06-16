"""
Topical logging system inspired by Kivy project.

Log levels include INFO, WARNING, DEBUG, and ERROR

"""
import os
import sys
import logging
from datetime import datetime

# Path to log directory and number of log files to keep
LOG_PATH = os.path.join(os.path.expanduser("~"), "SEND", "logs")
MAX_TO_KEEP = 5

# Coloration and special sequences
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = list(range(8))
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"

# Helper lambda to insert new reset sequence
format_msg = lambda msg: msg.replace("%RESET", RESET_SEQ)

COLORS = {
    "WARNING": YELLOW,
    "INFO": GREEN,
    "DEBUG": CYAN,
    "ERROR": RED
}

previous_stderr = sys.stderr

class TopicFormatter(logging.Formatter):
    """
    Add colored output to logs on terminal window
    """
    def __init__(self, msg):
        logging.Formatter.__init__(self, msg)

    def format(self, record):
        """
        Formats the message into SUBJECT: MESSAGE

        Arguments:
            record: Log message to process

        Returns:
            record: Log message with formatting applied

        """
        try:
            msg = record.msg.replace('[','').replace(']','')
            msg = msg.split(':',2)
            if len(msg) == 2:
                record.msg = "[%-12s]%s" % (msg[0], msg[1])
        except:
            pass
        levelname = record.levelname
        if levelname in COLORS:
            levelname_color = (
                COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            )
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)

class ConsoleHandler(logging.StreamHandler):
    """
    Handler for streaming to terminal. Makes use of TopicFormatter for
    coloration and adds in filtering of topics separated by ':'

    """
    def filter(self, record):
        """
        Filters messages based off topic given before ':'

        Arguments:
            record: Log message to process

        Returns:
            success: Flag indicating if message went to stderr or not
        """
        success = True
        try:
            msg.record.msg.split(':', 1)
            if msg[0] == "stderr" and len(msg) == 2:
                previous_stderr.write(msg[1] + "\n")
                success = False
        except:
            pass
        return success

class FileHandler(logging.Handler):
    """
    Handler to write log files to User Home Directory with limits on # of files
    """
    current_time = datetime.now().strftime("%m%d%Y_%H%M%S")
    fname = f"{LOG_PATH}/SEND_{time}.log"
    buffer = None

    def _configure(self, *args, **kwargs):
        if FileHandler.buffer is not None:
            return
        files = os.listdir(LOG_PATH)
        if len(files) >= MAX_TO_KEEP:
            files = sorted(files)
            files_to_remove = len(files) - MAX_TO_KEEP - 1
            while files_to_remove > 0:
                os.remove(os.path.join(LOG_PATH, files[0]))
                del files[0]
                files_to_remove -= 1
        FileHandler.buffer = open(FileHandler.filename, 'w')

    def _write_message(self, record):
        # Make sure FileHandler has been configured/has not run into any errors
        if FileHandler.buffer in (None, False):
            return
        msg = self.format(record)
        format = "%s\n"
        FileHandler.buffer.write("[%-7s] " % record.levelname)
        FileHandler.buffer.write(format % msg)
        FileHandler.buffer.flush()

    def emit(self, message):
        if FileHandler.buffer is None:
            try:
                self._configure()
            except:
                FileHandler.buffer = False
        self._write_message(message)

# Make sure that the log path exists
os.makedirs(LOG_PATH, exist_ok=True)

# Create the logger instance and set it as root
logger = logging.getLogger(__name__)
logger.setlevel(1)
logging.root = logger

# Create the file handler and set a generic formatter
handler = FileHandler()
handler.setFormatter(FileFormatter(""))
logger.addHandler(handler)

# Create the console handler and set our prettified formatter
format = format_msg("[%(levelname)-18s] %(message)s")
formatter = ConsoleFormatter(format)
console = ConsoleHandler()
console.setFormatter(formatter)
logger.addHandler(console)

# Expose our interface (e.g. log.info(Initialization: Logger Started))
log = logger
