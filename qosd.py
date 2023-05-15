#!/usr/bin/env python3

VERSION = "20230510"
DESCRIPTION = "OSD from python"
EXAMPLES = """examples:
qosd hello
tail -f /var/log/{messages,auth.log} | qosd -
"""

from pathlib import Path
import argparse
import fcntl
import socket
import signal
import time
import sys
import os

from PySide6 import QtWidgets, QtGui, QtCore

class Qosd_win(QtWidgets.QMainWindow):
    STYLE = 'color:"#FFFFFF";background-color:"#99000000";font-size:11pt;font-weight:bold;'
    OPACITY = 1.0

    def __init__(self, style=STYLE, opacity=OPACITY):
        super().__init__(None, QtCore.Qt.X11BypassWindowManagerHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(style)
        self.setWindowOpacity(opacity)

        self.layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(self)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def mouseReleaseEvent(self, ev):
        self.hide()

class Qosd(object):
    TIMEOUT = 2.5
    MAXLINES = 20
    def __init__(self, style, opacity, timeout=TIMEOUT, maxlines=MAXLINES):
        self.maxlines = maxlines
        self.app = QtWidgets.QApplication([])
        self.win = Qosd_win(style, opacity)
        self.text_log = ""
        self.win.show()
        self.win.raise_()
        self.visible = True
        self.stdin = None

        if timeout:
            self.timeout = timeout
            self.to = QtCore.QTimer()
            self.to.timeout.connect(self._timeout)
            self.to.start(int(timeout * 1000))
        else:
            self.to = None

    def _timeout(self):
        self.visible = False
        self.win.hide()
        if self.to:
            self.to.stop()
        if not self.stdin:
            self.win.close()
            self.app.exit()

    def text(self, text):
        if self.visible:
            self.text_log += text
        else:
            self.text_log = text
        lines = self.text_log.split('\n')
        if len(lines) > self.maxlines:
            self.text_log = '\n'.join(lines[-self.maxlines:])
        self.win.label.setText(self.text_log.strip())
        self.win.label.adjustSize()
        self.win.resize(self.win.label.width(), self.win.label.heightForWidth(self.win.label.width()))
        #import IPython; from IPython import embed; embed()

    def text_stdin(self):
        flags = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        self.stdin = QtCore.QSocketNotifier(sys.stdin.fileno(), QtCore.QSocketNotifier.Read, self.win)
        self.stdin.activated.connect(self._cb_read_stdin)
        self.stdin.setEnabled(True)

    def _cb_read_stdin(self):
        while True:
            try:
                data = os.read(sys.stdin.fileno(), 1024)
            except Exception as e:
                # nothing to read
                break
            if not data:
                # stdin is closed, disable self.stdin SocketNotifier
                self.stdin.setEnabled(False)
                self.stdin = None
                break
            text = data.decode(errors='ignore')
            self.text(text)
        if not self.visible:
            self.visible = True
            self.win.show()
            self.win.raise_()
        if self.to:
            self.to.start(int(self.timeout * 1000))

    def run(self):
        self.app.exec()

    @classmethod
    def clear_session(cls, session_name):
        pidfile = Path("/tmp") / (session_name + ".pid")
        pidfile.unlink()

    @classmethod
    def setup_session(cls, session_name):
        pidfile = Path("/tmp") / (session_name + ".pid")
        if pidfile.exists():
            try:
                pid = int(pidfile.read_text().strip())
            except Exception:
                print("Ignoring invalid session pidfile '%s'" % pidfile)
            try:
                os.kill(pid, 15)
                print("killed existing session")
            except Exception:
                pass
        pidfile.write_text(str(os.getpid()))

def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION+" - v"+VERSION, epilog=EXAMPLES, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-m', '--maxlines', type=int, default=Qosd.MAXLINES, help='default: %s' % Qosd.MAXLINES)
    parser.add_argument('-n', '--session-name', help='start named OSD display session, killing previous OSD with same session name')
    parser.add_argument('-o', '--opacity', type=float, default=Qosd_win.OPACITY, help='default: %s' % Qosd_win.OPACITY)
    parser.add_argument('-s', '--style', default=Qosd_win.STYLE, help='default: \'%s\'' % Qosd_win.STYLE)
    parser.add_argument('-t', '--timeout', type=float, default=Qosd.TIMEOUT, help='display timeout in stdin mode, default: %s' % Qosd.TIMEOUT)
    parser.add_argument('text', nargs="+", help='text to display, or \'-\' for stdin')

    args = parser.parse_args()

    # use OS signal handler, to exit on ctrl-c while in Qt loop
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    if args.session_name:
        Qosd.setup_session(args.session_name)

    osd = Qosd(args.style, args.opacity, args.timeout, args.maxlines)
    text = args.text
    if type(text) is list:
        text = ' '.join(args.text)
    if text == '-':
        osd.text_stdin()
    else:
        osd.text(text)
    osd.run()

    if args.session_name:
        Qosd.clear_session(args.session_name)

if __name__ == "__main__":
    sys.exit(main())

