#!/usr/bin/env python3

VERSION = "20230518"
DESCRIPTION = "display text over your Xorg screen"
EXAMPLES = """examples:
$ qosd hello
$ tail -f /var/log/{messages,auth.log} | qosd -
"""

from pathlib import Path
import argparse
import fcntl
import signal
import sys
import os

from PySide6 import QtWidgets, QtGui, QtCore

class Qosd_win(QtWidgets.QMainWindow):
    STYLE = 'color:"#FFFFFF";background-color:"#99000000";font-size:11pt;font-weight:bold;'
    OPACITY = 1.0
    POSITION = "topleft"

    def __init__(self, qosd, style=STYLE, opacity=OPACITY, position=POSITION, offset=(0,0), no_input=False):
        flags = QtCore.Qt.X11BypassWindowManagerHint | QtCore.Qt.WindowStaysOnTopHint
        if no_input:
            flags |= QtCore.Qt.WindowTransparentForInput
        super().__init__(None, flags)
        self.qosd = qosd
        self.position = position
        self.offset = offset
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(style)
        self.setWindowOpacity(opacity)

        self.layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(self)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.installEventFilter(self)
        self.resize(0, 0)

    def eventFilter(self, obj, event):
        if not obj.isVisible():
            return False
        if type(event) == QtGui.QHoverEvent:
            if event.type() == QtGui.QHoverEvent.Type.HoverEnter:
                self.qosd.hide_to_stop()
            elif event.type() == QtGui.QHoverEvent.Type.HoverLeave:
                self.qosd.hide_to_start()
        elif type(event) == QtGui.QMouseEvent:
            if event.type() == QtGui.QMouseEvent.Type.MouseButtonPress:
                self.qosd.hide_or_exit()
        return True

    def updatePosition(self):
        sdim = self.screen().geometry()
        if self.position == "topleft":
            coord = (self.offset[0], self.offset[1])
        elif self.position == "topright":
            coord = ((sdim.right()-self.width())-self.offset[0], self.offset[1])
        elif self.position == "bottomleft":
            coord = (self.offset[0], (sdim.bottom()-self.height())+self.offset[1])
        elif self.position == "bottomright":
            coord = ((sdim.right()-self.width())-self.offset[0], (sdim.bottom()-self.height())-self.offset[1])
        self.move(coord[0], coord[1])

class Qosd(object):
    TIMEOUT = 3
    MAXLINES = 30

    def __init__(self, style, opacity, timeout=TIMEOUT, maxlines=MAXLINES, position=Qosd_win.POSITION, offset=(0,0), no_input=False):
        self.maxlines = maxlines
        self.app = QtWidgets.QApplication([])
        self.win = Qosd_win(self, style, opacity, position, offset, no_input)
        self.text_log = ""
        self.win.show()
        self.win.raise_()
        self.visible = True
        self.stdin = None

        if timeout:
            self.hide_timeout = timeout
            self.hide_to = QtCore.QTimer()
            self.hide_to.timeout.connect(self.hide_or_exit)
            self.hide_to_start()
        else:
            self.hide_to = None

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
        self.win.updatePosition()

    def text_stdin(self):
        flags = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        self.stdin = QtCore.QSocketNotifier(sys.stdin.fileno(), QtCore.QSocketNotifier.Read, self.win)
        self.stdin.activated.connect(self._cb_read_stdin)
        self.stdin.setEnabled(True)

    def history(self, signum, stack):
        self.win.close()
        self.app.exit()

    def run(self):
        self.app.exec()

    def exit(self):
        self.win.close()
        self.app.exit()

    def show(self):
        if not self.visible:
            self.visible = True
            self.win.show()
            self.win.raise_()
        self.hide_to_start()

    def hide_or_exit(self):
        self.visible = False
        self.win.hide()
        self.hide_to_stop()
        if not self.stdin:
            self.exit()

    def hide_to_start(self):
        if self.hide_to:
            self.hide_to.start(int(self.hide_timeout * 1000))

    def hide_to_stop(self):
        if self.hide_to:
            self.hide_to.stop()

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
        self.show()

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
    parser = argparse.ArgumentParser(description="qosd - "+DESCRIPTION+" - v"+VERSION, epilog=EXAMPLES, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--no-input', action='store_true', help='set window transparent to input')
    parser.add_argument('-m', '--maxlines', type=int, default=Qosd.MAXLINES, help='default: %s' % Qosd.MAXLINES)
    parser.add_argument('-n', '--session-name', help='start named OSD display session, killing previous OSD with same session name')
    parser.add_argument('-o', '--opacity', type=float, default=Qosd_win.OPACITY, help='default: %s' % Qosd_win.OPACITY)
    parser.add_argument('-p', '--position', default=Qosd_win.POSITION, choices=["topleft", "topright", "bottomleft", "bottomright"], help='text position, default=%s' % Qosd_win.POSITION)
    parser.add_argument('-P', '--position-offset', type=int, nargs=2, default=(0,0), help='offset in pixels from position, default: 0 0')
    parser.add_argument('-s', '--style', default=Qosd_win.STYLE, help='default: \'%s\'' % Qosd_win.STYLE)
    parser.add_argument('-t', '--timeout', type=float, default=Qosd.TIMEOUT, help='display timeout in seconds, default: %s' % Qosd.TIMEOUT)
    parser.add_argument('text', nargs="+", help='text to display, or \'-\' for stdin')

    args = parser.parse_args()

    # use OS signal handler for SIGINT, to exit on ctrl-c while in Qt loop
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    if args.session_name:
        Qosd.setup_session(args.session_name)

    osd = Qosd(args.style, args.opacity, args.timeout, args.maxlines, args.position, args.position_offset, args.no_input)
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

