"""
NetScan
"""
import sys
import logging
import traceback
import io
import re
import time
import os
import wx

MYNAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]
MYDIR = '{HOME}/.config/{NAME}'.format(HOME=os.getenv("HOME"), NAME=MYNAME)
LOGGER = None

PURPLE = '\033[95m'
CYAN = '\033[96m'
DARKCYAN = '\033[36m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

ESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
COLORS = {
    'DEBUG':    BLUE,
    'INFO':     GREEN,
    'WARNING':  CYAN,
    'ERROR':    YELLOW,
    'CRITICAL': RED
}

def date():
    """
    date
    """
    return time.strftime("%a %b %d %H:%M:%S UTC %Y", time.gmtime())

class ColoredFormatter(logging.Formatter):
    """ Class to color the log messages. """
    def format(self, record):
        record.msg = COLORS[record.levelname] + record.msg + END
        return logging.Formatter.format(self, record)

class MainFrame(wx.Frame):
    """
    MainFrame
    """
    def __init__(self, *args, **kw):
        super(MainFrame, self).__init__(*args, **kw)

def main():
    """
    main
    """

    # requests.packages.urllib3.disable_warnings()

    app = wx.App()
    frm = MainFrame(None, title='{0}'.format(MYNAME))
    frm.Show()
    frm.Fit()
    app.MainLoop()

if __name__ == '__main__':
    FORMAT_STRING = "%(asctime)s [%(levelname)-8.8s %(filename)s:%(lineno)4d]  %(message)s"
    LOGFORMATTER = logging.Formatter(FORMAT_STRING)
    CLOGFORMATTER = ColoredFormatter(FORMAT_STRING)
    LOGGER = logging.getLogger(__name__)
    FILENAME = '{0}-log-{1}.log'.format(MYNAME, re.sub(' ', '_', date()))
    FILEHANDLER = logging.FileHandler(FILENAME)
    FILEHANDLER.setFormatter(LOGFORMATTER)
    LOGGER.addHandler(FILEHANDLER)
    CONSOLEHANDLER = logging.StreamHandler()
    CONSOLEHANDLER.setFormatter(CLOGFORMATTER)
    LOGGER.addHandler(CONSOLEHANDLER)
    LOGGER.setLevel(logging.INFO)
    LOGGER.info('Command line: %s', ' '.join(sys.argv))

    try:
        main()
    except Exception as global_error:
        FP = io.StringIO()
        LOGGER.critical('Unhandled exception: %s', type(global_error))
        LOGGER.critical('Arguments: %s', (global_error.args,))
        traceback.print_exc(file=FP)
        for line in FP.getvalue().splitlines():
            LOGGER.critical(line.strip())
        print(RED + 'The script encountered an unexpected error.' + END)
        print(RED + 'The log has been saved to the file {0}.'.format(FILENAME) + END)
        print(RED + "This script will now exit." + END)
