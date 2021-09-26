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
import nmap
from pprint import pprint
import wx
import wx.lib.scrolledpanel

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
        fileMenu = wx.Menu()
        scanItem = fileMenu.Append(wx.ID_ANY, 'Scan')
        exitItem = fileMenu.Append(wx.ID_EXIT)
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.scan, scanItem)

        self.panel = wx.Panel(self, size=(1024, 720))
        self.notebook = wx.Notebook(self.panel)

        self.sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.sizer.Add(self.notebook, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25).Expand().Proportion(10))
        self.panel.SetSizer(self.sizer)

        self.tabs = []

        self.CreateStatusBar()
        self.SetStatusText("{0} hosts found".format(len(self.tabs)))

    def insert(self, tree, item, data):
        if type(data) == str:
            tree.SetItemText(item, '{0} = {1}'.format(tree.GetItemText(item), data))
        elif type(data) == list:
            for i in data:
                # nitem = tree.AppendItem(item, '{0}'.format(i))
                self.insert(tree, item, i)
        elif type(data) == dict:
            for i in data:
                nitem = tree.AppendItem(item, '{0}'.format(i))
                self.insert(tree, nitem, data[i])

    def scan(self, event):
        LOGGER.info("Scan started")
        port_scanner = nmap.nmap.PortScannerYield()
        # for host in port_scanner.scan(hosts='10.1.1.1/24', arguments='-sV --version-intensity 0'):
        # for host in port_scanner.scan(hosts='10.1.1.1/24', arguments='-A -T4'):
        for host in port_scanner.scan(hosts='10.1.1.1/24', arguments='-sn'):
        # for host in port_scanner.scan(hosts='10.1.1.1/28', arguments='-PE -n'):
            if len(host[1]['scan']):
                pprint(host)
                panel = wx.lib.scrolledpanel.ScrolledPanel(self.notebook)
                sizer = wx.BoxSizer(orient=wx.VERTICAL)
                panel.SetSizer(sizer)
                for ip in host[1]['scan'].keys():
                    tree = wx.TreeCtrl(panel)
                    sizer.Add(tree, 1, wx.EXPAND)
                    root = tree.AddRoot(ip)
                    for attrib in host[1]['scan'][ip].keys():
                        item = tree.AppendItem(root, attrib)
                        self.insert(tree, item, host[1]['scan'][ip][attrib])
                    tree.ExpandAll()
                '''
                    ip_panel =  wx.StaticBox(panel, label=ip)
                    sizer.Add(ip_panel, 1, wx.EXPAND)
                    ip_sizer = wx.BoxSizer(orient=wx.VERTICAL)
                    ip_panel.SetSizer(ip_sizer)
                    for attrib in host[1]['scan'][ip].keys():
                        attrib_panel =  wx.StaticBox(ip_panel, label=attrib)
                        ip_sizer.Add(attrib_panel, 1, wx.EXPAND)
                        attrib_sizer = wx.BoxSizer(orient=wx.VERTICAL)
                        attrib_panel.SetSizer(attrib_sizer)
                        for item in host[1]['scan'][ip][attrib]:
                            attrib_sizer.Add(wx.StaticText(attrib_panel, label="{0}".format(item)), 1, wx.EXPAND)
                        # LOGGER.debug("{0} {1}".format(attrib, list(host[1]['scan'][ip][attrib])))
                '''
                self.tabs.append(panel)
                panel.SetupScrolling()
                self.notebook.AddPage(self.tabs[len(self.tabs) - 1], host[0])
                self.SetStatusText("{0} hosts found".format(len(self.tabs)))
            else:
                LOGGER.debug("Host %s is not alive" % host[0])
            wx.GetApp().Yield()
        LOGGER.info("Scan ended")

    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

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
    LOGGER.setLevel(logging.DEBUG)
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
